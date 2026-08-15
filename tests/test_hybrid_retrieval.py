from app.rag.hybrid import SearchHit, reciprocal_rank_fusion


def hit(doc_id: str, source: str) -> SearchHit:
    return SearchHit(doc_id, doc_id, f"content-{doc_id}", 1.0, source)


def test_rrf_rewards_documents_found_by_multiple_retrievers() -> None:
    semantic = [hit("runbook-a", "semantic"), hit("runbook-b", "semantic")]
    lexical = [hit("runbook-b", "lexical"), hit("runbook-c", "lexical")]

    fused = reciprocal_rank_fusion([semantic, lexical], limit=3)

    assert fused[0].document_id == "runbook-b"
    assert fused[0].source == "hybrid"
