from abc import ABC, abstractmethod
from typing import List
from loader.domain.entities import Imovel, Pessoa, Vinculo


class ImovelRepository(ABC):
    @abstractmethod
    async def upsert(self, imovel: Imovel) -> int:
        pass


class PessoaRepository(ABC):
    @abstractmethod
    async def upsert(self, pessoa: Pessoa) -> int:
        pass


class VinculoRepository(ABC):
    @abstractmethod
    async def upsert_batch(self, vinculos: List[Vinculo]) -> None:
        pass
