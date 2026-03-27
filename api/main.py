from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import imovel, pipeline, search

app = FastAPI(
    title="SNCR API",
    description="API para consulta de dados do Sistema Nacional de Cadastro Rural",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imovel.router)
app.include_router(pipeline.router)
app.include_router(search.router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "SNCR API"}
