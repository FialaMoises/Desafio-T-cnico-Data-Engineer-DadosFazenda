# 📦 Guia de Publicação no Git

## 🧹 Passo 1: Limpar Arquivos Desnecessários

### PowerShell:
```powershell
.\clean.ps1
```

### CMD:
```cmd
clean.bat
```

Isso remove:
- ✅ `__pycache__/` e arquivos `.pyc`
- ✅ Dados extraídos (`extractor/output/`, `checkpoints/`, `logs/`)
- ✅ Arquivo `.env` (configuração local)
- ✅ `desafio.txt` (enunciado do desafio)

---

## 🚀 Passo 2: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome do repositório: `sncr-data-pipeline`
3. Descrição: `Pipeline de dados do SNCR com Clean Architecture e SOLID`
4. Visibilidade: **Public** ou **Private**
5. **NÃO** marque "Add README" (já temos)
6. Clique em **"Create repository"**

---

## 📤 Passo 3: Publicar o Código

### Inicializar Git e fazer primeiro commit:

```bash
git init
git add .
git commit -m "feat: implementa pipeline completo SNCR com Clean Architecture

- Extrator com retry inteligente e suporte a proxies
- Loader com upsert idempotente no PostgreSQL
- API REST com FastAPI e CPF anonimizado
- Docker Compose para orquestração completa
- Documentação completa (README, USAGE, PROXY_SETUP)

Arquitetura: Clean Architecture + SOLID
Stack: Python, FastAPI, PostgreSQL, Docker"
```

### Conectar ao GitHub e publicar:

```bash
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/sncr-data-pipeline.git
git push -u origin main
```

Substitua `SEU-USUARIO` pelo seu username do GitHub.

---

## 🔐 Passo 4: Configurar GitHub (Primeira Vez)

Se for seu primeiro push, configure suas credenciais:

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@example.com"
```

### Autenticação (escolha uma):

#### Opção 1: HTTPS com Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Marque: `repo` (Full control of private repositories)
4. Copie o token
5. No primeiro `git push`, use o token como senha

#### Opção 2: SSH
```bash
ssh-keygen -t ed25519 -C "seu.email@example.com"
cat ~/.ssh/id_ed25519.pub
```
Copie a chave e adicione em: GitHub → Settings → SSH and GPG keys

---

## 📝 Passo 5: Adicionar Badges ao README (Opcional)

Edite o `README.md` e adicione no topo:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

---

## 🔄 Passo 6: Atualizações Futuras

Após fazer alterações:

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push
```

### Mensagens de Commit (Convenção)

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `refactor:` - Refatoração de código
- `test:` - Adição de testes
- `chore:` - Tarefas de manutenção

**Exemplos:**
```bash
git commit -m "feat: adiciona suporte a SOCKS5 proxies"
git commit -m "fix: corrige erro 403 em municípios com acento"
git commit -m "docs: atualiza README com exemplos de uso"
```

---

## 📊 Verificar Status do Repositório

```bash
git status
git log --oneline
git remote -v
```

---

## 🛡️ O Que Não Será Enviado (Graças ao .gitignore)

- ❌ `__pycache__/` e `.pyc`
- ❌ `.env` (configurações locais)
- ❌ `extractor/output/` (dados extraídos)
- ❌ `extractor/checkpoints/` (progresso local)
- ❌ `extractor/logs/` (logs locais)
- ❌ `desafio.txt` (enunciado do desafio)

---

## ✅ O Que Será Enviado

- ✅ Todo o código-fonte (`extractor/`, `loader/`, `api/`)
- ✅ Configuração Docker (`docker-compose.yml`, `Dockerfile`)
- ✅ Documentação (`README.md`, `USAGE.md`, `PROXY_SETUP.md`)
- ✅ Scripts de setup (`.env.example`, `requirements.txt`)
- ✅ Database schema (`db/schema.sql`, `db/indexes.sql`)

---

## 🎯 Estrutura Final no GitHub

```
sncr-data-pipeline/
├── README.md              ⭐ Documentação principal
├── USAGE.md               📖 Guia de uso
├── PROXY_SETUP.md         🌐 Config de proxies
├── requirements.txt       📦 Dependências
├── docker-compose.yml     🐳 Orquestração
├── .env.example           ⚙️ Exemplo de config
├── extractor/             📥 Módulo de extração
├── loader/                💾 Módulo de carga
├── api/                   🌐 API REST
└── db/                    🗄️ Schema do banco
```

---

## 🚨 Importante: Antes do Push

1. ✅ Execute `.\clean.ps1` para remover dados temporários
2. ✅ Verifique se `.env` não está sendo commitado
3. ✅ Teste se o projeto funciona após clone:
   ```bash
   git clone https://github.com/SEU-USUARIO/sncr-data-pipeline.git
   cd sncr-data-pipeline
   .\run-pipeline.ps1
   ```

---

## 📧 Compartilhando com Recrutadores

Adicione ao corpo do email:

```
Repositório: https://github.com/SEU-USUARIO/sncr-data-pipeline

Stack: Python, FastAPI, PostgreSQL, Docker
Arquitetura: Clean Architecture + SOLID
Destaques:
- Retry inteligente com backoff exponencial
- Suporte a proxies rotativos
- Idempotência garantida (UPSERT)
- API documentada (Swagger)
- Performance < 2ms (índices otimizados)

Executar localmente:
git clone <repo>
cd sncr-data-pipeline
.\run-pipeline.ps1
```
