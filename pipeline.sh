#!/bin/bash

set -e

UFS="${1:-SP MG GO}"

echo "=========================================="
echo "SNCR Pipeline - Execução Completa"
echo "=========================================="
echo ""

echo "[1/5] Verificando ambiente..."
if [ ! -f .env ]; then
    echo "Copiando .env.example para .env"
    cp .env.example .env
fi

echo "[2/5] Subindo PostgreSQL..."
docker-compose up -d postgres
sleep 5

echo "[3/5] Executando extração (UFs: $UFS)..."
python -m extractor.main --ufs $UFS

echo "[4/5] Carregando dados no PostgreSQL..."
python -m loader.main --input-dir extractor/output

echo "[5/5] Subindo API..."
docker-compose up -d api

echo ""
echo "=========================================="
echo "Pipeline concluído com sucesso!"
echo "=========================================="
echo ""
echo "API disponível em: http://localhost:8000"
echo "Documentação (Swagger): http://localhost:8000/docs"
echo ""
echo "Exemplo de consulta:"
echo "  curl http://localhost:8000/imovel/{codigo_incra}"
echo ""
