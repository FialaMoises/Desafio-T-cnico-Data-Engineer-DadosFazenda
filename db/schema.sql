CREATE TABLE IF NOT EXISTS imoveis (
    id SERIAL PRIMARY KEY,
    codigo_incra VARCHAR(17) NOT NULL UNIQUE,
    nome_imovel TEXT,
    uf CHAR(2) NOT NULL,
    municipio TEXT NOT NULL,
    area_ha NUMERIC(12, 4),
    situacao TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pessoas (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    nome_completo TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vinculos (
    id SERIAL PRIMARY KEY,
    imovel_id INT NOT NULL REFERENCES imoveis(id) ON DELETE CASCADE,
    pessoa_id INT NOT NULL REFERENCES pessoas(id) ON DELETE CASCADE,
    tipo_vinculo TEXT NOT NULL CHECK (tipo_vinculo IN ('Proprietário', 'Arrendatário')),
    participacao_pct NUMERIC(5, 2) CHECK (participacao_pct >= 0 AND participacao_pct <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (imovel_id, pessoa_id, tipo_vinculo)
);

CREATE TABLE IF NOT EXISTS extracao_metadata (
    id SERIAL PRIMARY KEY,
    uf CHAR(2) NOT NULL,
    municipio TEXT NOT NULL,
    total_registros INT,
    extraido_em TIMESTAMPTZ NOT NULL,
    duracao_segundos NUMERIC(8, 2),
    status TEXT NOT NULL CHECK (status IN ('sucesso', 'erro')),
    erro TEXT,
    arquivo TEXT
);
