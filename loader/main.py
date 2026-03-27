import asyncio
import argparse
import logging
from pathlib import Path

from loader.config.settings import db_settings
from loader.infrastructure.database import (
    DatabaseConnection,
    PostgresImovelRepository,
    PostgresPessoaRepository,
    PostgresVinculoRepository
)
from loader.services.transformer import DataTransformer
from loader.services.loader_service import LoaderService


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("loader")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


async def main(input_dir: Path) -> None:
    logger = setup_logger()

    db = DatabaseConnection(db_settings.connection_string)
    imovel_repo = PostgresImovelRepository(db)
    pessoa_repo = PostgresPessoaRepository(db)
    vinculo_repo = PostgresVinculoRepository(db)

    transformer = DataTransformer()

    service = LoaderService(
        imovel_repo=imovel_repo,
        pessoa_repo=pessoa_repo,
        vinculo_repo=vinculo_repo,
        transformer=transformer,
        logger=logger,
    )

    await service.load_directory(input_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNCR Loader")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("extractor/output"),
        help="Diretório com arquivos CSV extraídos"
    )
    args = parser.parse_args()

    asyncio.run(main(args.input_dir))
