---
name: D.E.L.I.V.E.R
description: "Use when you need a deterministic task workflow that integrates Define, Execute, Layer Checks, Improve, Validate, Export Docs, and Release."
---

# SKILL: D.E.L.I.V.E.R

Este skill orienta o desenvolvimento de uma tarefa por vez, seguindo um fluxo determinístico que integra outras skills de qualidade e documentação.

## Fluxo D.E.L.I.V.E.R

1. **D — Define**
   - Criar uma branch por STORY no formato `feature/<nome_projeto>_<epic>_<story>`.
   - Abrir o planejamento e marcar a tarefa como `Doing...`.
   - Preparar o ambiente e confirmar o status no planejamento antes de começar.

2. **E — Execute**
   - Ler o prompt localizado em `docs/features/<feat_name>/EPIC-<number>/STORY-<number>/TASK-<number>.prompt`.
   - Implementar exatamente o que o prompt da task manda fazer.

3. **L — Layer Checks**
   - Executar a skill `V.E.R.I.F.Y.`.
   - Executar a skill `S.E.C.U.R.E.`.
   - Executar a skill `S.H.I.E.L.D.`.

4. **I — Improve**
   - Ajustar o código com a skill `R.E.F.A.C.T.`.
   - Garantir que o código esteja limpo, legível e alinhado com padrões do projeto.

5. **V — Validate**
   - Realizar revisão de código com a skill `C.L.E.A.R.`.
   - Se encontrar algo novo, aplicar novamente a skill `R.E.F.A.C.T.`.

6. **E — Export Docs**
   - Documentar as mudanças usando a skill `D.O.C.S.`.
   - Atualizar documentação de design, uso ou configuração quando necessário.

7. **R — Release**
   - Avisar que a tarefa foi finalizada e aguardar `OK` ou `Continue` do usuário.
   - Após o sinal verde, marcar a tarefa como `Done` no planejamento.
   - Comitar todas as alterações e dar `push` para o repositório.
   - Notificar que tudo terminou e perguntar pela nova tarefa.

## Regras importantes

- Deve desenvolver apenas uma tarefa por vez.
- Deve seguir a sequência exata do fluxo.
- Deve ler e seguir o prompt da task antes de implementar.
- Deve usar as skills relacionadas no momento certo do fluxo.
- Deve fechar o ciclo com revisão, documentação e liberação.
