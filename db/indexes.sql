CREATE INDEX IF NOT EXISTS idx_imoveis_uf
ON imoveis(uf);

CREATE INDEX IF NOT EXISTS idx_imoveis_municipio
ON imoveis(municipio);

CREATE INDEX IF NOT EXISTS idx_imoveis_uf_municipio
ON imoveis(uf, municipio);

CREATE INDEX IF NOT EXISTS idx_vinculos_imovel_id
ON vinculos(imovel_id);

CREATE INDEX IF NOT EXISTS idx_vinculos_pessoa_id
ON vinculos(pessoa_id);

CREATE INDEX IF NOT EXISTS idx_pessoas_cpf
ON pessoas(cpf);

CREATE INDEX IF NOT EXISTS idx_extracao_metadata_uf_municipio
ON extracao_metadata(uf, municipio);
