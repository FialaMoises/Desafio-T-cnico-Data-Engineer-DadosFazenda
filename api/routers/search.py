from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.config.database import get_db
from api.models.schemas import ImovelResponse
from api.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Busca Avançada"])


@router.get("/filters")
async def get_filters(session: AsyncSession = Depends(get_db)):
    service = SearchService()
    return await service.get_available_filters(session)


@router.get("/imoveis", response_model=List[ImovelResponse])
async def search_imoveis(
    uf: str | None = Query(None, description="Estado (UF)"),
    municipio: str | None = Query(None, description="Município (busca parcial)"),
    situacao: str | None = Query(None, description="Situação do imóvel"),
    area_min: float | None = Query(None, description="Área mínima em hectares"),
    area_max: float | None = Query(None, description="Área máxima em hectares"),
    nome_imovel: str | None = Query(None, description="Nome do imóvel (busca parcial)"),
    nome_pessoa: str | None = Query(None, description="Nome do proprietário (busca parcial)"),
    limit: int = Query(100, ge=1, le=500, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: AsyncSession = Depends(get_db)
):
    service = SearchService()
    return await service.search_imoveis(
        session=session,
        uf=uf,
        municipio=municipio,
        situacao=situacao,
        area_min=area_min,
        area_max=area_max,
        nome_imovel=nome_imovel,
        nome_pessoa=nome_pessoa,
        limit=limit,
        offset=offset
    )
