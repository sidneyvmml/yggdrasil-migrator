---
name: C.O.M.M.I.T
description: "Use para validar e padronizar mensagens de commit conforme o padrão obrigatório do projeto, com base no nome da branch atual."
---

# SKILL: C.O.M.M.I.T

Commit Oriented Message Management & Integrity Tool.

## Objetivo

Garantir que TODA mensagem de commit siga o padrão obrigatório do projeto:

[branch-name] descrição clara e objetiva

E garantir padrão único de branch no formato:

dev-<numero_task_easyredmine>

## Modo de operação

Sempre:

1. Solicitar o número da task no EasyRedmine.
2. Montar ou validar o nome da branch no padrão `dev-<numero_task_easyredmine>`.
3. Solicitar ou identificar o nome da branch atual.
4. Se a branch atual não seguir o padrão, sugerir correção para `dev-<numero_task_easyredmine>`.
5. Validar o padrão da mensagem de commit.
6. Corrigir automaticamente caso esteja fora do padrão.
7. Sugerir uma versão otimizada da mensagem.
8. Aplicar boas práticas de clareza, rastreabilidade e granularidade.

Pergunta obrigatória inicial:
"Qual o número da task no EasyRedmine?"

Com esse número, o nome da branch deve ser composto com prefixo obrigatório `dev-`.

Exemplo:
- Task EasyRedmine: `83400`
- Branch obrigatória: `dev-83400`

Fluxo mínimo obrigatório:

1. Perguntar o número da task no EasyRedmine.
2. Construir branch esperada como `dev-<numero>`.
3. Validar se a branch atual corresponde à branch esperada.
4. Só então validar/padronizar a mensagem de commit.

## Regras obrigatórias

- Toda mensagem de commit deve começar com o prefixo da branch entre colchetes: `[branch-name]`.
- O nome da branch deve obrigatoriamente começar com `dev-`.
- O nome da branch deve obrigatoriamente ser `dev-<numero_task_easyredmine>`.
- O corpo da mensagem deve ser técnico, claro e no presente.
- Nunca permitir uso de prefixos como `feat:`, `fix:`, `chore:`, `refactor:`.
- Mensagens genéricas como `ajustes`, `update`, `correções`, `mudanças` são proibidas.

## Padrão de escrita

- Sempre em português técnico e claro.
- Verbos no presente:
  - Adiciona
  - Corrige
  - Remove
  - Refatora
  - Ajusta
  - Melhora

## Saída esperada

Deve retornar:

1. ✅ Commit corrigido e padronizado
2. 🔍 Versão melhorada (mais profissional)
3. ⚠️ Erros encontrados (se houver)
4. 💡 Sugestões de melhoria (opcional)

## Comportamento inteligente

- Sempre perguntar primeiro:
  "Qual o número da task no EasyRedmine?"
- Se a branch não for informada, perguntar:
  "Qual o nome da branch atual? (padrão obrigatório: dev-<numero_task>)"
- Se a branch não começar com `dev-`, corrigir automaticamente para `dev-<numero_task_easyredmine>`.
- Se a mensagem for vaga, melhorar automaticamente.
- Se a mensagem estiver fora do padrão, corrigir automaticamente.
- Se a mensagem já estiver correta, otimizar para maior clareza e profissionalismo.

## Formato completo (quando necessário)

Se o contexto justificar, expandir para:

[branch] Descrição curta

- Arquivo/Classe: alteração realizada
- Arquivo/Classe: alteração realizada

Motivo: explicação técnica
Impacto: resultado da mudança

## Checklist interno

Sempre validar:

- O prefixo corresponde à branch?
- A mensagem está clara?
- O verbo está no presente?
- Existe ambiguidade?
- Está técnico o suficiente?

Se algo falhar → corrigir automaticamente.

## Integração com D.E.L.I.V.E.R

Esta skill atua principalmente nas etapas:

- L (Layer Checks) → valida padrão
- V (Validate) → melhora qualidade
- R (Release) → garante histórico limpo

## Exemplo de uso

INPUT:
"ajustes no sistema"

OUTPUT:
[dev-1234] Ajusta regras de validação no sistema

INPUT:
"fix bug nullpointer"

OUTPUT:
[dev-4567] Corrige NullPointerException em faturamento
