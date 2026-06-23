# Template — Documentação de Implementação

Copiar estrutura **literalmente**. Substituir placeholders `{...}`. Não adicionar seções.

---

**Projeto/Branch:** {nome-projeto} / {branch}  
**Banco de Dados:** {ambiente} ({engine} — {coleções ou tabelas})  
**Implementação solicitada:** {parágrafo único — funcionalidade + chave de negócio + consumo no fluxo}

**Desenvolvimento realizado:**

**Commit `{sha-curto}` — {serviço} ({DD/MM/YYYY})**
- {bullet técnico 1}
- {bullet técnico 2}
- {bullet técnico N}

{repetir bloco para cada commit}

**Orientação de testes:**

1. **{Contexto} — {ação principal}**
   - `{MÉTODO} {path}` com {headers/body relevantes}.
   - Esperado: **{HTTP}** com {descrição}.
   - Cenários de erro: **{HTTP}** {condição}; ...

2. **{Próximo cenário}**
   - ...

{N. **Regressão automatizada**}
   - `./gradlew :{modulo}:test --tests "*{ClasseRelevante}*"`
   - Validar integração {serviço A} ↔ {serviço B} após deploy.

**Informações auxiliares:**

| Item | Detalhe |
|------|---------|
| **Demanda** | {dev-XXXXX} |
| **Commits** | `{sha-completo-1}`, `{sha-completo-2}`, ... |
| **Autor** | {nome do git log} |
| **Data** | {DD/MM/YYYY} – {DD/MM/YYYY} |
| **Serviços** | `{serviço-1}`, `{serviço-2}`, ... |
| **Escopo** | ~{N} arquivos, +{ins} / −{del} linhas (intervalo `{primeiro}`..`{ultimo}`) |
| **Branch remota** | `origin/{branch}` |
| **Migração DB** | {campo/script ou "sem migração"} |

**Evidências da implementação:**

| Evidência | Referência |
|-----------|------------|
| {o quê prova} | `{endpoint ou classe}` — `{Arquivo.java}` |
| ... | ... |
| Histórico Git | `git show {sha-curto-1}` … `git show {sha-curto-N}` na branch `{branch}` |

**Exemplo de payload — {descrição do cenário principal}:**

```
{MÉTODO} {path}
{headers opcionais}

{
  "campo": "valor"
}
```

**Resposta esperada ({HTTP}):** {descrição ou JSON resumido}

**Exemplo {contexto secundário} — {descrição}:**

```
{MÉTODO} {path}?{query-param}={valor}
...

{
  ...
}
```

**Resposta esperada ({HTTP}):** {descrição}

---

## Exemplo real

Ver: [bffs/sansys-agency-bff-web/docs/IMPLEMENTATION-dev-84626.md](../../../bffs/sansys-agency-bff-web/docs/IMPLEMENTATION-dev-84626.md)
