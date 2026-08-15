from fastapi import Depends, FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from strawberry.fastapi import GraphQLRouter

from app.core.config import Settings, get_settings
from app.graphql.schema import schema
from app.rag.service import RAGService

app = FastAPI(title="OpsMind AI Platform", version="0.1.0")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


class AskRequest(BaseModel):
    question: str


def get_engine(settings: Settings = Depends(get_settings)) -> AsyncEngine:
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def get_rag_service(
    settings: Settings = Depends(get_settings),
    engine: AsyncEngine = Depends(get_engine),
) -> RAGService:
    return RAGService(engine=engine, client=AsyncOpenAI(api_key=settings.openai_api_key), settings=settings)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/ask")
async def ask(request: AskRequest, rag: RAGService = Depends(get_rag_service)) -> dict:
    return await rag.answer(request.question)
