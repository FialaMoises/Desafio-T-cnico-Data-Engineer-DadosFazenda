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

    @staticmethod
    def extract_uf_from_municipio(codigo_incra: str) -> str:
        if not codigo_incra or len(codigo_incra) < 2:
            return "XX"
        codigo_uf = codigo_incra[:2]
        uf_map = {
            "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
            "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
            "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE",
            "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
            "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
            "52": "GO", "53": "DF"
        }
        return uf_map.get(codigo_uf, "XX")

    def transform_imovel(self, row: Dict[str, str]) -> Imovel:
        codigo_incra = row.get("codigo_incra", "").strip()
        return Imovel(
            codigo_incra=codigo_incra,
            nome_imovel=row.get("denominacao") or None,
            uf=self.extract_uf_from_municipio(codigo_incra),
            municipio=row.get("municipio", "").strip(),
            area_ha=None,
            situacao="Ativo"
        )

    def transform_pessoa(self, row: Dict[str, str]) -> Pessoa | None:
        cpf = self.clean_cpf(row.get("matricula", ""))
        nome = row.get("proprietario", "").strip()

        if not cpf or not nome:
            return None

        return Pessoa(cpf=cpf, nome_completo=nome)

    def transform_vinculo(self, row: Dict[str, str]) -> Vinculo | None:
        codigo_incra = row.get("codigo_incra", "").strip()
        cpf = self.clean_cpf(row.get("matricula", ""))

        if not codigo_incra or not cpf:
            return None

        return Vinculo(
            codigo_incra=codigo_incra,
            cpf=cpf,
            tipo_vinculo="Proprietário",
            participacao_pct=self.parse_decimal(row.get("pct_obtencao", ""))
        )
