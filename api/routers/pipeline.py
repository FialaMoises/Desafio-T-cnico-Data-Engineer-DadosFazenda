import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import os

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class PipelineRequest(BaseModel):
    estados: list[str]


class PipelineStatus(BaseModel):
    running: bool
    current_step: str | None
    estados: list[str]


pipeline_state = {
    "running": False,
    "current_step": None,
    "estados": []
}


async def log_stream(estados: list[str]) -> AsyncGenerator[str, None]:
    try:
        pipeline_state["running"] = True
        pipeline_state["estados"] = estados

        pipeline_state["current_step"] = "extração"
        estados_str = ', '.join(estados)
        yield f"data: {json.dumps({'type': 'info', 'message': f'Iniciando extração dos estados: {estados_str}', 'timestamp': datetime.now().isoformat()})}\n\n"

        cmd = ["python", "-m", "extractor.main", "--ufs"] + estados
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            line = line.strip()
            if line:
                yield f"data: {json.dumps({'type': 'log', 'message': line, 'step': 'extração', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.01)

        process.wait()

        if process.returncode != 0:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Erro na extração (código {process.returncode})', 'timestamp': datetime.now().isoformat()})}\n\n"
            pipeline_state["running"] = False
            return

        yield f"data: {json.dumps({'type': 'success', 'message': 'Extração concluída com sucesso!', 'step': 'extração', 'timestamp': datetime.now().isoformat()})}\n\n"
        await asyncio.sleep(1)

        pipeline_state["current_step"] = "carregamento"
        yield f"data: {json.dumps({'type': 'info', 'message': 'Iniciando carregamento dos dados no PostgreSQL...', 'timestamp': datetime.now().isoformat()})}\n\n"

        cmd = ["python", "-m", "loader.main"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )

        for line in process.stdout:
            line = line.strip()
            if line:
                yield f"data: {json.dumps({'type': 'log', 'message': line, 'step': 'carregamento', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(0.01)

        process.wait()

        if process.returncode != 0:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Erro no carregamento (código {process.returncode})', 'timestamp': datetime.now().isoformat()})}\n\n"
            pipeline_state["running"] = False
            return

        yield f"data: {json.dumps({'type': 'success', 'message': 'Carregamento concluído com sucesso!', 'step': 'carregamento', 'timestamp': datetime.now().isoformat()})}\n\n"
        await asyncio.sleep(1)

        pipeline_state["current_step"] = "concluído"
        yield f"data: {json.dumps({'type': 'complete', 'message': 'Pipeline executado com sucesso! 🎉', 'timestamp': datetime.now().isoformat()})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Erro inesperado: {str(e)}', 'timestamp': datetime.now().isoformat()})}\n\n"

    finally:
        pipeline_state["running"] = False
        pipeline_state["current_step"] = None


@router.get("/run", response_class=StreamingResponse)
async def run_pipeline(estados: str):
    if pipeline_state["running"]:
        raise HTTPException(
            status_code=409,
            detail="Pipeline já está em execução. Aguarde a conclusão."
        )

    estados_list = [e.strip().upper() for e in estados.split(",") if e.strip()]

    if not estados_list:
        raise HTTPException(
            status_code=400,
            detail="Lista de estados não pode ser vazia."
        )

    estados_validos = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
                       "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
                       "RS", "RO", "RR", "SC", "SP", "SE", "TO"}

    for estado in estados_list:
        if estado not in estados_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido: {estado}. Estados válidos: {', '.join(sorted(estados_validos))}"
            )

    return StreamingResponse(
        log_stream(estados_list),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status", response_model=PipelineStatus)
async def get_pipeline_status():
    return PipelineStatus(
        running=pipeline_state["running"],
        current_step=pipeline_state["current_step"],
        estados=pipeline_state["estados"]
    )
