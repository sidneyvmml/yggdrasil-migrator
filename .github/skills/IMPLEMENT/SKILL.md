---
name: I.M.P.L.E.M.E.N.T.
description: "Gera documentação de implementação a partir de commits Git no padrão IMPLEMENTATION-{demanda}.md. Use quando o usuário solicitar documentação de implementação, doc de entrega, evidências de commits ou informar SHAs de commits para documentar."
---

# SKILL: I.M.P.L.E.M.E.N.T.

Gera documentação técnica de entrega **exatamente** no padrão estrutural de [bffs/sansys-agency-bff-web/docs/IMPLEMENTATION-dev-84626.md](../../../bffs/sansys-agency-bff-web/docs/IMPLEMENTATION-dev-84626.md).

Referência de template: [TEMPLATE.md](TEMPLATE.md)

## Quando usar

- Usuário pede documentação de implementação / entrega / evidências de PR
- Usuário informa lista de commits (SHA curto ou completo)
- Usuário referencia o padrão Payment Route ou `IMPLEMENTATION-dev-*`

## Entradas obrigatórias

Coletar do usuário ou inferir do repositório:

| Entrada | Origem |
|---------|--------|
| **Demanda** | Task EasyRedmine (ex.: `dev-84626`) |
| **Commits** | Lista de SHAs informada pelo usuário |
| **Branch** | `git branch --show-current` ou informada |
| **Projeto** | Nome do repositório/módulo principal |

Opcionais (perguntar se não inferível):

- **Banco de Dados** (ambiente, engine, coleções/tabelas)
- **Implementação solicitada** (1 parágrafo — objetivo de negócio)
- **Caminho de saída** (padrão abaixo)

## Fluxo de execução

### 1. Validar commits

```bash
git rev-parse --verify <sha>^{commit}
git log -1 --format="%H|%an|%ad|%s" --date=format:"%d/%m/%Y" <sha>
git show --stat --format="" <sha>
git diff-tree --no-commit-id --name-only -r <sha> | head -40
```

Para escopo total:

```bash
git diff --shortstat <primeiro-sha>^..<ultimo-sha>
```

Identificar **serviço/módulo** de cada commit pelo caminho dos arquivos (`bffs/`, `services/`, `libs/`).

### 2. Analisar cada commit

Por commit, extrair:

- SHA curto (8 chars) para título do bloco; SHA completo para tabela auxiliar
- Serviço afetado (ex.: `sansys-agency-bff-web`)
- Data `(DD/MM/YYYY)`
- Bullets técnicos objetivos (3–8): endpoints, classes, campos, eventos, testes, migrações

**Não inventar** alterações — basear-se em `git show`, nomes de arquivos e diff.

### 3. Montar o documento

Seguir **ordem e títulos exatos** do template. Ver [TEMPLATE.md](TEMPLATE.md).

Regras estruturais **obrigatórias**:

- **Sem** título H1 (`# ...`) no início
- **Sem** seções extras (`O que foi entregue`, `Contrato principal`, copyright, `---` decorativos)
- Commits em ordem cronológica
- Formato de commit: `**Commit \`<sha-curto>\` — <serviço> (DD/MM/YYYY)**`
- Bullets com `-` (não numerados dentro do bloco de commit)
- **Orientação de testes** numerada (`1.`, `2.`, …) com sub-bullets, `Esperado:` e cenários de erro HTTP quando aplicável
- Tabelas markdown para **Informações auxiliares** e **Evidências**
- Exemplos de payload em blocos ``` (sem linguagem), com **Resposta esperada (HTTP):**

### 4. Preencher seções derivadas

| Seção | Como preencher |
|-------|----------------|
| **Projeto/Branch** | `{repo} / {branch}` |
| **Banco de Dados** | MongoDB/coleções ou SQL inferidos dos entities/migrations tocados |
| **Implementação solicitada** | Parágrafo único: o quê + chave de negócio + consumo no fluxo |
| **Informações auxiliares** | Demanda, SHAs completos, autor (git), intervalo de datas, serviços únicos, escopo (`~N arquivos, +X / −Y`), branch remota, migração DB |
| **Evidências** | Endpoints, classes, use cases, OpenAPI, scripts de migração, `git show` |
| **Exemplos de payload** | Request/response reais do OpenAPI ou controllers alterados |

### 5. Salvar arquivo

Caminho padrão (ajustar ao módulo principal da entrega):

```
{modulo}/docs/IMPLEMENTATION-{demanda}.md
```

Exemplos:

- `bffs/sansys-agency-bff-web/docs/IMPLEMENTATION-dev-84626.md`
- `services/sansys-agency-software/docs/IMPLEMENTATION-dev-12345.md`

Se o usuário indicar outro caminho, usar o informado.

### 6. Validar antes de entregar

Checklist:

- [ ] Estrutura idêntica ao [TEMPLATE.md](TEMPLATE.md) e ao exemplo dev-84626
- [ ] Todos os commits informados estão documentados
- [ ] Bullets refletem o diff real (não genéricos)
- [ ] Documento conciso (ideal: 120–200 linhas; evitar prolixidade)
- [ ] Português técnico, verbos no presente
- [ ] SHAs completos na tabela **Commits**

## Integração com outras skills

- **D.O.C.S.**: esta skill cobre documentação de **entrega por commits**; D.O.C.S. cobre decisões e contexto operacional geral
- **D.E.L.I.V.E.R.**: etapa **E — Export Docs** pode invocar I.M.P.L.E.M.E.N.T. ao finalizar a task
- **C.L.E.A.R.**: revisar documento gerado antes de anexar ao PR

## Anti-padrões (proibido)

- Adicionar H1 ou índice
- Duplicar commits em tabela separada além de **Informações auxiliares**
- Descrever commits sem executar `git show`
- Omitir **Orientação de testes** ou **Evidências**
- Gerar documento genérico sem analisar os SHAs informados
