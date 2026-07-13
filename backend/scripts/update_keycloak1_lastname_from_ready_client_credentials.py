#!/usr/bin/env python3
"""
Atualiza usuários do Keycloak 1 usando o arquivo ready-only da pré-migração.

Autenticação suportada:
1) Client Credentials: --client-id + --client-secret ou --client-secret-env
2) Password Grant: --client-id + --admin-username + --admin-password

Regra de segurança:
- Só atualiza usuários cujo username atual no Keycloak contém '@'.
- Busca o usuário atual no Keycloak por ID antes de atualizar.
- Confere se o email atual do Keycloak bate com o email do arquivo.
- Altera apenas lastName, usando o lastName/documentNumber vindo do arquivo.
- Por padrão roda em DRY-RUN. Para aplicar de verdade, use --apply.

Exemplo client credentials, dry-run:
python update_keycloak1_lastname_from_ready_client_credentials.py \
  --base-url https://keycloak.exemplo.com \
  --realm meu-realm \
  --input keycloak-pre-migration-v2-ready-only.json \
  --auth-realm master \
  --client-id keycloak-migration-admin \
  --client-secret 'SEU_CLIENT_SECRET' \
  --output-report keycloak-update-dry-run.csv

Exemplo client credentials, aplicando:
python update_keycloak1_lastname_from_ready_client_credentials.py \
  --base-url https://keycloak.exemplo.com \
  --realm meu-realm \
  --input keycloak-pre-migration-v2-ready-only.json \
  --auth-realm master \
  --client-id keycloak-migration-admin \
  --client-secret 'SEU_CLIENT_SECRET' \
  --output-report keycloak-update-applied.csv \
  --apply
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print("Erro: instale a dependência com: pip install requests", file=sys.stderr)
    sys.exit(1)


def normalize_email(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def trim_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def resolve_client_secret(args: argparse.Namespace) -> Optional[str]:
    if args.client_secret:
        return args.client_secret
    if args.client_secret_env:
        secret = os.getenv(args.client_secret_env)
        if not secret:
            raise ValueError(f"Variável de ambiente {args.client_secret_env} não encontrada ou vazia.")
        return secret
    return None


def get_token(
    base_url: str,
    auth_realm: str,
    client_id: str,
    admin_username: Optional[str],
    admin_password: Optional[str],
    client_secret: Optional[str],
    timeout: int,
) -> str:
    token_url = f"{trim_base_url(base_url)}/realms/{auth_realm}/protocol/openid-connect/token"

    if client_secret:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    else:
        if not admin_username or not admin_password:
            raise ValueError(
                "Informe --client-secret/--client-secret-env para client_credentials "
                "ou --admin-username e --admin-password para password grant."
            )
        data = {
            "grant_type": "password",
            "client_id": client_id,
            "username": admin_username,
            "password": admin_password,
        }

    response = requests.post(token_url, data=data, timeout=timeout)
    if response.status_code != 200:
        raise RuntimeError(f"Falha ao obter token: HTTP {response.status_code} - {response.text[:800]}")

    payload = response.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError("Resposta do token não contém access_token.")
    return token


def request_with_refresh(
    method: str,
    url: str,
    token_state: Dict[str, str],
    token_args: Dict[str, Any],
    timeout: int,
    **kwargs: Any,
) -> requests.Response:
    headers = kwargs.pop("headers", {}) or {}
    headers["Authorization"] = f"Bearer {token_state['token']}"
    headers.setdefault("Accept", "application/json")

    response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    if response.status_code == 401:
        token_state["token"] = get_token(**token_args)
        headers["Authorization"] = f"Bearer {token_state['token']}"
        response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    return response


def load_users(input_path: Path) -> List[Dict[str, Any]]:
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("O arquivo de entrada precisa ser uma lista JSON de usuários.")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Atualiza lastName no Keycloak 1 a partir do arquivo ready-only. Suporta client_id/client_secret."
    )
    parser.add_argument("--base-url", required=True, help="URL base do Keycloak. Ex: https://host ou https://host/auth em versões antigas.")
    parser.add_argument("--realm", required=True, help="Realm onde os usuários serão atualizados.")
    parser.add_argument("--input", required=True, help="Arquivo JSON ready-only gerado na pré-migração.")
    parser.add_argument("--output-report", default="keycloak-update-report.csv", help="CSV de resultado da execução.")
    parser.add_argument("--auth-realm", default="master", help="Realm usado para autenticar o client/admin. Padrão: master.")
    parser.add_argument("--client-id", required=True, help="Client ID para autenticação.")
    parser.add_argument("--client-secret", help="Client secret. Se informado, usa grant_type=client_credentials.")
    parser.add_argument("--client-secret-env", help="Nome da variável de ambiente que contém o client secret.")
    parser.add_argument("--admin-username", help="Usuário admin. Usado apenas no grant password.")
    parser.add_argument("--admin-password", help="Senha admin. Usado apenas no grant password.")
    parser.add_argument("--apply", action="store_true", help="Aplica as alterações. Sem isso, roda em dry-run.")
    parser.add_argument("--set-attribute", action="store_true", help="Também salva attributes.documentNumber=[lastName].")
    parser.add_argument("--sleep", type=float, default=0.0, help="Pausa em segundos entre updates. Ex: 0.1")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout HTTP em segundos. Padrão: 30")
    args = parser.parse_args()

    client_secret = resolve_client_secret(args)

    input_path = Path(args.input)
    users = load_users(input_path)

    token_args = {
        "base_url": args.base_url,
        "auth_realm": args.auth_realm,
        "client_id": args.client_id,
        "admin_username": args.admin_username,
        "admin_password": args.admin_password,
        "client_secret": client_secret,
        "timeout": args.timeout,
    }
    token_state = {"token": get_token(**token_args)}

    base_admin_url = f"{trim_base_url(args.base_url)}/admin/realms/{args.realm}"
    rows: List[Dict[str, Any]] = []

    print(f"Modo: {'APLICANDO ALTERAÇÕES' if args.apply else 'DRY-RUN'}")
    print(f"Autenticação: {'client_credentials' if client_secret else 'password grant'}")
    print(f"Usuários no arquivo: {len(users)}")

    for index, candidate in enumerate(users, start=1):
        user_id = candidate.get("id")
        target_last_name = candidate.get("lastName")
        input_username = candidate.get("username")
        input_email = candidate.get("email")

        row = {
            "index": index,
            "id": user_id,
            "inputUsername": input_username,
            "inputEmail": input_email,
            "targetLastName": target_last_name,
            "currentUsername": "",
            "currentEmail": "",
            "oldLastName": "",
            "newLastName": target_last_name or "",
            "status": "",
            "message": "",
        }

        try:
            if not user_id:
                row.update(status="SKIPPED", message="Usuário sem id no arquivo.")
                rows.append(row)
                continue

            if not target_last_name:
                row.update(status="SKIPPED", message="Usuário sem lastName/documentNumber no arquivo.")
                rows.append(row)
                continue

            get_url = f"{base_admin_url}/users/{user_id}"
            get_response = request_with_refresh("GET", get_url, token_state, token_args, args.timeout)

            if get_response.status_code == 404:
                row.update(status="NOT_FOUND", message="Usuário não encontrado no Keycloak.")
                rows.append(row)
                continue

            if get_response.status_code != 200:
                row.update(status="ERROR", message=f"GET HTTP {get_response.status_code}: {get_response.text[:500]}")
                rows.append(row)
                continue

            current_user = get_response.json()
            current_username = current_user.get("username")
            current_email = current_user.get("email")
            old_last_name = current_user.get("lastName")
            row["currentUsername"] = current_username
            row["currentEmail"] = current_email
            row["oldLastName"] = old_last_name or ""

            # Proteção principal: se o username atual não é email, não tocar.
            if "@" not in (current_username or ""):
                row.update(status="SKIPPED", message="Username atual não é email; usuário preservado intocado.")
                rows.append(row)
                continue

            # Proteção adicional: o email atual precisa bater com o email usado na pré-migração.
            if normalize_email(current_email) != normalize_email(input_email):
                row.update(status="SKIPPED", message="Email atual no Keycloak difere do email do arquivo.")
                rows.append(row)
                continue

            if old_last_name == target_last_name:
                row.update(status="UNCHANGED", message="lastName já está com o valor esperado.")
                rows.append(row)
                continue

            # Atualiza a representação atual completa para evitar comportamento de patch parcial.
            current_user["lastName"] = target_last_name

            if args.set_attribute:
                attrs = current_user.get("attributes") or {}
                if not isinstance(attrs, dict):
                    attrs = {}
                attrs["documentNumber"] = [str(target_last_name)]
                current_user["attributes"] = attrs

            if not args.apply:
                row.update(status="DRY_RUN", message="Alteração validada, mas não aplicada.")
                rows.append(row)
                continue

            put_response = request_with_refresh(
                "PUT",
                get_url,
                token_state,
                token_args,
                args.timeout,
                json=current_user,
                headers={"Content-Type": "application/json"},
            )

            if put_response.status_code == 204:
                row.update(status="UPDATED", message="lastName atualizado com sucesso.")
            else:
                row.update(status="ERROR", message=f"PUT HTTP {put_response.status_code}: {put_response.text[:500]}")

            rows.append(row)

            if args.sleep > 0:
                time.sleep(args.sleep)

        except Exception as exc:
            row.update(status="ERROR", message=str(exc))
            rows.append(row)

    output_path = Path(args.output_report)
    fieldnames = list(rows[0].keys()) if rows else ["status"]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    print("\nResumo:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")
    print(f"\nRelatório gerado em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
