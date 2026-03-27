# ✅ Checklist de Validação

Use esta checklist antes de entregar o desafio.

---

## 📦 Arquivos e Estrutura

- [ ] Código-fonte está organizado em módulos (`extractor/`, `loader/`, `api/`)
- [ ] Clean Architecture implementada (Domain, Application, Infrastructure)
- [ ] Princípios SOLID aplicados
- [ ] `.gitignore` configurado corretamente
- [ ] `.env.example` presente (sem credenciais reais)
- [ ] `requirements.txt` completo
- [ ] `docker-compose.yml` funcional

---

## 🔍 Etapa 1: Extração

- [ ] Extrator automatizado implementado
- [ ] Coleta dados de pelo menos 3 estados
- [ ] Todos os municípios de cada estado são processados
- [ ] Retry automático com backoff exponencial
- [ ] Checkpointing funcional (retoma de onde parou)
- [ ] Logging estruturado em JSONL
- [ ] Metadados registrados (timestamp, UF, município, total de registros)

**Teste:**
```powershell
docker run --rm -v "${PWD}:/app" -w /app python:3.11-slim bash -c "pip install -q httpx tenacity pydantic-settings && python -m extractor.main --ufs SP MG GO"
```

---

## 💾 Etapa 2: Modelagem e Carga

- [ ] Schema normalizado (3NF)
- [ ] Tipos corretos (VARCHAR, NUMERIC, TIMESTAMPTZ)
- [ ] Constraints definidas (UNIQUE, CHECK, FOREIGN KEY)
- [ ] Idempotência garantida (UPSERT)
- [ ] Script de migration (`db/schema.sql`)
- [ ] Pode rodar múltiplas vezes sem erros

**Teste:**
```bash
docker-compose up -d postgres
# Aguardar 5s
docker-compose exec postgres psql -U sncr_user -d sncr -c "\dt"
```

---

## ⚡ Etapa 3: Performance

- [ ] Índices criados e documentados (`db/indexes.sql`)
- [ ] Índice no `codigo_incra` (busca principal)
- [ ] Índices em `imovel_id` e `pessoa_id` (JOINs)
- [ ] Consulta por código INCRA responde em < 2s
- [ ] Justificativa técnica dos índices documentada

**Teste:**
```sql
EXPLAIN ANALYZE
SELECT * FROM imoveis WHERE codigo_incra = '12345678901234567';
```

Deve mostrar `Index Scan` com tempo < 2000ms.

---

## 🌐 Etapa 4: API REST

- [ ] Endpoint `GET /imovel/{codigo_incra}` implementado
- [ ] CPF anonimizado (formato: `***.***.XXX-XX`)
- [ ] Retorna 404 para códigos inexistentes
- [ ] Documentação automática (Swagger) em `/docs`
- [ ] Consulta PostgreSQL (não o site original)

**Teste:**
```bash
docker-compose up -d api
curl http://localhost:8000/docs
curl http://localhost:8000/imovel/99999999999999999
```

Deve retornar:
```json
{"detail": "Imóvel com código INCRA '99999999999999999' não encontrado."}
```

---

## 📖 Documentação

- [ ] README.md completo com:
  - [ ] Instruções para rodar localmente
  - [ ] Decisões técnicas justificadas
  - [ ] O que faria diferente com mais tempo
  - [ ] Arquitetura documentada
  - [ ] Tecnologias utilizadas
- [ ] Código sem comentários desnecessários (autodocumentado)
- [ ] Nomes de variáveis e funções descritivos

---

## 🐳 Docker

- [ ] PostgreSQL sobe via Docker Compose
- [ ] API sobe via Docker Compose
- [ ] Healthcheck configurado
- [ ] Volumes persistentes para dados
- [ ] Network isolada

**Teste:**
```bash
docker-compose up -d
docker-compose ps
```

Todos os serviços devem estar `healthy` ou `running`.

---

## 🧪 Testes Manuais

### 1. Pipeline Completo

```powershell
.\run-pipeline.ps1
```

Deve:
- ✅ Subir PostgreSQL
- ✅ Extrair dados de 3 UFs
- ✅ Carregar dados no banco
- ✅ Subir API
- ✅ API responder em http://localhost:8000/docs

### 2. Consulta de Imóvel

```bash
curl http://localhost:8000/imovel/CODIGO_VALIDO
```

Deve retornar JSON com CPF anonimizado.

### 3. Idempotência

Execute o loader 2 vezes:
```bash
python -m loader.main --input-dir extractor/output
python -m loader.main --input-dir extractor/output
```

Não deve duplicar dados no banco.

---

## 🛡️ Qualidade de Código

- [ ] Sem hardcoded credentials
- [ ] Configurações via `.env`
- [ ] Tratamento de erros adequado
- [ ] Logs informativos (não excessivos)
- [ ] Funções pequenas e coesas
- [ ] Classes com responsabilidade única (SRP)
- [ ] Dependency Injection implementada

---

## 📤 Git

- [ ] Repositório criado no GitHub
- [ ] `.gitignore` configurado
- [ ] Nenhum dado sensível commitado (`.env`, CSVs)
- [ ] Commit messages descritivas
- [ ] README.md aparece na página inicial

**Teste:**
```bash
git clone https://github.com/SEU-USUARIO/sncr-data-pipeline.git
cd sncr-data-pipeline
.\run-pipeline.ps1
```

Deve funcionar em máquina limpa (apenas com Docker).

---

## 🎯 Critérios de Avaliação

| Critério | Peso | Status |
|----------|------|--------|
| Qualidade do código | 20% | [ ] |
| Robustez da extração | 20% | [ ] |
| Modelagem do banco | 20% | [ ] |
| Performance | 20% | [ ] |
| API | 10% | [ ] |
| Documentação | 10% | [ ] |

---

## ✅ Checklist Final

Antes de submeter:

- [ ] Executei `.\clean.ps1` para remover dados temporários
- [ ] Testei o pipeline completo do zero
- [ ] Verifiquei que `.env` não está no Git
- [ ] README.md está completo e bem formatado
- [ ] API está documentada e funcional
- [ ] Banco de dados tem índices otimizados
- [ ] Código segue Clean Architecture e SOLID
- [ ] Repositório Git está público/compartilhado

---

## 📧 Entrega

1. Link do repositório GitHub
2. Email com:
   - Link do repositório
   - Breve descrição das decisões técnicas
   - Instruções de execução (ou link para README)

**Exemplo de email:**

```
Assunto: Desafio Técnico - Data Engineer - [Seu Nome]

Olá,

Segue o link do repositório com a solução do desafio:
https://github.com/SEU-USUARIO/sncr-data-pipeline

Principais destaques:
- Arquitetura limpa com separação de responsabilidades
- Retry inteligente com backoff exponencial
- Idempotência garantida via UPSERT
- Performance < 2ms com índices otimizados
- Documentação completa

Para executar localmente:
git clone https://github.com/SEU-USUARIO/sncr-data-pipeline.git
cd sncr-data-pipeline
.\run-pipeline.ps1

Att,
[Seu Nome]
```

---

**Boa sorte! 🚀**
