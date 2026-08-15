from dataclasses import dataclass

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    title: str
    content: str
    score: float


class RAGService:
    def __init__(self, engine: AsyncEngine, client: AsyncOpenAI, settings: Settings) -> None:
        self.engine = engine
        self.client = client
        self.settings = settings

    async def _embed(self, value: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=value,
        )
        return response.data[0].embedding

    async def retrieve(self, question: str) -> list[RetrievedChunk]:
        embedding = await self._embed(question)
        query = text(
            """
            SELECT document_id::text, title, content,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS score
            FROM document_chunks
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """
        )
        async with self.engine.connect() as connection:
            rows = (
                await connection.execute(
                    query,
                    {"embedding": str(embedding), "limit": self.settings.rag_top_k},
                )
            ).mappings().all()
        return [RetrievedChunk(**row) for row in rows]

    async def answer(self, question: str) -> dict:
        chunks = await self.retrieve(question)
        context = "\n\n".join(
            f"SOURCE {index}: {chunk.title}\n{chunk.content}"
            for index, chunk in enumerate(chunks, start=1)
        )
        response = await self.client.responses.create(
            model=self.settings.openai_chat_model,
            input=(
                "You are an internal operations assistant. Answer only from the supplied sources. "
                "If the sources are insufficient, say so. Cite claims with [SOURCE n].\n\n"
                f"Question: {question}\n\nSources:\n{context}"
            ),
        )
        return {
            "answer": response.output_text,
            "sources": [
                {
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "score": round(chunk.score, 4),
                }
                for chunk in chunks
            ],
        }
