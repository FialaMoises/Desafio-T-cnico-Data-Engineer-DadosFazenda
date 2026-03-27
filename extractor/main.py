import asyncio
import argparse
import httpx

from extractor.config.settings import settings
from extractor.config.logger import setup_logger
from extractor.infrastructure.http_client import (
    HttpEstadoRepository,
    HttpMunicipioRepository,
    HttpCaptchaRepository,
    HttpExportRepository
)
from extractor.infrastructure.checkpoint_manager import CheckpointManager
from extractor.infrastructure.metadata_writer import MetadataWriter
from extractor.infrastructure.proxy_manager import ProxyManager
from extractor.infrastructure.user_agent_manager import UserAgentManager
from extractor.application.scraper_service import ScraperService


async def main(ufs: list[str], resume: bool, retry_until_complete: bool) -> None:
    logger = setup_logger("scraper", settings.log_dir / "scraper.log")

    proxy_manager = ProxyManager(settings.proxy_list)

    if proxy_manager.has_proxies():
        logger.info(f"🔄 Proxy rotation ativado com {len(proxy_manager.proxies)} proxies")

    client_kwargs = {
        "timeout": 20,
        "follow_redirects": True,
        "headers": UserAgentManager.get_headers() if settings.use_random_user_agent else {}
    }

    if settings.use_proxy_rotation and proxy_manager.has_proxies():
        proxy_url = proxy_manager.get_random_proxy()
        client_kwargs["proxies"] = {"http://": proxy_url, "https://": proxy_url}
        logger.info(f"🌐 Usando proxy: {proxy_url}")

    if settings.use_random_user_agent:
        logger.info(f"🎭 User-Agent rotation ativado")

    async with httpx.AsyncClient(**client_kwargs) as client:
        estado_repo = HttpEstadoRepository(client)
        municipio_repo = HttpMunicipioRepository(client)
        captcha_repo = HttpCaptchaRepository(client)
        export_repo = HttpExportRepository(client)

        checkpoint_manager = CheckpointManager(settings.checkpoint_dir)
        metadata_writer = MetadataWriter(settings.log_dir)

        service = ScraperService(
            estado_repo=estado_repo,
            municipio_repo=municipio_repo,
            captcha_repo=captcha_repo,
            export_repo=export_repo,
            checkpoint_manager=checkpoint_manager,
            metadata_writer=metadata_writer,
            logger=logger,
        )

        await service.run(ufs=ufs, resume=resume, retry_until_complete=retry_until_complete)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNCR Scraper")
    parser.add_argument(
        "--ufs",
        nargs="+",
        default=["SP", "MG", "GO"],
        help="UFs a extrair (ex: SP MG GO)"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignora checkpoints e reinicia do zero"
    )
    parser.add_argument(
        "--retry-until-complete",
        action="store_true",
        help="Continua tentando até extrair 100% dos municípios"
    )
    args = parser.parse_args()

    asyncio.run(main(
        ufs=args.ufs,
        resume=not args.no_resume,
        retry_until_complete=args.retry_until_complete
    ))
