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
    nome_imovel: str | None = None
    uf: str | None = None
    municipio: str | None = None
    area_ha: Decimal | None = None
    situacao: str | None = None
    proprietarios: list[ProprietarioResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    detail: str
