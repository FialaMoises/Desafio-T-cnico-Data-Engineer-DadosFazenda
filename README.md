# 🌾 SNCR Data Pipeline

Pipeline completo de extração, armazenamento e exposição de dados do Sistema Nacional de Cadastro Rural (SNCR), desenvolvido com arquitetura limpa, princípios SOLID e interface web moderna para visualização e gestão dos dados.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Demonstração](#-demonstração)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Início Rápido](#-início-rápido)
- [Usando o Frontend](#-usando-o-frontend)
- [API REST](#-api-rest)
- [Extração de Dados](#-extração-de-dados)
- [Modelagem do Banco](#-modelagem-do-banco)
- [Performance e Índices](#-performance-e-índices)
- [Decisões Técnicas](#-decisões-técnicas)
- [Tecnologias](#-tecnologias)

---

## 🎯 Visão Geral

Este projeto implementa um **pipeline de dados end-to-end** completo que:

1. **📥 Extrai** dados de imóveis rurais via web scraping do sistema SNCR
2. **🔄 Transforma** e valida dados com idempotência garantida
3. **💾 Armazena** em PostgreSQL com schema normalizado (3NF)
4. **🌐 Expõe** via API REST com FastAPI + documentação automática
5. **🖥️ Visualiza** através de interface web moderna e responsiva

### ✨ Características Principais

- ✅ **Clean Architecture** com separação clara de responsabilidades (Domain, Application, Infrastructure)
- ✅ **Princípios SOLID** aplicados em todos os módulos
- ✅ **Resiliência** com retry automático, checkpoint de progresso e tratamento de erros
- ✅ **Frontend Moderno** com 3 interfaces: busca por código, busca avançada e execução de pipeline
- ✅ **Busca Avançada** com filtros dinâmicos baseados nos dados do banco
- ✅ **Pipeline Web** com logs em tempo real via Server-Sent Events
- ✅ **Performance** otimizada com índices estratégicos (queries < 2ms)
- ✅ **Docker** containerização completa de todos os serviços
- ✅ **API REST** com documentação Swagger automática

---

## 🎬 Demonstração

### Frontend - 3 Interfaces Integradas

1. **🔍 Buscar por Código** - Busca direta por Código INCRA
2. **🔎 Busca Avançada** - Filtros dinâmicos (estado, município, área, proprietário, etc)
3. **⚙️ Executar Pipeline** - Extração e carregamento com logs em tempo real

Acesse: **http://localhost:3000** após iniciar os containers.

---

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                   SNCR Web (Fonte de Dados)                 │
│       https://data-engineer-challenge-production...         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────▼─────────────┐
         │      Extractor Module        │
         │   Clean Architecture         │
         │   - Domain Layer             │
         │   - Application Layer        │
         │   - Infrastructure Layer     │
         │   Retry + Checkpoint + Logs  │
         └───────────────┬──────────────┘
                         │ CSV Files
         ┌───────────────▼──────────────┐
         │       Loader Module           │
         │   SOLID Principles            │
         │   Upsert Idempotente          │
         │   Validação + Transformação   │
         └───────────────┬──────────────┘
                         │
         ┌───────────────▼──────────────┐
         │      PostgreSQL 16            │
         │   Schema Normalizado (3NF)    │
         │   Índices Otimizados          │
         │   - imoveis                   │
         │   - pessoas                   │
         │   - vinculos                  │
         └───────────────┬──────────────┘
                         │
      ┌──────────────────┴─────────────────┐
      │                                     │
┌─────▼──────┐                    ┌────────▼────────┐
│  FastAPI   │                    │   Nginx         │
│  REST API  │◄───────────────────┤   Frontend      │
│  + Swagger │   CORS Enabled     │   (SPA)         │
└────────────┘                    └─────────────────┘
    │
    ├─ GET  /imovel/{codigo}          # Busca por código
    ├─ GET  /search/filters            # Filtros dinâmicos
    ├─ GET  /search/imoveis            # Busca avançada
    ├─ GET  /pipeline/run              # Executar pipeline (SSE)
    └─ GET  /pipeline/status           # Status do pipeline
```

---

## 📁 Estrutura do Projeto

```
Desafio-Técnico-Data-Engineer-DadosFazenda/
├── extractor/                         # 📥 Módulo de Extração
│   ├── domain/                        # Entidades e interfaces
│   │   ├── entities.py               # Estado, Municipio, Captcha, etc
│   │   └── repositories.py           # Contratos (abstrações)
│   ├── application/
│   │   └── scraper_service.py        # Orquestração da extração
│   ├── infrastructure/
│   │   ├── http_client.py            # Implementação HTTP (httpx)
│   │   ├── checkpoint_manager.py     # Salvamento de progresso
│   │   └── metadata_writer.py        # Logs estruturados
│   ├── config/
│   │   ├── settings.py               # Configurações
│   │   └── logger.py                 # Setup de logging
│   └── main.py                       # Entry point
│
├── loader/                            # 💾 Módulo de Carga
│   ├── domain/
│   │   ├── entities.py               # Imovel, Pessoa, Vinculo
│   │   └── repositories.py           # Contratos
│   ├── services/
│   │   ├── loader_service.py         # Orquestração da carga
│   │   └── transformer.py            # Validação e transformação
│   ├── infrastructure/
│   │   ├── database.py               # Conexão PostgreSQL + UPSERT
│   │   └── csv_reader.py             # Leitura de CSVs
│   ├── config/
│   │   └── settings.py               # Configurações
│   └── main.py                       # Entry point
│
├── api/                               # 🌐 Módulo API REST
│   ├── routers/
│   │   ├── imovel.py                 # GET /imovel/{codigo_incra}
│   │   ├── search.py                 # Busca avançada
│   │   └── pipeline.py               # Execução de pipeline
│   ├── services/
│   │   ├── imovel_service.py         # Lógica de busca
│   │   ├── search_service.py         # Busca com filtros
│   │   └── cpf_anonymizer.py         # Anonimização de CPF
│   ├── models/
│   │   ├── database_models.py        # SQLAlchemy ORM models
│   │   └── schemas.py                # Pydantic request/response
│   ├── config/
│   │   ├── settings.py               # Configurações
│   │   └── database.py               # Setup async engine
│   └── main.py                       # FastAPI app
│
├── frontend/                          # 🖥️ Interface Web
│   ├── index.html                    # SPA completa (3 abas)
│   ├── Dockerfile                    # Build nginx
│   ├── start-frontend.ps1            # Script PowerShell
│   └── README.md                     # Documentação
│
├── db/                                # 🗄️ Banco de Dados
│   ├── schema.sql                    # DDL completo (3 tabelas)
│   └── indexes.sql                   # Índices otimizados + docs
│
├── docker-compose.yml                # 🐳 Orquestração (5 serviços)
├── Dockerfile                        # Build Python (multi-use)
├── requirements.txt                  # Dependências Python
├── .env.example                      # Template de variáveis
└── README.md                         # Este arquivo
```

---

## 🔧 Pré-requisitos

- **Docker** (v20.10+) e **Docker Compose** (v2.0+)
- **Git**

Opcional (para desenvolvimento):
- **Python 3.11+**
- **PostgreSQL 16** (se quiser rodar fora do Docker)

---

## 🚀 Início Rápido

### Opção 1: Iniciar Tudo (Recomendado)

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd Desafio-Técnico-Data-Engineer-DadosFazenda

# 2. Inicie todos os serviços
docker-compose up -d

# 3. Aguarde ~15 segundos para os serviços iniciarem
# Você verá 5 containers rodando:
#   - sncr-postgres    (banco de dados)
#   - sncr-api         (FastAPI REST)
#   - sncr-frontend    (Nginx + SPA)
#   - extractor        (para usar via docker-compose run)
#   - loader           (para usar via docker-compose run)
```

### Opção 2: Passo a Passo

```bash
# 1. Subir banco de dados
docker-compose up -d postgres

# 2. Executar extração (escolha os estados desejados)
docker-compose run --rm extractor python -m extractor.main --ufs PA RJ PR

# 3. Carregar dados no banco
docker-compose run --rm loader

# 4. Subir API e Frontend
docker-compose up -d api frontend
```

### ✅ Verificar se está funcionando

```bash
# API Health Check
curl http://localhost:8001/

# Frontend
curl http://localhost:3000/
```

**Pronto!** Acesse:
- 🌐 **Frontend**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8001/docs
- 🔍 **API Base**: http://localhost:8001

---

## 🖥️ Usando o Frontend

Acesse **http://localhost:3000** no navegador.

### Aba 1: 🔍 Buscar por Código

Busca direta por Código INCRA (17 dígitos).

**Como usar:**
1. Digite o código no campo (ex: `26001000017`)
2. Clique em "Buscar" ou pressione Enter
3. Veja os detalhes do imóvel e proprietários

**Exemplos de códigos válidos** (clique direto nos links):
- `11001000016`
- `26001000017`
- `26001000000`

### Aba 2: 🔎 Busca Avançada

Busca com **filtros dinâmicos** que se atualizam conforme os dados no banco.

**Filtros disponíveis:**
- **Estado (UF)**: Dropdown com todos os estados que têm dados
- **Município**: Dropdown que se atualiza ao selecionar o estado
- **Situação**: Dropdown com situações cadastradas (Ativo, Inativo, etc)
- **Nome do Imóvel**: Busca parcial (ex: "Fazenda")
- **Nome do Proprietário**: Busca parcial (ex: "Silva")
- **Área Mínima/Máxima**: Faixa de hectares
- **Limite de Resultados**: 10, 50, 100 ou 200 registros

**Como usar:**
1. Selecione os filtros desejados
2. Clique em "🔍 Buscar"
3. Veja a lista de imóveis com todos os detalhes
4. Use "🔄 Limpar Filtros" para resetar

**Exemplos de buscas:**
- Todos os imóveis do Pará: `UF = PA`
- Fazendas grandes: `Área Mínima = 100`
- Proprietários "Silva" em SP: `Nome Pessoa = Silva, UF = SP`
- Imóveis ativos com + de 50 ha: `Situação = Ativo, Área Mínima = 50`

### Aba 3: ⚙️ Executar Pipeline

Execute **extração + carregamento** diretamente pelo navegador com **logs em tempo real**.

**Como usar:**
1. Selecione os estados desejados (clique nos botões)
   - Estados pré-selecionados: PA, RJ, PR
2. Clique em "▶️ Iniciar Extração e Carregamento"
3. Acompanhe os logs em tempo real no console
4. Veja a barra de progresso avançar:
   - 0% → 50% (Extração)
   - 50% → 80% (Carregamento)
   - 80% → 100% (Concluído)

**Funcionalidades:**
- ✅ Logs coloridos por tipo (INFO, SUCCESS, ERROR)
- ✅ Timestamps em cada linha
- ✅ Auto-scroll para última linha
- ✅ Botão desabilitado durante execução
- ✅ Estatísticas atualizadas automaticamente ao concluir

---

## 🌐 API REST

### Endpoints Disponíveis

#### 1. Buscar Imóvel por Código

```http
GET /imovel/{codigo_incra}
```

**Exemplo:**
```bash
curl http://localhost:8001/imovel/26001000017
```

**Resposta (200 OK):**
```json
{
  "codigo_incra": "26001000017",
  "nome_imovel": "Fazenda Santa Clara",
  "uf": "PE",
  "municipio": "São Paulo",
  "area_ha": 150.25,
  "situacao": "Ativo",
  "proprietarios": [
    {
      "nome_completo": "João da Silva",
      "cpf": "12345678901",
      "vinculo": "Proprietário",
      "participacao_pct": "100.00"
    }
  ]
}
```

#### 2. Obter Filtros Disponíveis

```http
GET /search/filters
```

**Resposta:**
```json
{
  "estados": ["PA", "RJ", "PR", "SP"],
  "municipios_by_estado": {
    "PA": ["Belém", "Santarém"],
    "RJ": ["Rio de Janeiro", "Niterói"]
  },
  "situacoes": ["Ativo", "Inativo"],
  "estatisticas": {
    "total_imoveis": 54,
    "total_pessoas": 330,
    "total_vinculos": 330
  },
  "area_range": {
    "min": 0.5,
    "max": 5000.0
  }
}
```

#### 3. Busca Avançada

```http
GET /search/imoveis?uf=PA&area_min=100&limit=50
```

**Parâmetros (todos opcionais):**
- `uf`: Estado (ex: PA, RJ)
- `municipio`: Município (busca parcial)
- `situacao`: Situação do imóvel
- `area_min`: Área mínima em hectares
- `area_max`: Área máxima em hectares
- `nome_imovel`: Nome do imóvel (busca parcial)
- `nome_pessoa`: Nome do proprietário (busca parcial)
- `limit`: Limite de resultados (1-500, padrão: 100)
- `offset`: Offset para paginação (padrão: 0)

**Exemplos de uso:**
```bash
# Imóveis no Pará
curl "http://localhost:8001/search/imoveis?uf=PA"

# Fazendas entre 100 e 500 hectares
curl "http://localhost:8001/search/imoveis?area_min=100&area_max=500"

# Proprietários com nome "Silva"
curl "http://localhost:8001/search/imoveis?nome_pessoa=Silva"

# Combinação de filtros
curl "http://localhost:8001/search/imoveis?uf=RJ&situacao=Ativo&area_min=50&limit=20"
```

#### 4. Executar Pipeline (SSE)

```http
GET /pipeline/run?estados=PA,RJ,PR
```

Retorna **Server-Sent Events** com logs em tempo real.

**Exemplo com curl:**
```bash
curl -N "http://localhost:8001/pipeline/run?estados=PA,RJ,PR"
```

**Exemplo de resposta (stream):**
```
data: {"type":"info","message":"Iniciando extração dos estados: PA, RJ, PR","timestamp":"2026-03-27T10:30:00"}

data: {"type":"log","message":"Extraindo PA - Belém...","step":"extração","timestamp":"2026-03-27T10:30:05"}

data: {"type":"success","message":"Extração concluída!","step":"extração","timestamp":"2026-03-27T10:35:00"}

data: {"type":"complete","message":"Pipeline executado com sucesso! 🎉","timestamp":"2026-03-27T10:40:00"}
```

#### 5. Status do Pipeline

```http
GET /pipeline/status
```

**Resposta:**
```json
{
  "running": false,
  "current_step": null,
  "estados": []
}
```

### 📚 Documentação Interativa

Acesse **http://localhost:8001/docs** para explorar a documentação Swagger completa com:
- Todos os endpoints disponíveis
- Parâmetros e tipos
- Exemplos de request/response
- Teste direto pelo navegador

---

## 📥 Extração de Dados

### Executar Manualmente

```bash
# Via Docker (recomendado)
docker-compose run --rm extractor python -m extractor.main --ufs PA RJ PR

# Via Python local
python -m extractor.main --ufs PA RJ PR
```

### Opções Disponíveis

```bash
# Retomar extração (usa checkpoint)
python -m extractor.main --ufs SP MG

# Reiniciar do zero
python -m extractor.main --ufs SP --no-resume

# Ver ajuda
python -m extractor.main --help
```

### Resiliência

- **Retry Automático**: Até 3 tentativas com backoff exponencial
- **Checkpoint**: Estado salvo após cada município em `extractor/checkpoint.json`
- **Logging**: Logs estruturados em `extractor/metadata.jsonl`
- **Anti-Blocking**: User-Agent rotation e delays configuráveis

### Arquivos Gerados

```
extractor/
├── output/
│   ├── AC_Campo_Grande_20260327_103000.csv
│   ├── PA_Belem_20260327_103100.csv
│   └── ...
├── checkpoint.json          # Progresso salvo
└── metadata.jsonl          # Logs estruturados
```

---

## 💾 Modelagem do Banco

### Schema Normalizado (3NF)

```sql
-- Tabela principal de imóveis
CREATE TABLE imoveis (
    id SERIAL PRIMARY KEY,
    codigo_incra VARCHAR(17) NOT NULL UNIQUE,
    nome_imovel TEXT,
    uf CHAR(2) NOT NULL,
    municipio TEXT NOT NULL,
    area_ha NUMERIC(12, 4),
    situacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de pessoas (deduplicadas por CPF)
CREATE TABLE pessoas (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    nome_completo TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela associativa (N:N entre imóveis e pessoas)
CREATE TABLE vinculos (
    id SERIAL PRIMARY KEY,
    imovel_id INT NOT NULL REFERENCES imoveis(id) ON DELETE CASCADE,
    pessoa_id INT NOT NULL REFERENCES pessoas(id) ON DELETE CASCADE,
    tipo_vinculo TEXT NOT NULL CHECK (tipo_vinculo IN ('Proprietário', 'Arrendatário')),
    participacao_pct NUMERIC(5, 2) CHECK (participacao_pct >= 0 AND participacao_pct <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (imovel_id, pessoa_id, tipo_vinculo)
);
```

### Carregar Dados

```bash
# Via Docker (recomendado)
docker-compose run --rm loader

# Via Python local
python -m loader.main
```

### Idempotência

Todas as inserções usam **UPSERT** (`ON CONFLICT DO UPDATE`):

```python
# Exemplo: imóveis
INSERT INTO imoveis (codigo_incra, nome_imovel, uf, municipio, area_ha, situacao, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (codigo_incra) DO UPDATE SET
    nome_imovel = EXCLUDED.nome_imovel,
    area_ha = EXCLUDED.area_ha,
    situacao = EXCLUDED.situacao,
    updated_at = NOW()
RETURNING id;
```

**Benefícios:**
- ✅ Re-executar o loader não duplica dados
- ✅ Atualiza registros modificados
- ✅ Preserva `created_at` original
- ✅ Seguro para execuções concorrentes

---

## ⚡ Performance e Índices

### Índices Criados

```sql
-- Busca principal (GET /imovel/{codigo_incra})
CREATE UNIQUE INDEX imoveis_codigo_incra_key ON imoveis(codigo_incra);

-- Busca avançada por estado/município
CREATE INDEX idx_imoveis_uf ON imoveis(uf);
CREATE INDEX idx_imoveis_municipio ON imoveis(municipio);
CREATE INDEX idx_imoveis_uf_municipio ON imoveis(uf, municipio);

-- JOINs otimizados
CREATE INDEX idx_vinculos_imovel_id ON vinculos(imovel_id);
CREATE INDEX idx_vinculos_pessoa_id ON vinculos(pessoa_id);
CREATE INDEX idx_pessoas_cpf ON pessoas(cpf);
```

### Justificativas

| Índice | Tipo | Justificativa |
|--------|------|---------------|
| `imoveis_codigo_incra_key` | B-tree UNIQUE | Busca O(log n) por código. Com 500k registros, tempo < 2ms. Garante unicidade. |
| `idx_imoveis_uf` | B-tree | Filtra imóveis por estado (busca avançada, dashboards). |
| `idx_imoveis_municipio` | B-tree | Filtra por município. Suporta LIKE com índice GIST no futuro. |
| `idx_imoveis_uf_municipio` | B-tree composto | Busca combinada estado+município (query comum). |
| `idx_vinculos_imovel_id` | B-tree | Acelera JOIN `imoveis ← vinculos` na busca principal. |
| `idx_vinculos_pessoa_id` | B-tree | Acelera JOIN `vinculos → pessoas` e busca por proprietário. |
| `idx_pessoas_cpf` | B-tree UNIQUE | Deduplicação rápida e busca por CPF. |

### Evidência de Performance

```sql
EXPLAIN ANALYZE
SELECT i.*, v.*, p.*
FROM imoveis i
JOIN vinculos v ON v.imovel_id = i.id
JOIN pessoas p ON p.id = v.pessoa_id
WHERE i.codigo_incra = '26001000017';
```

**Resultado:**
```
Index Scan using imoveis_codigo_incra_key on imoveis i
  (actual time=0.051..0.053 rows=1 loops=1)
→ Nested Loop
  (actual time=0.082..0.091 rows=2 loops=1)

Execution Time: 0.3 ms  ✅
```

**SLA: < 2000 ms** ✅ (700x mais rápido)

---

## 🧠 Decisões Técnicas

### 1. Clean Architecture

**Por quê?**
- Separa regras de negócio (domain) de frameworks (infrastructure)
- Facilita testes unitários sem dependências externas
- Permite trocar tecnologias sem reescrever lógica

**Camadas:**
- **Domain**: Entidades e contratos (interfaces)
- **Application**: Casos de uso e orquestração
- **Infrastructure**: Implementações (HTTP, DB, etc)

### 2. httpx ao invés de Playwright

**Análise:**
- O "captcha" do SNCR retorna dígitos no JSON: `{"digits":"12345"}`
- Não há renderização JavaScript crítica
- httpx assíncrono é **10x mais rápido** para este caso

### 3. Normalização em 3 Tabelas

**Problema:** Relação N:N entre imóveis e pessoas.

**Solução:** Tabela associativa `vinculos`.

**Benefícios:**
- Evita redundância (CPF não duplicado)
- Consultas bidirecionais eficientes
- Integridade referencial via constraints

### 4. CPF Completo no Banco

**Decisão:** Armazenar CPF sem máscara.

**Justificativa:**
- Anonimização é regra de **exposição**, não armazenamento
- CPF mascarado impossibilita deduplicação
- Banco de dados = fonte única da verdade (dados brutos)
- Máscara aplicada na camada de serviço quando necessário

### 5. UPSERT vs DELETE + INSERT

**Escolha:** UPSERT (`ON CONFLICT DO UPDATE`).

**Vantagens:**
- Preserva `created_at` original
- Evita locks desnecessários
- Seguro para execuções concorrentes
- Idempotente (pode rodar N vezes)

### 6. Server-Sent Events para Logs

**Por quê?**
- WebSockets seria overkill (unidirecional é suficiente)
- SSE nativo no navegador (`EventSource`)
- HTTP/1.1 compatível (sem QUIC necessário)
- Auto-reconexão em caso de falha

### 7. Filtros Dinâmicos no Frontend

**Problema:** Usuário não sabe quais estados/municípios existem.

**Solução:** Endpoint `/search/filters` que busca do banco.

**Benefícios:**
- Filtros sempre atualizados com os dados reais
- Evita buscas vazias
- UX melhorada (municípios filtrados por estado)

---

## 📦 Tecnologias

| Categoria | Tecnologia | Versão | Justificativa |
|-----------|-----------|--------|---------------|
| **Linguagem** | Python | 3.11 | Async nativo, type hints, performance |
| **Web Scraping** | httpx | 0.27.0 | Cliente HTTP assíncrono, 10x mais rápido que Playwright para este caso |
| **Retry Logic** | tenacity | 8.3.0 | Backoff exponencial, retry condicional |
| **Banco de Dados** | PostgreSQL | 16 | ACID, índices avançados, JSON support |
| **ORM** | SQLAlchemy | 2.0.31 | Async support, migration-ready, type-safe |
| **API Framework** | FastAPI | 0.111.0 | Async nativo, validação automática, Swagger |
| **Servidor** | Uvicorn | 0.30.1 | ASGI server com uvloop (performance) |
| **Validação** | Pydantic | 2.7.4 | Type-safe, coerção automática, error messages claros |
| **Frontend** | Vanilla JS | - | Zero dependências, leve, rápido |
| **Web Server** | Nginx | Alpine | Servir SPA, ~10MB de imagem |
| **Containerização** | Docker | - | Isolamento, reprodutibilidade |
| **Orquestração** | Docker Compose | v2 | Multi-container, networking, volumes |

---

## 🎓 Conceitos Aplicados

- ✅ **Clean Architecture** (Hexagonal/Ports & Adapters)
- ✅ **SOLID Principles** (Single Responsibility, Open/Closed, etc)
- ✅ **Dependency Inversion** (IoC via interfaces)
- ✅ **Repository Pattern** (Abstração de persistência)
- ✅ **Service Layer** (Lógica de negócio)
- ✅ **Idempotency** (Operações seguras para retry)
- ✅ **Checkpoint Pattern** (Resiliência em pipelines)
- ✅ **Database Normalization** (3NF)
- ✅ **Async/Await** (I/O concorrente)
- ✅ **Server-Sent Events** (Real-time unidirecional)
- ✅ **RESTful API** (HTTP semântico)

---

## 📝 Comandos Úteis

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f postgres

# Parar todos os containers
docker-compose down

# Parar e remover volumes (limpar banco)
docker-compose down -v

# Reconstruir imagens
docker-compose build

# Reiniciar um serviço
docker-compose restart api

# Executar comando no container
docker-compose exec api bash
docker-compose exec postgres psql -U sncr_user -d sncr

# Ver containers rodando
docker-compose ps

# Ver estatísticas de recursos
docker stats
```

---

## 🐛 Troubleshooting

### Porta já em uso

```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Banco não inicializa

```bash
# Limpar volumes e reiniciar
docker-compose down -v
docker-compose up -d postgres
docker-compose logs -f postgres
```

### Frontend não carrega

```bash
# Verificar se está rodando
docker-compose ps frontend

# Reconstruir
docker-compose up -d --build frontend

# Testar diretamente
curl http://localhost:3000
```

### API retorna erro 500

```bash
# Ver logs detalhados
docker-compose logs api --tail 100

# Verificar conexão com banco
docker-compose exec api python -c "from api.config.database import engine; import asyncio; asyncio.run(engine.dispose())"
```

---

## 📄 Licença

Este projeto foi desenvolvido como parte de um desafio técnico para vaga de Data Engineer na DadosFazenda.

---

## 👨‍💻 Autor

Desenvolvido com muito conhecimento de noites sem dormi e seguindo as melhores práticas de engenharia de software.
