import psycopg2
from psycopg2.extras import execute_values
from contextlib import contextmanager
from typing import List

from loader.config.settings import db_settings
from loader.domain.entities import Imovel, Pessoa, Vinculo
from loader.domain.repositories import ImovelRepository, PessoaRepository, VinculoRepository


class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class PostgresImovelRepository(ImovelRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db

    async def upsert(self, imovel: Imovel) -> int:
        query = """
            INSERT INTO imoveis (codigo_incra, nome_imovel, uf, municipio, area_ha, situacao, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (codigo_incra)
            DO UPDATE SET
                nome_imovel = EXCLUDED.nome_imovel,
                uf = EXCLUDED.uf,
                municipio = EXCLUDED.municipio,
                area_ha = EXCLUDED.area_ha,
                situacao = EXCLUDED.situacao,
                updated_at = NOW()
            RETURNING id
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (pessoa.cpf, pessoa.nome_completo))
                result = cursor.fetchone()
                return result[0] if result else 0


class PostgresVinculoRepository(VinculoRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db

    async def upsert_batch(self, vinculos: List[Vinculo]) -> None:
        if not vinculos:
            return

        query = """
            INSERT INTO vinculos (imovel_id, pessoa_id, tipo_vinculo, participacao_pct)
            SELECT
                (SELECT id FROM imoveis WHERE codigo_incra = data.codigo_incra),
                (SELECT id FROM pessoas WHERE cpf = data.cpf),
                data.tipo_vinculo,
                data.participacao_pct
            FROM (VALUES %s) AS data(codigo_incra, cpf, tipo_vinculo, participacao_pct)
            ON CONFLICT (imovel_id, pessoa_id, tipo_vinculo)
            DO UPDATE SET
                participacao_pct = EXCLUDED.participacao_pct
