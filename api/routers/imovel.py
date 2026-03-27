from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.config.database import get_db
from api.models.schemas import ImovelResponse, ErrorResponse
from api.services.imovel_service import ImovelService
from api.services.cpf_anonymizer import CPFAnonymizer

router = APIRouter(prefix="/imovel", tags=["Imóveis"])


@router.get(
    "/{codigo_incra}",
    response_model=ImovelResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Imóvel não encontrado"}
    },
    summary="Consultar imóvel por código INCRA",
    description="Retorna dados do imóvel e proprietários com CPF anonimizado"
)
async def get_imovel(
    codigo_incra: str,
    session: AsyncSession = Depends(get_db)
):
    anonymizer = CPFAnonymizer()
    service = ImovelService(anonymizer)

    imovel = await service.get_by_codigo_incra(codigo_incra, session)

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Imóvel com código INCRA '{codigo_incra}' não encontrado."
        )

    return imovel
