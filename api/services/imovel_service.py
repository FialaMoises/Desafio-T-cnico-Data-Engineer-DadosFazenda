from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.database_models import Imovel, Vinculo
from api.models.schemas import ImovelResponse, ProprietarioResponse
from api.services.cpf_anonymizer import CPFAnonymizer


class ImovelService:
    def __init__(self, anonymizer: CPFAnonymizer):
        self.anonymizer = anonymizer

    async def get_by_codigo_incra(
        self,
        codigo_incra: str,
        session: AsyncSession
    ) -> ImovelResponse | None:
        query = (
            select(Imovel)
            .where(Imovel.codigo_incra == codigo_incra)
            .options(
                selectinload(Imovel.vinculos).selectinload(Vinculo.pessoa)
            )
        )

        result = await session.execute(query)
        imovel = result.scalar_one_or_none()

        if not imovel:
            return None

        proprietarios = [
            ProprietarioResponse(
                nome_completo=vinculo.pessoa.nome_completo,
                cpf=self.anonymizer.anonymize(vinculo.pessoa.cpf),
                vinculo=vinculo.tipo_vinculo,
                participacao_pct=vinculo.participacao_pct
            )
            for vinculo in imovel.vinculos
        ]

        return ImovelResponse(
            codigo_incra=imovel.codigo_incra,
            nome_imovel=imovel.nome_imovel,
            uf=imovel.uf,
            municipio=imovel.municipio,
            area_ha=imovel.area_ha,
            situacao=imovel.situacao,
            proprietarios=proprietarios
        )
