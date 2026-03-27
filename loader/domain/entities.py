from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Imovel:
    codigo_incra: str
    nome_imovel: str | None
    uf: str
    municipio: str
    area_ha: Decimal | None
    situacao: str | None


@dataclass
class Pessoa:
    cpf: str
    nome_completo: str


@dataclass
class Vinculo:
    codigo_incra: str
    cpf: str
    tipo_vinculo: str
    participacao_pct: Decimal | None
