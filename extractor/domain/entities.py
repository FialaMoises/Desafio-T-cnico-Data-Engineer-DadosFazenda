from dataclasses import dataclass
from datetime import datetime


@dataclass
class Estado:
    sigla: str
    nome: str


@dataclass
class Municipio:
    nome: str


@dataclass
class Captcha:
    captcha_id: str
    captcha_value: str


@dataclass
class ExtracaoMetadata:
    timestamp: datetime
    uf: str
    municipio: str
    total_registros: int | None
    arquivo: str | None
    duracao_segundos: float
    status: str
    erro: str | None = None
