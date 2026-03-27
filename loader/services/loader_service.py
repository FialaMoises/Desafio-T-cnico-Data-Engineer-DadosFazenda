import logging
from pathlib import Path
from typing import List

from loader.domain.repositories import ImovelRepository, PessoaRepository, VinculoRepository
from loader.infrastructure.csv_reader import CSVReader
from loader.services.transformer import DataTransformer


class LoaderService:
    def __init__(
        self,
        imovel_repo: ImovelRepository,
        pessoa_repo: PessoaRepository,
        vinculo_repo: VinculoRepository,
        transformer: DataTransformer,
        logger: logging.Logger,
    ):
        self.imovel_repo = imovel_repo
        self.pessoa_repo = pessoa_repo
        self.vinculo_repo = vinculo_repo
        self.transformer = transformer
        self.logger = logger

    async def load_file(self, file_path: Path) -> None:
        self.logger.info(f"Carregando {file_path}")

        rows = CSVReader.read(file_path)
        if not rows:
            self.logger.warning(f"Arquivo vazio: {file_path}")
            return

        vinculos = []

        for row in rows:
            imovel = self.transformer.transform_imovel(row)
            await self.imovel_repo.upsert(imovel)

            pessoa = self.transformer.transform_pessoa(row)
            if pessoa:
                await self.pessoa_repo.upsert(pessoa)

            vinculo = self.transformer.transform_vinculo(row)
            if vinculo:
                vinculos.append(vinculo)

        if vinculos:
            await self.vinculo_repo.upsert_batch(vinculos)

        self.logger.info(f"✔ {file_path.name} — {len(rows)} registros carregados")

    async def load_directory(self, directory: Path) -> None:
        csv_files = list(directory.rglob("*.csv"))
        self.logger.info(f"Encontrados {len(csv_files)} arquivos CSV em {directory}")

        for csv_file in csv_files:
            try:
                await self.load_file(csv_file)
            except Exception as e:
                self.logger.error(f"Erro ao carregar {csv_file}: {e}")
                continue

        self.logger.info(f"Carga completa: {len(csv_files)} arquivos processados")
