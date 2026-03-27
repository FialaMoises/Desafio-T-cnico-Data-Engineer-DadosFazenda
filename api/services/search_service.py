from sqlalchemy import select, func, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from api.models.database_models import Imovel, Vinculo, Pessoa
from api.models.schemas import ImovelResponse, ProprietarioResponse


class SearchService:

    async def get_available_filters(self, session: AsyncSession) -> Dict[str, Any]:
        estados_query = select(distinct(Imovel.uf)).order_by(Imovel.uf)
        estados_result = await session.execute(estados_query)
        estados = [row[0] for row in estados_result.all()]

        municipios_by_uf = {}
        for uf in estados:
            municipios_query = (
                select(distinct(Imovel.municipio))
                .where(Imovel.uf == uf)
                .order_by(Imovel.municipio)
            )
            municipios_result = await session.execute(municipios_query)
            municipios_by_uf[uf] = [row[0] for row in municipios_result.all()]

        situacoes_query = select(distinct(Imovel.situacao)).order_by(Imovel.situacao)
        situacoes_result = await session.execute(situacoes_query)
        situacoes = [row[0] for row in situacoes_result.all() if row[0]]

        total_imoveis_query = select(func.count(Imovel.id))
        total_imoveis = await session.scalar(total_imoveis_query)

        total_pessoas_query = select(func.count(Pessoa.id))
        total_pessoas = await session.scalar(total_pessoas_query)

        total_vinculos_query = select(func.count(Vinculo.id))
        total_vinculos = await session.scalar(total_vinculos_query)

        area_min_query = select(func.min(Imovel.area_ha)).where(Imovel.area_ha.isnot(None))
        area_max_query = select(func.max(Imovel.area_ha)).where(Imovel.area_ha.isnot(None))

        area_min = await session.scalar(area_min_query)
        area_max = await session.scalar(area_max_query)

        return {
            "estados": estados,
            "municipios_by_estado": municipios_by_uf,
            "situacoes": situacoes,
            "estatisticas": {
                "total_imoveis": total_imoveis or 0,
                "total_pessoas": total_pessoas or 0,
                "total_vinculos": total_vinculos or 0
            },
            "area_range": {
                "min": float(area_min) if area_min else 0,
                "max": float(area_max) if area_max else 0
            }
        }

    async def search_imoveis(
        self,
        session: AsyncSession,
        uf: str | None = None,
        municipio: str | None = None,
        situacao: str | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
        nome_imovel: str | None = None,
        nome_pessoa: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ImovelResponse]:
        query = (
            select(Imovel)
            .options(
                selectinload(Imovel.vinculos).selectinload(Vinculo.pessoa)
            )
        )

        if uf:
            query = query.where(Imovel.uf == uf.upper())

        if municipio:
            query = query.where(Imovel.municipio.ilike(f"%{municipio}%"))

        if situacao:
            query = query.where(Imovel.situacao == situacao)

        if area_min is not None:
            query = query.where(Imovel.area_ha >= area_min)

        if area_max is not None:
            query = query.where(Imovel.area_ha <= area_max)

        if nome_imovel:
            query = query.where(Imovel.nome_imovel.ilike(f"%{nome_imovel}%"))

        if nome_pessoa:
            query = (
                query
                .join(Imovel.vinculos)
                .join(Vinculo.pessoa)
                .where(Pessoa.nome_completo.ilike(f"%{nome_pessoa}%"))
            )

        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        imoveis = result.unique().scalars().all()

        return [
            ImovelResponse(
                codigo_incra=imovel.codigo_incra,
                nome_imovel=imovel.nome_imovel,
                uf=imovel.uf,
                municipio=imovel.municipio,
                area_ha=imovel.area_ha,
                situacao=imovel.situacao,
                proprietarios=[
                    ProprietarioResponse(
                        nome_completo=vinculo.pessoa.nome_completo,
                        cpf=vinculo.pessoa.cpf,
                        vinculo=vinculo.tipo_vinculo,
                        participacao_pct=vinculo.participacao_pct
                    )
                    for vinculo in imovel.vinculos
                ]
            )
            for imovel in imoveis
        ]
