# Frontend SNCR - Sistema Nacional de Cadastro Rural

Interface web para visualização dos dados do SNCR.

## Como usar

### Opção 1: Com Docker (Recomendado)

```bash
docker-compose up -d frontend
```

Depois acesse: http://localhost:3000

**Ou inicie tudo de uma vez:**
```bash
docker-compose up -d
```

### Opção 2: Abrir diretamente no navegador

Simplesmente abra o arquivo `index.html` no seu navegador:

```
file:///caminho/para/frontend/index.html
```

### Opção 3: Usar um servidor HTTP local

#### Com Python:
```bash
cd frontend
python -m http.server 3000
```

#### Com Node.js (http-server):
```bash
cd frontend
npx http-server -p 3000
```

#### Com PowerShell:
```powershell
cd frontend
.\start-frontend.ps1
```

## Funcionalidades

- 🔍 **Busca de Imóveis**: Consulte imóveis pelo Código INCRA
- 📊 **Estatísticas**: Visualize totais de imóveis, pessoas e vínculos
- 🔒 **Dados Anonimizados**: CPF e nomes exibidos com privacidade
- 📱 **Responsivo**: Funciona em desktop e mobile
- ⚡ **Interface Moderna**: Design clean e intuitivo

## Exemplos de Códigos INCRA

- `11001000016`
- `26001000017`
- `26001000000`

## Requisitos

- API SNCR rodando em http://localhost:8001
- Navegador moderno (Chrome, Firefox, Edge, Safari)
