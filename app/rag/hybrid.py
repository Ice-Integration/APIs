from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SearchHit:
    document_id: str
    title: str
    content: str
    score: float
    source: str
    acl_teams: frozenset[str] = frozenset()


class Retriever(Protocol):
    async def search(self, query: str, limit: int) -> list[SearchHit]: ...


def reciprocal_rank_fusion(
    result_sets: list[list[SearchHit]],
    limit: int = 8,
    k: int = 60,
) -> list[SearchHit]:
    scores: dict[str, float] = {}
    canonical: dict[str, SearchHit] = {}
    for results in result_sets:
        for rank, hit in enumerate(results, start=1):
            canonical[hit.document_id] = hit
            scores[hit.document_id] = scores.get(hit.document_id, 0.0) + 1 / (k + rank)
    ranked_ids = sorted(scores, key=scores.get, reverse=True)[:limit]
    return [
        SearchHit(**{**canonical[doc_id].__dict__, "score": scores[doc_id], "source": "hybrid"})
        for doc_id in ranked_ids
    ]


class HybridRetriever:
    """Combines semantic and lexical retrieval with reciprocal-rank fusion."""

    def __init__(self, semantic: Retriever, lexical: Retriever) -> None:
        self.semantic = semantic
        self.lexical = lexical

    async def search(self, query: str, limit: int = 8) -> list[SearchHit]:
        semantic_hits = await self.semantic.search(query, limit * 2)
        lexical_hits = await self.lexical.search(query, limit * 2)
        return reciprocal_rank_fusion([semantic_hits, lexical_hits], limit=limit)
