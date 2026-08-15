import asyncio
import uuid

from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings

DOCUMENTS = [
    {
        "title": "Checkout API SLO Runbook",
        "content": (
            "The checkout-api p95 latency SLO is 450ms. If latency exceeds the SLO for 10 minutes, "
            "check database saturation, upstream payment-provider latency, and recent deployments. "
            "For a sustained customer-impacting breach, open a SEV-2 incident and page the payments team."
        ),
    },
    {
        "title": "Incident Management Policy",
        "content": (
            "SEV-1 and SEV-2 incidents require an incident commander, a communications owner, an incident "
            "channel, and a written timeline. AI-generated incident records must remain drafts until a human approves them."
        ),
    },
]


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY,
                    document_id UUID NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536) NOT NULL
                )
                """
            )
        )

        for document in DOCUMENTS:
            embedding = (
                await client.embeddings.create(
                    model=settings.openai_embedding_model,
                    input=document["content"],
                )
            ).data[0].embedding
            await conn.execute(
                text(
                    """
                    INSERT INTO document_chunks (id, document_id, title, content, embedding)
                    VALUES (:id, :document_id, :title, :content, CAST(:embedding AS vector))
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "document_id": uuid.uuid4(),
                    "title": document["title"],
                    "content": document["content"],
                    "embedding": str(embedding),
                },
            )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
