# MongoDB Exploration API Testing Guide

Todos os endpoints estão funcionando e testados. Use os comandos abaixo para testar manualmente.

## Endpoints Disponíveis

### 1. Validar Conexão
Testa se a conexão com MongoDB é válida.

```bash
curl -X POST http://127.0.0.1:8000/api/explore/validate \
  -H "Content-Type: application/json" \
  -d '{
    "connectionString": "mongodb://localhost:27017",
    "database": "omnichannel",
    "collection": "attendances"
  }'
```

**Resposta:**
```json
{
  "connected": true
}
```

---

### 2. Listar Bancos de Dados
Lista todos os bancos de dados disponíveis.

```bash
curl -X POST http://127.0.0.1:8000/api/explore/databases \
  -H "Content-Type: application/json" \
  -d '{
    "connectionString": "mongodb://localhost:27017",
    "database": "test",
    "collection": "test"
  }'
```

**Resposta:**
```json
{
  "databases": [
    "admin",
    "config",
    "local",
    "omnichannel",
    "sa-appconfigs",
    ...
  ]
}
```

---

### 3. Listar Collections
Lista todas as collections de um banco de dados.

```bash
curl -X POST http://127.0.0.1:8000/api/explore/collections \
  -H "Content-Type: application/json" \
  -d '{
    "connectionString": "mongodb://localhost:27017",
    "database": "omnichannel",
    "collection": "test"
  }'
```

**Resposta:**
```json
{
  "collections": [
    "predefined_messages",
    "attendances",
    "attendances_messages",
    "contacts",
    "admin_credentials",
    "current_conversations",
    "rest_poll_configuration",
    "instances"
  ]
}
```

---

### 4. Obter Amostras de Documentos
Retorna os primeiros 10 documentos de uma collection (padrão).

```bash
curl -X POST http://127.0.0.1:8000/api/explore/sample \
  -H "Content-Type: application/json" \
  -d '{
    "connectionString": "mongodb://localhost:27017",
    "database": "omnichannel",
    "collection": "attendances"
  }'
```

**Resposta:**
```json
{
  "items": [
    {
      "_id": "2c5520e7-f371-4534-ac36-246a87191195",
      "instanceId": "sansysJtech",
      "customer": "Sidney Victor",
      "platformId": "5582993336500",
      "platform": "WhatsappBusiness",
      "contactId": "655374038b26f34d950aaa5b",
      ...
    }
  ]
}
```

## Tratamento de Tipos BSON

Todos os tipos especiais do MongoDB são convertidos automaticamente:

- **ObjectId** → String (e.g., `"2c5520e7-f371-4534-ac36-246a87191195"`)
- **DBRef** → JSON object com campos `$ref`, `$id`, `$db`
- **Binary Data** → String (UTF-8 decoded)
- **Nested Objects/Arrays** → Recursivamente serializados

## Status de Implementação

✅ Validação de Conexão  
✅ Listagem de Bancos de Dados  
✅ Listagem de Collections  
✅ Obtenção de Amostras de Documentos  
✅ Serialização BSON para JSON  

## Próximos Passos

- [ ] Adicionar filtros personalizados no endpoint `/sample`
- [ ] Adicionar paginação no endpoint `/sample`
- [ ] Implementar busca por campo específico
- [ ] Adicionar agregações customizadas
