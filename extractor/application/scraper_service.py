import asyncio
import random
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path
from typing import Set

from extractor.domain.repositories import (
    EstadoRepository,
    MunicipioRepository,
    CaptchaRepository,
    ExportRepository
)
from extractor.domain.entities import ExtracaoMetadata
from extractor.infrastructure.checkpoint_manager import CheckpointManager
from extractor.infrastructure.metadata_writer import MetadataWriter
from extractor.config.settings import settings


class ScraperService:
    def __init__(
        self,
        estado_repo: EstadoRepository,
        municipio_repo: MunicipioRepository,
        captcha_repo: CaptchaRepository,
        export_repo: ExportRepository,
        checkpoint_manager: CheckpointManager,
        metadata_writer: MetadataWriter,
        logger: Logger,
    ):
        self.estado_repo = estado_repo
        self.municipio_repo = municipio_repo
        self.captcha_repo = captcha_repo
        self.export_repo = export_repo
        self.checkpoint_manager = checkpoint_manager
        self.metadata_writer = metadata_writer
        self.logger = logger

    async def process_municipio(
        self,
        uf: str,
        municipio: str,
        concluidos: Set[str],
        max_attempts: int = 5,
    ) -> int | None:
        output_path = settings.output_dir / uf / f"{municipio.replace(' ', '_')}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        for attempt in range(1, max_attempts + 1):
            started = datetime.now(timezone.utc)
            try:
                if attempt > 1:
                    backoff_time = min(2 ** attempt, 30)
                    self.logger.info(
                        f"🔄 {uf}/{municipio} — Tentativa {attempt}/{max_attempts} "
                        f"(aguardando {backoff_time}s...)"
                    )
                    await asyncio.sleep(backoff_time)

                captcha = await self.captcha_repo.get_captcha()

                delay = settings.delay_seconds + random.uniform(0, settings.delay_random_range)
                await asyncio.sleep(delay)

                content = await self.export_repo.export_csv(
                    uf=uf,
                    municipio=municipio,
                    captcha_id=captcha.captcha_id,
                    captcha_value=captcha.captcha_value
                )
                output_path.write_bytes(content)

                linhas = max(0, content.decode("utf-8", errors="ignore").count("\n") - 1)
                elapsed = (datetime.now(timezone.utc) - started).total_seconds()

                self.logger.info(f"✔ {uf}/{municipio} — {linhas} registros ({elapsed:.1f}s)")

                metadata = ExtracaoMetadata(
                    timestamp=started,
                    uf=uf,
                    municipio=municipio,
                    total_registros=linhas,
                    arquivo=str(output_path),
                    duracao_segundos=elapsed,
                    status="sucesso"
                )
                self.metadata_writer.append(metadata)
                concluidos.add(municipio)
                return linhas

            except Exception as exc:
                elapsed = (datetime.now(timezone.utc) - started).total_seconds()

                if attempt == max_attempts:
                    self.logger.error(
                        f"✘ {uf}/{municipio} — Falhou após {max_attempts} tentativas: {exc}"
                    )
                    metadata = ExtracaoMetadata(
                        timestamp=started,
                        uf=uf,
                        municipio=municipio,
                        total_registros=None,
                        arquivo=None,
                        duracao_segundos=elapsed,
                        status="erro",
                        erro=str(exc)
                    )
                    self.metadata_writer.append(metadata)
                    return None
                else:
                    self.logger.warning(
                        f"⚠ {uf}/{municipio} — Erro na tentativa {attempt}: {exc}"
                    )

        return None

    async def process_uf(self, uf: str, resume: bool = True, retry_until_complete: bool = False) -> None:
        concluidos = self.checkpoint_manager.load(uf) if resume else set()
        municipios_entities = await self.municipio_repo.list_by_uf(uf)
        municipios = [m.nome for m in municipios_entities]

        round_number = 1
        while True:
            pendentes = [m for m in municipios if m not in concluidos]

            if not pendentes:
                self.logger.info(
                    f"✅ {uf} — 100% completo: {len(concluidos)}/{len(municipios)} municípios"
                )
                break

            if round_number > 1:
                self.logger.info(
                    f"🔄 {uf} — Rodada {round_number}: {len(pendentes)} municípios restantes"
                )
            else:
                self.logger.info(
                    f"── {uf}: {len(municipios)} municípios, {len(pendentes)} pendentes"
                )

            for municipio in pendentes:
                await self.process_municipio(uf, municipio, concluidos)
                self.checkpoint_manager.save(uf, concluidos)

                delay = settings.delay_seconds + random.uniform(0, settings.delay_random_range)
                await asyncio.sleep(delay)

            if not retry_until_complete:
                self.logger.info(
                    f"── {uf} concluído: {len(concluidos)}/{len(municipios)} municípios"
                )
                break

            if round_number >= settings.max_rounds:
                self.logger.warning(
                    f"⚠ {uf} — Limite de {settings.max_rounds} rodadas atingido. "
                    f"Progresso: {len(concluidos)}/{len(municipios)} municípios"
                )
                break

            round_number += 1
            if pendentes and retry_until_complete:
                await asyncio.sleep(5)

    async def run(self, ufs: list[str], resume: bool = True, retry_until_complete: bool = False) -> None:
        estados = await self.estado_repo.list_all()
        estados_validos = {e.sigla for e in estados}

        ufs_invalidas = [u for u in ufs if u not in estados_validos]
        if ufs_invalidas:
            self.logger.warning(f"UFs não encontradas, ignorando: {ufs_invalidas}")

        ufs_validas = [u for u in ufs if u in estados_validos]

        for uf in ufs_validas:
            await self.process_uf(uf, resume=resume, retry_until_complete=retry_until_complete)
