import asyncio
import json
from pathlib import Path

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.rag.service import RAGService


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    rag = RAGService(engine, AsyncOpenAI(api_key=settings.openai_api_key), settings)
    cases = json.loads(Path("evals/golden.json").read_text())

    retrieval_hits = 0
    answer_hits = 0

    for case in cases:
        result = await rag.answer(case["question"])
        titles = {source["title"] for source in result["sources"]}
        retrieval_hits += int(case["expected_source"] in titles)
        answer = result["answer"].lower()
        answer_hits += int(all(term.lower() in answer for term in case["required_terms"]))

    total = len(cases)
    print(
        json.dumps(
            {
                "cases": total,
                "retrieval_hit_rate": retrieval_hits / total,
                "required_term_coverage": answer_hits / total,
            },
            indent=2,
        )
    )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
