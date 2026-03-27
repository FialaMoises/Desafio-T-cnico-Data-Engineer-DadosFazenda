import httpx
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from extractor.config.settings import settings
from extractor.domain.entities import Estado, Municipio, Captcha
from extractor.domain.repositories import (
    EstadoRepository,
    MunicipioRepository,
    CaptchaRepository,
    ExportRepository
)


class HttpEstadoRepository(EstadoRepository):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.base_url

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def list_all(self) -> List[Estado]:
        response = await self.client.get(f"{self.base_url}/api/estados")
        response.raise_for_status()
        data = response.json()
        return [Estado(sigla=item["sigla"], nome=item["nome"]) for item in data]


class HttpMunicipioRepository(MunicipioRepository):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.base_url

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def list_by_uf(self, uf: str) -> List[Municipio]:
        response = await self.client.get(f"{self.base_url}/api/municipios/{uf}")
        response.raise_for_status()
        data = response.json()
        return [Municipio(nome=item["nome"]) for item in data]


class HttpCaptchaRepository(CaptchaRepository):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.base_url

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def get_captcha(self) -> Captcha:
        response = await self.client.get(f"{self.base_url}/api/captcha")
        response.raise_for_status()
        data = response.json()
        return Captcha(
            captcha_id=data["captcha_id"],
            captcha_value=data["digits"]
        )


class HttpExportRepository(ExportRepository):
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.base_url = settings.base_url

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def export_csv(
        self,
        uf: str,
        municipio: str,
        captcha_id: str,
        captcha_value: str
    ) -> bytes:
        params = {
            "uf": uf,
            "municipio": municipio,
            "captcha_id": captcha_id,
            "captcha_value": captcha_value,
        }
        response = await self.client.get(
            f"{self.base_url}/api/dados-abertos/exportar",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.content
