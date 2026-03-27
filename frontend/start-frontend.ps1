# Script para iniciar o frontend SNCR

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Frontend SNCR - Iniciando...  " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se a API está rodando
Write-Host "Verificando API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API está rodando em http://localhost:8001" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ AVISO: API não está respondendo em http://localhost:8001" -ForegroundColor Red
    Write-Host "  Execute: docker-compose up -d api" -ForegroundColor Yellow
    Write-Host ""
}

# Verificar se Python está instalado
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✓ Python encontrado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciando servidor HTTP na porta 3000..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Acesse o frontend em:" -ForegroundColor Green
    Write-Host "  http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
    Write-Host ""

    python -m http.server 3000
} else {
    Write-Host "✗ Python não encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Abrindo arquivo diretamente no navegador..." -ForegroundColor Yellow

    $htmlPath = Join-Path $PSScriptRoot "index.html"
    Start-Process $htmlPath

    Write-Host ""
    Write-Host "✓ Frontend aberto no navegador padrão" -ForegroundColor Green
    Write-Host ""
    Write-Host "NOTA: Algumas funcionalidades podem não funcionar corretamente" -ForegroundColor Yellow
    Write-Host "ao abrir o arquivo diretamente. Recomendamos usar um servidor HTTP." -ForegroundColor Yellow
}
