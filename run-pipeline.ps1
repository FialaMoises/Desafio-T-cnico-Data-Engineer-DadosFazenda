Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SNCR Pipeline - Execução Completa" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/5] Verificando PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres
Start-Sleep -Seconds 5

Write-Host "[2/5] Executando extração..." -ForegroundColor Yellow
docker run --rm -v "${PWD}:/app" -w /app python:3.11-slim bash -c "pip install -q httpx tenacity pydantic-settings && python -m extractor.main --ufs SP MG GO --retry-until-complete"

Write-Host "[3/5] Carregando dados no PostgreSQL..." -ForegroundColor Yellow
$network = "desafio-t-cnico-data-engineer-dadosfazenda_sncr-network"
docker run --rm -v "${PWD}:/app" -w /app --network $network `
  -e POSTGRES_HOST=postgres `
  -e POSTGRES_PORT=5432 `
  -e POSTGRES_DB=sncr `
  -e POSTGRES_USER=sncr_user `
  -e POSTGRES_PASSWORD=sncr_pass `
  python:3.11-slim bash -c "pip install -q psycopg2-binary pydantic-settings && python -m loader.main --input-dir extractor/output"

Write-Host "[4/5] Subindo API..." -ForegroundColor Yellow
docker-compose up -d api

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Pipeline concluído com sucesso!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "API disponível em: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentação (Swagger): http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Exemplo de consulta:" -ForegroundColor Yellow
Write-Host "  curl http://localhost:8000/imovel/{codigo_incra}" -ForegroundColor White
Write-Host ""
