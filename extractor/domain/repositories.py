from abc import ABC, abstractmethod
from typing import List
from extractor.domain.entities import Estado, Municipio, Captcha


class EstadoRepository(ABC):
    @abstractmethod
    async def list_all(self) -> List[Estado]:
        pass


class MunicipioRepository(ABC):
    @abstractmethod
    async def list_by_uf(self, uf: str) -> List[Municipio]:
        pass


class CaptchaRepository(ABC):
    @abstractmethod
    async def get_captcha(self) -> Captcha:
        pass


class ExportRepository(ABC):
    @abstractmethod
    async def export_csv(
        self,
        uf: str,
        municipio: str,
        captcha_id: str,
        captcha_value: str
    ) -> bytes:
        pass
