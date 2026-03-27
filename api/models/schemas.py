from pydantic import BaseModel, Field
from decimal import Decimal


class ProprietarioResponse(BaseModel):
    nome_completo: str
    cpf: str
    vinculo: str
    participacao_pct: Decimal | None = None

    class Config:
        from_attributes = True


class ImovelResponse(BaseModel):
    codigo_incra: str
    area_ha: Decimal | None
    situacao: str | None
    proprietarios: list[ProprietarioResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str
