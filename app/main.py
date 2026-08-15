from __future__ import annotations

import json

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from strawberry.fastapi import GraphQLRouter

from app.core.config import Settings, get_settings
from app.graphql.schema import schema
from app.observability.telemetry import configure_tracing, tracer
from app.rag.service import RAGService
from app.security.prompt_guard import PromptGuard

settings = get_settings()
configure_tracing(endpoint=settings.otel_exporter_endpoint)
trace = tracer()

app = FastAPI(title="OpsMind AI Platform", version="0.2.0")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


class AskRequest(BaseModel):
    question: str


def get_engine(settings: Settings = Depends(get_settings)) -> AsyncEngine:
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def get_rag_service(
    settings: Settings = Depends(get_settings),
    engine: AsyncEngine = Depends(get_engine),
) -> RAGService:
    return RAGService(
        engine=engine,
        client=AsyncOpenAI(api_key=settings.openai_api_key),
        settings=settings,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0"}


@app.post("/api/v1/ask")
async def ask(request: AskRequest, rag: RAGService = Depends(get_rag_service)) -> dict:
    inspection = PromptGuard().inspect(request.question)
    if not inspection.allowed:
        return {"status": "blocked", "reason": inspection.reason}
    with trace.start_as_current_span("rag.answer"):
        return await rag.answer(request.question)


@app.post("/api/v1/ask/stream")
async def ask_stream(
    request: AskRequest,
    rag: RAGService = Depends(get_rag_service),
) -> StreamingResponse:
    inspection = PromptGuard().inspect(request.question)

    async def events():
        if not inspection.allowed:
            yield f"data: {json.dumps({'type': 'blocked', 'reason': inspection.reason})}\n\n"
            return
        with trace.start_as_current_span("rag.answer.stream"):
            result = await rag.answer(request.question)
        answer = result.get("answer", "")
        for token in answer.split():
            yield f"data: {json.dumps({'type': 'token', 'value': token + ' '})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'citations': result.get('citations', [])})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
