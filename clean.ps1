Write-Host "Limpando arquivos desnecessários para Git..." -ForegroundColor Cyan

Write-Host "`n[1/4] Removendo __pycache__..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -File | Remove-Item -Force
Get-ChildItem -Path . -Recurse -Filter "*.pyo" -File | Remove-Item -Force

Write-Host "[2/4] Removendo dados extraídos..." -ForegroundColor Yellow
if (Test-Path "extractor\output") { Remove-Item -Recurse -Force "extractor\output\*" }
if (Test-Path "extractor\checkpoints") { Remove-Item -Recurse -Force "extractor\checkpoints\*" }
if (Test-Path "extractor\logs") { Remove-Item -Recurse -Force "extractor\logs\*" }

Write-Host "[3/4] Removendo .env (mantendo .env.example)..." -ForegroundColor Yellow
if (Test-Path ".env") { Remove-Item -Force ".env" }

Write-Host "[4/4] Removendo desafio.txt..." -ForegroundColor Yellow
if (Test-Path "desafio.txt") { Remove-Item -Force "desafio.txt" }

Write-Host "`n✅ Limpeza concluída!" -ForegroundColor Green
Write-Host "`nArquivos prontos para commit no Git." -ForegroundColor Cyan
Write-Host "`nPróximos passos:" -ForegroundColor White
Write-Host "  1. git init" -ForegroundColor Gray
Write-Host "  2. git add ." -ForegroundColor Gray
Write-Host "  3. git commit -m 'Initial commit: SNCR Data Pipeline'" -ForegroundColor Gray
Write-Host "  4. git remote add origin <seu-repositorio>" -ForegroundColor Gray
Write-Host "  5. git push -u origin main" -ForegroundColor Gray
