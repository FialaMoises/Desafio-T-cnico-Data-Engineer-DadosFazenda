from decimal import Decimal, InvalidOperation
from typing import Dict, List
from loader.domain.entities import Imovel, Pessoa, Vinculo


class DataTransformer:
    @staticmethod
    def clean_cpf(cpf: str) -> str:
        return "".join(filter(str.isdigit, cpf))

    @staticmethod
    def parse_decimal(value: str) -> Decimal | None:
        if not value or value.strip() == "":
            return None
        try:
            cleaned = value.replace(",", ".")
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    def transform_imovel(self, row: Dict[str, str]) -> Imovel:
        return Imovel(
            codigo_incra=row.get("codigo_incra", "").strip(),
            nome_imovel=row.get("nome_imovel") or None,
            uf=row.get("uf", "").strip(),
            municipio=row.get("municipio", "").strip(),
            area_ha=self.parse_decimal(row.get("area_ha", "")),
            situacao=row.get("situacao") or None
        )

    def transform_pessoa(self, row: Dict[str, str]) -> Pessoa | None:
        cpf = self.clean_cpf(row.get("cpf", ""))
        nome = row.get("nome_completo", "").strip()

        if not cpf or not nome:
            return None

        return Pessoa(cpf=cpf, nome_completo=nome)

    def transform_vinculo(self, row: Dict[str, str]) -> Vinculo | None:
        codigo_incra = row.get("codigo_incra", "").strip()
        cpf = self.clean_cpf(row.get("cpf", ""))
        tipo_vinculo = row.get("tipo_vinculo", "").strip()

        if not codigo_incra or not cpf or not tipo_vinculo:
            return None

        return Vinculo(
            codigo_incra=codigo_incra,
            cpf=cpf,
            tipo_vinculo=tipo_vinculo,
            participacao_pct=self.parse_decimal(row.get("participacao_pct", ""))
        )
