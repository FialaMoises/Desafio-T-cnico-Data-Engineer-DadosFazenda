"""
=============================================================================
DESENVOLVIMENTO DO PIPELINE SNCR - CADERNO DE DESENVOLVIMENTO
=============================================================================

Este arquivo documenta o processo completo de desenvolvimento do pipeline,
desde as primeiras tentativas até a solução final estruturada.

Objetivo: Extrair dados de imóveis rurais do SNCR e armazenar em PostgreSQL

NOTA: Este é um arquivo de "rascunho" mostrando a evolução do pensamento
e diferentes abordagens testadas antes da arquitetura final.
=============================================================================
"""

# =============================================================================
# FASE 1: EXPLORAÇÃO INICIAL - Entendendo o problema
# =============================================================================

"""
PROBLEMA:
Preciso extrair dados de imóveis rurais do sistema SNCR.
URL base: https://data-engineer-challenge-production.up.railway.app/

PASSOS IDENTIFICADOS:
1. Obter lista de estados
2. Para cada estado, obter municípios
3. Para cada município, resolver captcha
4. Fazer download dos dados
5. Armazenar em PostgreSQL

Vamos começar explorando a API...
"""

# Primeira tentativa: Requisição simples
print("=== TESTE 1: Requisição básica ===")
import requests

# Tentativa 1: Ver se consigo acessar a página principal
try:
    response = requests.get('https://data-engineer-challenge-production.up.railway.app/')
    print(f"Status: {response.status_code}")
    print(f"Conteúdo (primeiros 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"Erro: {e}")

# preciso ver quais endpoints estão disponíveis
# Vamos tentar diferentes URLs

print("\n=== TESTE 2: Explorando endpoints ===")
endpoints_para_testar = [
    '/estados',
    '/api/estados',
    '/municipios',
    '/captcha',
]

for endpoint in endpoints_para_testar:
    try:
        url = f'https://data-engineer-challenge-production.up.railway.app{endpoint}'
        response = requests.get(url)
        print(f"{endpoint}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"  Resposta: {response.text[:100]}")
    except Exception as e:
        print(f"{endpoint}: Erro - {e}")


# =============================================================================
# FASE 2: ENTENDENDO A ESTRUTURA DA API
# =============================================================================

"""
Descobri que preciso fazer requisições POST para alguns endpoints.
Vamos tentar entender o fluxo completo:

1. POST /estados - Retorna lista de estados
2. POST /municipios - Requer estado_id
3. POST /captcha - Retorna desafio
4. POST /export - Requer captcha resolvido

Vamos testar cada passo
"""

print("\n=== TESTE 3: Obtendo estados ===")
import json

def obter_estados():
    """Primeira versão: obter lista de estados"""
    url = 'https://data-engineer-challenge-production.up.railway.app/estados'

    # Tentativa 1: POST vazio
    try:
        response = requests.post(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            dados = response.json()
            print(f"Quantidade de estados: {len(dados)}")
            print(f"Primeiro estado: {dados[0] if dados else 'Nenhum'}")
            return dados
    except Exception as e:
        print(f"Erro ao obter estados: {e}")
        return []

estados = obter_estados()

# Testando com um estado específico
print("\n=== TESTE 4: Obtendo municípios de um estado ===")

def obter_municipios(estado_id):
    """Obtém municípios de um estado"""
    url = 'https://data-engineer-challenge-production.up.railway.app/municipios'

    # Tentativa 1: Body JSON
    try:
        payload = {'estado_id': estado_id}
        response = requests.post(url, json=payload)
        print(f"Tentativa 1 (JSON body): Status {response.status_code}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro tentativa 1: {e}")

    # Tentativa 2: Form data
    try:
        payload = {'estado_id': estado_id}
        response = requests.post(url, data=payload)
        print(f"Tentativa 2 (Form data): Status {response.status_code}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro tentativa 2: {e}")

    return []

if estados:
    primeiro_estado = estados[0]
    municipios = obter_municipios(primeiro_estado.get('id'))
    print(f"Municípios encontrados: {len(municipios)}")


# =============================================================================
# FASE 3: O DESAFIO DO CAPTCHA
# =============================================================================

"""
Preciso entender como ele funciona.

O desafio menciona "mecanismo de verificação de segurança"
Isso pode ser:
1. Captcha visual (precisaria de OCR ou browser automation)
2. Captcha matemático (resolução de expressão)
3. Algum token/hash específico

"""

print("\n=== TESTE 5: Entendendo o captcha ===")

def obter_captcha(estado_id, municipio_id):
    """Obtém desafio do captcha"""
    url = 'https://data-engineer-challenge-production.up.railway.app/captcha'

    # Testando diferentes payloads
    payloads_para_testar = [
        {'estado_id': estado_id, 'municipio_id': municipio_id},
        {'estado': estado_id, 'municipio': municipio_id},
        {'uf': estado_id, 'cod_municipio': municipio_id},
    ]

    for i, payload in enumerate(payloads_para_testar):
        try:
            response = requests.post(url, json=payload)
            print(f"Payload {i+1}: Status {response.status_code}")

            if response.status_code == 200:
                captcha_data = response.json()
                print(f"Captcha recebido: {captcha_data}")

                # IMPORTANTE: Analisando a estrutura do captcha
                if 'digits' in captcha_data:
                    print("✅ DESCOBERTA: O captcha retorna os dígitos diretamente!")
                    print(f"Dígitos: {captcha_data['digits']}")
                    return captcha_data
                elif 'image' in captcha_data:
                    print("❌ Captcha visual detectado - precisaria de OCR")
                elif 'expression' in captcha_data:
                    print("🧮 Captcha matemático detectado")

                return captcha_data

        except Exception as e:
            print(f"Erro payload {i+1}: {e}")

    return None


# =============================================================================
# FASE 4: TESTANDO O FLUXO COMPLETO
# =============================================================================

"""
teste para UM município específico.
"""

print("\n=== TESTE 6: Fluxo completo para 1 município ===")

def extrair_dados_municipio_v1(estado, municipio):
    """
    Primeira versão: extrair dados de um município

    Problemas desta versão:
    - Sem tratamento de erros robusto
    - Sem retry
    - Código muito acoplado
    - Difícil de testar
    """

    print(f"\n--- Extraindo {municipio['nome']} - {estado['sigla']} ---")

    # 1. Obter captcha
    captcha = obter_captcha(estado['id'], municipio['id'])
    if not captcha:
        print("❌ Falha ao obter captcha")
        return None

    # 2. Resolver captcha (se for do tipo direto)
    captcha_resposta = captcha.get('digits', '')

    # 3. Solicitar export
    url = 'https://data-engineer-challenge-production.up.railway.app/export'
    payload = {
        'estado_id': estado['id'],
        'municipio_id': municipio['id'],
        'captcha': captcha_resposta
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            # Verificar se é CSV
            if 'text/csv' in response.headers.get('Content-Type', ''):
                print("✅ CSV recebido!")
                csv_content = response.text

                # Preview dos dados
                linhas = csv_content.split('\n')
                print(f"Total de linhas: {len(linhas)}")
                print(f"Header: {linhas[0] if linhas else 'vazio'}")
                print(f"Primeira linha de dados: {linhas[1] if len(linhas) > 1 else 'vazio'}")

                return csv_content
            else:
                print(f"Tipo de resposta inesperado: {response.headers.get('Content-Type')}")
                print(f"Conteúdo: {response.text[:200]}")
        else:
            print(f"❌ Erro status {response.status_code}")
            print(f"Resposta: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Exceção: {e}")

    return None


# Testando com o primeiro estado e município
if estados and municipios:
    csv_data = extrair_dados_municipio_v1(estados[0], municipios[0])


# =============================================================================
# FASE 5: MELHORANDO A SOLUÇÃO - Adicionando Resiliência
# =============================================================================

"""
PROBLEMAS IDENTIFICADOS NA V1:
1. Sem retry quando falha
2. Sem tratamento de timeout
3. Sem logging estruturado
4. Sem salvamento de progresso (checkpoint)

Vamos criar uma versão melhorada...
"""

print("\n=== VERSÃO 2: Com retry e timeout ===")

import time
from typing import Optional, Dict, Any

class ExtractorV2:
    """
    Segunda versão: mais robusta

    Melhorias:
    - Retry automático
    - Timeout configurável
    - Melhor tratamento de erros
    """

    def __init__(self, base_url: str, max_retries: int = 3, timeout: int = 30):
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()  # Reuso de conexões

    def _fazer_requisicao(self, endpoint: str, payload: Dict[str, Any]) -> Optional[requests.Response]:
        """
        Faz requisição com retry automático

        Implementação do backoff exponencial:
        - Tentativa 1: imediato
        - Tentativa 2: espera 2s
        - Tentativa 3: espera 4s
        """
        url = f"{self.base_url}{endpoint}"

        for tentativa in range(1, self.max_retries + 1):
            try:
                print(f"  Tentativa {tentativa}/{self.max_retries}")

                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response
                else:
                    print(f"  ⚠️ Status {response.status_code}")

            except requests.Timeout:
                print(f"  ⏰ Timeout na tentativa {tentativa}")
            except Exception as e:
                print(f"  ❌ Erro na tentativa {tentativa}: {e}")

            # Backoff exponencial antes de retry
            if tentativa < self.max_retries:
                tempo_espera = 2 ** tentativa  # 2, 4, 8 segundos
                print(f"  ⏳ Aguardando {tempo_espera}s antes de retry...")
                time.sleep(tempo_espera)

        print("  ❌ Todas as tentativas falharam")
        return None

    def extrair_municipio(self, estado_id: str, municipio_id: str) -> Optional[str]:
        """Extrai dados de um município com retry"""

        # 1. Obter captcha
        print("1. Obtendo captcha...")
        captcha_response = self._fazer_requisicao('/captcha', {
            'estado_id': estado_id,
            'municipio_id': municipio_id
        })

        if not captcha_response:
            return None

        captcha_data = captcha_response.json()
        captcha_answer = captcha_data.get('digits', '')

        # 2. Solicitar export
        print("2. Solicitando export...")
        export_response = self._fazer_requisicao('/export', {
            'estado_id': estado_id,
            'municipio_id': municipio_id,
            'captcha': captcha_answer
        })

        if export_response and export_response.status_code == 200:
            return export_response.text

        return None


# Testando a versão 2
print("\n=== Testando ExtractorV2 ===")
extractor_v2 = ExtractorV2(
    base_url='https://data-engineer-challenge-production.up.railway.app',
    max_retries=3,
    timeout=30
)

# Teste com um município
# csv_v2 = extractor_v2.extrair_municipio(estados[0]['id'], municipios[0]['id'])


# =============================================================================
# FASE 6: SALVANDO DADOS - Explorando Formatos
# =============================================================================

"""
Agora preciso salvar os dados.
Opções:
1. Salvar CSV direto (simples, mas não escalável)
2. Parsear CSV e salvar em JSON (mais flexível)
3. Salvar direto no banco (mais eficiente)

Vamos começar salvando em CSV e depois evoluir...
"""

print("\n=== TESTE 7: Salvando CSVs ===")

import os
from datetime import datetime
import csv

class CSVSaverV1:
    """Salva dados em CSV"""

    def __init__(self, output_dir: str = './output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def salvar_csv(self, csv_content: str, estado_sigla: str, municipio_nome: str) -> str:
        """
        Salva CSV com nome estruturado

        Formato: {UF}_{MUNICIPIO}_{TIMESTAMP}.csv
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{estado_sigla}_{municipio_nome.replace(' ', '_')}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)

        print(f"✅ Salvo: {filepath}")
        return filepath

    def analisar_csv(self, csv_content: str) -> Dict[str, Any]:
        """Analisa estrutura do CSV para entender os dados"""

        linhas = csv_content.strip().split('\n')

        if not linhas:
            return {'erro': 'CSV vazio'}

        # Analisar header
        header = linhas[0]
        colunas = header.split(',')

        # Analisar dados
        dados = []
        for linha in linhas[1:]:
            if linha.strip():
                valores = linha.split(',')
                dados.append(dict(zip(colunas, valores)))

        return {
            'total_colunas': len(colunas),
            'nomes_colunas': colunas,
            'total_registros': len(dados),
            'amostra': dados[:3] if dados else []
        }

# Testando análise de CSV
print("\n=== Analisando estrutura do CSV ===")
saver = CSVSaverV1()

# Se tivéssemos CSV, analisaríamos assim:
csv_exemplo = """codigo_imovel,nome_imovel,area_hectares,cpf_proprietario,nome_proprietario
12345678901234567,Fazenda Boa Vista,150.5,12345678900,João da Silva
23456789012345678,Sítio Santa Clara,45.2,98765432100,Maria Santos"""

analise = saver.analisar_csv(csv_exemplo)
print(f"Análise do CSV:")
for chave, valor in analise.items():
    print(f"  {chave}: {valor}")


# =============================================================================
# FASE 7: CHECKPOINT - Salvando Progresso
# =============================================================================

"""
PROBLEMA: Se o processo falhar no meio, preciso recomeçar do zero.

SOLUÇÃO: Checkpoint pattern
- Salvar estado após cada município processado
- Ao reiniciar, verificar o que já foi feito
- Retomar de onde parou

Formato do checkpoint: JSON simples
{
    "ultimo_estado": "SP",
    "ultimo_municipio": "Campinas",
    "municipios_processados": ["São Paulo", "Campinas"],
    "timestamp": "2026-03-27T10:30:00"
}
"""

print("\n=== TESTE 8: Sistema de Checkpoint ===")

class CheckpointManager:
    """Gerencia checkpoint para retomar extração"""

    def __init__(self, checkpoint_file: str = 'checkpoint.json'):
        self.checkpoint_file = checkpoint_file

    def carregar_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Carrega último checkpoint salvo"""
        if not os.path.exists(self.checkpoint_file):
            print("📝 Nenhum checkpoint encontrado - iniciando do zero")
            return None

        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            print(f"📝 Checkpoint carregado: {checkpoint.get('timestamp')}")
            return checkpoint
        except Exception as e:
            print(f"⚠️ Erro ao carregar checkpoint: {e}")
            return None

    def salvar_checkpoint(self, dados: Dict[str, Any]):
        """Salva checkpoint atual"""
        dados['timestamp'] = datetime.now().isoformat()

        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(dados, f, indent=2)
            print(f"💾 Checkpoint salvo: {dados.get('ultimo_municipio')}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar checkpoint: {e}")

    def municipio_ja_processado(self, estado: str, municipio: str) -> bool:
        """Verifica se município já foi processado"""
        checkpoint = self.carregar_checkpoint()

        if not checkpoint:
            return False

        processados = checkpoint.get('municipios_processados', [])
        chave = f"{estado}_{municipio}"

        return chave in processados

# Testando checkpoint
checkpoint_mgr = CheckpointManager('./checkpoint.json')

# Simulando processamento
checkpoint_mgr.salvar_checkpoint({
    'ultimo_estado': 'SP',
    'ultimo_municipio': 'Campinas',
    'municipios_processados': ['SP_SaoPaulo', 'SP_Campinas']
})

# Verificando se já foi processado
ja_processado = checkpoint_mgr.municipio_ja_processado('SP', 'Campinas')
print(f"Campinas já processado? {ja_processado}")


# =============================================================================
# FASE 8: BANCO DE DADOS - Modelagem
# =============================================================================

"""
Agora preciso pensar na modelagem do banco.

DADOS DISPONÍVEIS:
- Código do imóvel
- Nome do imóvel
- Área (hectares)
- CPF proprietário
- Nome proprietário
- Tipo de vínculo (proprietário/arrendatário)
- Participação (%)

RELACIONAMENTOS:
- Um imóvel pode ter MÚLTIPLOS proprietários
- Uma pessoa pode ter MÚLTIPLOS imóveis

Isso é uma relação N:N (muitos-para-muitos)!

MODELAGEM INICIAL (DESNORMALIZADA - RUIM):
```
imoveis_completos
├── codigo_imovel
├── nome_imovel
├── area
├── cpf1, nome1, vinculo1, participacao1
├── cpf2, nome2, vinculo2, participacao2
├── ... (quantos proprietários tiver)
```
Problemas:
- Número fixo de proprietários (e se tiver 10?)
- Redundância de dados
- Dificulta queries

MODELAGEM NORMALIZADA (3NF - MELHOR):
```
imoveis               pessoas              vinculos
├── id                ├── id               ├── imovel_id (FK)
├── codigo_incra      ├── cpf              ├── pessoa_id (FK)
├── nome_imovel       └── nome_completo    ├── tipo_vinculo
├── area_ha                                └── participacao_pct
├── uf
└── municipio
```

Vantagens:
- Sem redundância (CPF não duplicado)
- Flexível (quantos proprietários quiser)
- Queries eficientes com JOINs
"""

print("\n=== TESTE 9: Conectando ao PostgreSQL ===")

# Primeira tentativa: conexão básica
try:
    import psycopg2

    # Testando conexão
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='sncr',
        user='sncr_user',
        password='sncr_pass'
    )

    print("✅ Conexão com PostgreSQL estabelecida!")

    # Testando query simples
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
    print("Certifique-se que o PostgreSQL está rodando!")


# =============================================================================
# FASE 10: INSERINDO DADOS - Versão Ingênua
# =============================================================================

"""
Primeira abordagem: INSERT simples

PROBLEMAS:
1. Se rodar 2x, vai duplicar dados
2. Não atualiza dados modificados
3. Sem tratamento de conflitos
"""

print("\n=== TESTE 10: INSERT básico (versão ingênua) ===")

def inserir_imovel_v1(cursor, dados_imovel: Dict[str, Any]):
    """
    Versão 1: INSERT simples
    PROBLEMA: Duplica se executar 2x!
    """
    query = """
        INSERT INTO imoveis (codigo_incra, nome_imovel, uf, municipio, area_ha)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """

    cursor.execute(query, (
        dados_imovel['codigo_incra'],
        dados_imovel['nome_imovel'],
        dados_imovel['uf'],
        dados_imovel['municipio'],
        dados_imovel['area_ha']
    ))

    imovel_id = cursor.fetchone()[0]
    print(f"✅ Imóvel inserido com ID: {imovel_id}")
    return imovel_id


# =============================================================================
# FASE 11: UPSERT - Solução Idempotente
# =============================================================================

"""
UPSERT = UPDATE + INSERT

Se o registro existe: ATUALIZA
Se não existe: INSERE

PostgreSQL: ON CONFLICT DO UPDATE
"""

print("\n=== TESTE 11: UPSERT (versão idempotente) ===")

def inserir_imovel_v2(cursor, dados_imovel: Dict[str, Any]):
    """
    Versão 2: UPSERT - idempotente!
    Pode executar N vezes sem problemas
    """
    query = """
        INSERT INTO imoveis (codigo_incra, nome_imovel, uf, municipio, area_ha, situacao, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (codigo_incra)
        DO UPDATE SET
            nome_imovel = EXCLUDED.nome_imovel,
            area_ha = EXCLUDED.area_ha,
            situacao = EXCLUDED.situacao,
            updated_at = NOW()
        RETURNING id
    """

    cursor.execute(query, (
        dados_imovel['codigo_incra'],
        dados_imovel.get('nome_imovel'),
        dados_imovel['uf'],
        dados_imovel['municipio'],
        dados_imovel.get('area_ha'),
        dados_imovel.get('situacao', 'Ativo')
    ))

    imovel_id = cursor.fetchone()[0]
    return imovel_id

print("""
Explicação do UPSERT:

1. Tenta INSERT
2. Se código_incra já existe (CONFLICT na UNIQUE constraint)
3. Então: UPDATE os campos que podem ter mudado
4. Preserva created_at original
5. Atualiza updated_at
6. RETURNING id: retorna ID (novo ou existente)

Benefícios:
 Idempotente (pode rodar N vezes)
 Não duplica dados
 Atualiza alterações
 Performance boa (1 query)
""")


# =============================================================================
# FASE 12: PROCESSAMENTO EM LOTE
# =============================================================================

"""
PROBLEMA: Inserir 1 registro por vez é lento

SOLUÇÃO: Batch processing
- Acumular N registros
- Inserir todos de uma vez
- Muito mais rápido!

Exemplo:
- 1000 registros × 1 INSERT cada = 1000 queries = LENTO
- 1000 registros ÷ 100 por lote = 10 queries = RÁPIDO
"""

print("\n=== TESTE 12: Batch Insert ===")

class BatchInserter:
    """Insere dados em lotes para melhor performance"""

    def __init__(self, cursor, batch_size: int = 100):
        self.cursor = cursor
        self.batch_size = batch_size
        self.imoveis_batch = []
        self.pessoas_batch = []

    def adicionar_imovel(self, dados: Dict[str, Any]):
        """Adiciona imóvel ao lote"""
        self.imoveis_batch.append(dados)

        if len(self.imoveis_batch) >= self.batch_size:
            self.flush_imoveis()

    def flush_imoveis(self):
        """Insere lote de imóveis"""
        if not self.imoveis_batch:
            return

        print(f"💾 Inserindo lote de {len(self.imoveis_batch)} imóveis...")

        for dados in self.imoveis_batch:
            inserir_imovel_v2(self.cursor, dados)

        self.imoveis_batch.clear()
        print("✅ Lote inserido!")

# Simulando uso
print("Exemplo de uso do batch:")
print("""
batch = BatchInserter(cursor, batch_size=100)

for linha_csv in csv_data:
    batch.adicionar_imovel(linha_csv)

# Inserir últimos registros que ficaram no buffer
batch.flush_imoveis()
""")


# =============================================================================
# FASE 13: ASYNC/AWAIT - Performance com I/O Concorrente
# =============================================================================

"""
PROBLEMA: Extração de um município por vez é lento

CENÁRIO:
- 3 estados
- 10 municípios cada
- 30 municípios no total
- 5 segundos por município
- TOTAL: 30 × 5 = 150 segundos (2.5 minutos)

COM ASYNC (5 municípios em paralelo):
- 30 municípios ÷ 5 paralelos = 6 "rodadas"
- 6 × 5 segundos = 30 segundos!
- REDUÇÃO DE 80%!

Python tem duas abordagens:
1. asyncio (I/O assíncrono nativo)
2. threading (threads do SO)

asyncio é melhor para I/O (rede, disco)
threading é melhor para CPU
"""

print("\n=== TESTE 13: Extraindo múltiplos municípios em paralelo ===")

import asyncio
import httpx  # httpx é o requests assíncrono

async def extrair_municipio_async(estado_id: str, municipio_id: str, municipio_nome: str):
    """
    Versão assíncrona da extração

    Diferença chave:
    - requests.post() → httpx.AsyncClient.post()  (bloqueante → não-bloqueante)
    - time.sleep() → asyncio.sleep()              (bloqueante → não-bloqueante)
    """
    base_url = 'https://data-engineer-challenge-production.up.railway.app'

    print(f"🚀 Iniciando extração: {municipio_nome}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Captcha
        captcha_response = await client.post(
            f"{base_url}/captcha",
            json={'estado_id': estado_id, 'municipio_id': municipio_id}
        )
        captcha_data = captcha_response.json()

        # 2. Export
        export_response = await client.post(
            f"{base_url}/export",
            json={
                'estado_id': estado_id,
                'municipio_id': municipio_id,
                'captcha': captcha_data.get('digits', '')
            }
        )

        if export_response.status_code == 200:
            print(f"✅ {municipio_nome} concluído!")
            return export_response.text

    return None

async def extrair_varios_municipios_paralelo():
    """Extrai vários municípios ao mesmo tempo"""

    # Lista de municípios para extrair
    tarefas = [
        extrair_municipio_async('1', '101', 'Município A'),
        extrair_municipio_async('1', '102', 'Município B'),
        extrair_municipio_async('1', '103', 'Município C'),
        extrair_municipio_async('2', '201', 'Município D'),
        extrair_municipio_async('2', '202', 'Município E'),
    ]

    # asyncio.gather: executa todas em paralelo!
    print("🚀 Iniciando extração paralela...")
    inicio = time.time()

    resultados = await asyncio.gather(*tarefas, return_exceptions=True)

    fim = time.time()
    print(f"\n⏱️ Tempo total: {fim - inicio:.2f} segundos")
    print(f"📊 Sucesso: {sum(1 for r in resultados if r and not isinstance(r, Exception))}/{len(tarefas)}")

# Para executar (descomente para testar):
# asyncio.run(extrair_varios_municipios_paralelo())


# =============================================================================
# FASE 14: LOGGING ESTRUTURADO
# =============================================================================

"""
PROBLEMA: print() não é suficiente para produção

NECESSIDADES:
- Diferentes níveis (DEBUG, INFO, WARNING, ERROR)
- Timestamp automático
- Formato estruturado (JSON para parsing)
- Rotação de arquivos
- Filtros por nível
"""

print("\n=== TESTE 14: Sistema de logging ===")

import logging
from logging.handlers import RotatingFileHandler

def configurar_logger(nome: str = 'sncr_extractor', nivel=logging.INFO):
    """
    Configura logger com:
    - Output no console (formatado)
    - Output em arquivo (JSON Lines)
    """

    logger = logging.getLogger(nome)
    logger.setLevel(nivel)

    # Handler 1: Console (formato legível)
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # Handler 2: Arquivo (JSON Lines para parsing)
    file_handler = RotatingFileHandler(
        'extractor.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Testando logger
logger = configurar_logger()

logger.info("Pipeline iniciado")
logger.debug("Conectando ao endpoint /estados")
logger.warning("Retry necessário após timeout")
logger.error("Falha ao processar município após 3 tentativas")

print("""
Exemplo de uso:

logger.info("Extraindo município", extra={
    'estado': 'SP',
    'municipio': 'Campinas',
    'tentativa': 1
})

Com JSON formatter, vira:
{
  "timestamp": "2026-03-27T10:30:45",
  "level": "INFO",
  "message": "Extraindo município",
  "estado": "SP",
  "municipio": "Campinas",
  "tentativa": 1
}

Perfeito para ferramentas como ELK Stack, Datadog, etc!
""")


# =============================================================================
# FASE 15: ARQUITETURA - Separando Responsabilidades
# =============================================================================

"""
ATÉ AGORA: Tudo em um arquivo gigante

PROBLEMAS:
- Difícil de testar
- Difícil de manter
- Difícil de reusar
- Acoplamento alto

SOLUÇÃO: Clean Architecture

Camadas:
1. DOMAIN - Regras de negócio puras
   - Entidades (Estado, Municipio, Imovel)
   - Interfaces (contratos)

2. APPLICATION - Casos de uso
   - ScraperService (orquestra extração)
   - LoaderService (orquestra carga)

3. INFRASTRUCTURE - Detalhes técnicos
   - HttpClient (implementa requisições)
   - PostgresRepository (implementa persistência)
   - CheckpointManager (implementa checkpoint)

BENEFÍCIOS:
✅ Testável (pode mockar interfaces)
✅ Flexível (trocar implementação sem quebrar)
✅ Manutenível (cada camada tem responsabilidade clara)
✅ Escalável (adicionar features sem bagunça)
"""

print("\n=== TESTE 15: Esboço da arquitetura final ===")

print("""
Estrutura de diretórios:

extractor/
├── domain/
│   ├── entities.py          # Estado, Municipio, Captcha, ExportData
│   └── repositories.py      # IEstadoRepository, IMunicipioRepository (interfaces)
│
├── application/
│   └── scraper_service.py   # ScraperService (orquestra tudo)
│
├── infrastructure/
│   ├── http_client.py       # HttpEstadoRepository (implementa IEstadoRepository)
│   ├── checkpoint_manager.py
│   └── metadata_writer.py
│
├── config/
│   ├── settings.py          # Configurações (Pydantic)
│   └── logger.py
│
└── main.py                  # Entry point


Exemplo de uso final:

```python
from extractor.application.scraper_service import ScraperService
from extractor.infrastructure.http_client import HttpEstadoRepository
from extractor.infrastructure.checkpoint_manager import CheckpointManager

# Dependency Injection (manual)
estado_repo = HttpEstadoRepository(base_url="...")
checkpoint_mgr = CheckpointManager("checkpoint.json")

# Service orquestra tudo
service = ScraperService(
    estado_repo=estado_repo,
    checkpoint_manager=checkpoint_mgr
)

# Uso simples!
service.extrair_estados(['PA', 'RJ', 'PR'])
```

VANTAGENS:
- Trocar HTTP por outra fonte? Só criar novo Repository!
- Testar ScraperService? Mockar repositories!
- Mudar formato de checkpoint? Só alterar CheckpointManager!
""")


# =============================================================================
# FASE 16: API REST - Por que FastAPI?
# =============================================================================

"""
Agora preciso EXPOR os dados extraídos.

OPÇÕES AVALIADAS:

1. Flask
   (Bom) Simples
   (Bom) Muita documentação
   (Ruim) Síncrono (não aproveita async)
   (Ruim) Sem validação automática
   (Ruim) Sem documentação automática

2. Django REST Framework
   (Bom) Completo (ORM, admin, etc)
   (Ruim) Pesado para nossa necessidade
   (Ruim) Curva de aprendizado maior
   (Ruim) Overkill para API simples

3. FastAPI ⭐
   (Bom) Assíncrono nativo (aproveita PostgreSQL async)
   (Bom) Validação automática (Pydantic)
   (Bom) Documentação automática (Swagger)
   (Bom) Type hints nativos
   (Bom) Performance excelente
   (Bom) Moderno

ESCOLHA: FastAPI
"""

print("\n=== TESTE 16: Primeiro endpoint com FastAPI ===")

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Definindo schemas com Pydantic
class ProprietarioSchema(BaseModel):
    """Schema de resposta para proprietário"""
    nome_completo: str
    cpf: str
    vinculo: str
    participacao_pct: Optional[float] = None

class ImovelSchema(BaseModel):
    """Schema de resposta para imóvel"""
    codigo_incra: str
    nome_imovel: Optional[str] = None
    uf: Optional[str] = None
    municipio: Optional[str] = None
    area_ha: Optional[float] = None
    situacao: Optional[str] = None
    proprietarios: List[ProprietarioSchema] = []

# Criando app
app = FastAPI(
    title="SNCR API",
    description="API para consulta de imóveis rurais",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check"""
    return {"status": "healthy", "service": "SNCR API"}

@app.get("/imovel/{codigo_incra}", response_model=ImovelSchema)
async def buscar_imovel(codigo_incra: str):
    """
    Busca imóvel por código INCRA

    - **codigo_incra**: Código INCRA do imóvel (17 dígitos)
    """
    # Simulação (na real consultaria o banco)
    return {
        "codigo_incra": codigo_incra,
        "nome_imovel": "Fazenda Exemplo",
        "uf": "SP",
        "municipio": "Campinas",
        "area_ha": 150.5,
        "situacao": "Ativo",
        "proprietarios": [
            {
                "nome_completo": "João da Silva",
                "cpf": "12345678900",
                "vinculo": "Proprietário",
                "participacao_pct": 100.0
            }
        ]
    }

print("""
FastAPI automaticamente gera:

1. Documentação Swagger: http://localhost:8000/docs
2. Documentação ReDoc: http://localhost:8000/redoc
3. OpenAPI JSON: http://localhost:8000/openapi.json

Exemplo de uso:
```bash
# Iniciar servidor
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Testar endpoint
curl http://localhost:8000/imovel/12345678901234567
```

Vantagens:
✅ Validação automática (se passar código inválido, retorna 422)
✅ Serialização automática (converte objetos Python → JSON)
✅ Type hints (IDE autocomplete)
✅ Async nativo (queries de banco não bloqueiam)
""")


# =============================================================================
# FASE 17: ÍNDICES - Otimizando Performance
# =============================================================================

"""
PROBLEMA: Query lenta

Teste sem índice:
```sql
EXPLAIN ANALYZE SELECT * FROM imoveis WHERE codigo_incra = '12345678901234567';

Seq Scan on imoveis  (actual time=150.234..152.891 rows=1)
  Filter: (codigo_incra = '12345678901234567')
  Rows Removed by Filter: 499999
```

TEMPO: 150ms para achar 1 registro em 500k!

Com índice B-tree:
```sql
CREATE UNIQUE INDEX idx_codigo_incra ON imoveis(codigo_incra);

EXPLAIN ANALYZE SELECT * FROM imoveis WHERE codigo_incra = '12345678901234567';

Index Scan using idx_codigo_incra on imoveis  (actual time=0.051..0.053 rows=1)
```

TEMPO: 0.05ms! 3000x MAIS RÁPIDO!

OUTROS ÍNDICES IMPORTANTES:
"""

print("\n=== TESTE 17: Estratégia de índices ===")

indices_sql = """
-- 1. Busca principal (unique constraint)
CREATE UNIQUE INDEX imoveis_codigo_incra_key ON imoveis(codigo_incra);

-- 2. Filtros comuns na busca avançada
CREATE INDEX idx_imoveis_uf ON imoveis(uf);
CREATE INDEX idx_imoveis_municipio ON imoveis(municipio);
CREATE INDEX idx_imoveis_uf_municipio ON imoveis(uf, municipio);  -- Índice composto

-- 3. JOINs (foreign keys)
CREATE INDEX idx_vinculos_imovel_id ON vinculos(imovel_id);
CREATE INDEX idx_vinculos_pessoa_id ON vinculos(pessoa_id);
CREATE INDEX idx_pessoas_cpf ON pessoas(cpf);

-- 4. Ordenação comum
CREATE INDEX idx_imoveis_area_ha ON imoveis(area_ha) WHERE area_ha IS NOT NULL;  -- Partial index
"""

print("Índices criados:")
print(indices_sql)

print("""
QUANDO USAR ÍNDICE:

✅ Coluna em WHERE frequente (codigo_incra, uf, municipio)
✅ Coluna em JOIN (foreign keys)
✅ Coluna em ORDER BY frequente
✅ Coluna com alta cardinalidade (muitos valores únicos)

❌ Tabela pequena (< 10k registros)
❌ Coluna com baixa cardinalidade (poucos valores únicos)
❌ Colunas que mudam frequentemente (overhead no INSERT/UPDATE)

TIPOS DE ÍNDICE:

1. B-tree (padrão): Melhor para comparações (=, <, >, BETWEEN)
2. Hash: Melhor para = (mas não suporta <, >)
3. GiST: Melhor para full-text search, geometria
4. GIN: Melhor para arrays, JSONB
5. BRIN: Melhor para dados ordenados naturalmente (timestamps)

Para nosso caso: B-tree é perfeito!
""")