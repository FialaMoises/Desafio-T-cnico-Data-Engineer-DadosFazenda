@echo off

echo ==========================================
echo SNCR Pipeline - Execução via Docker
echo ==========================================
echo.

echo [1/4] Subindo PostgreSQL...
docker-compose -f docker-compose.full.yml up -d postgres
timeout /t 10 /nobreak >nul

echo [2/4] Executando extração...
docker-compose -f docker-compose.full.yml up extractor

echo [3/4] Carregando dados no banco...
docker-compose -f docker-compose.full.yml up loader

echo [4/4] Subindo API...
docker-compose -f docker-compose.full.yml up -d api

echo.
echo ==========================================
echo Pipeline concluído!
echo ==========================================
echo.
echo API disponível em: http://localhost:8000/docs
echo.
echo Para ver logs:
echo   docker-compose -f docker-compose.full.yml logs -f api
echo.
