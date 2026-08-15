# OpsMind AI Platform

A portfolio-grade AI engineering project that demonstrates retrieval-augmented generation, MCP tool servers, GraphQL, agent orchestration, evaluation, observability, and production backend practices.

## Real-world problem

Engineering and operations teams lose time searching across runbooks, incident notes, service documentation, and internal APIs. Existing chatbots often hallucinate, cannot cite sources, and cannot safely take actions.

OpsMind solves this with a governed AI operations copilot that:

- ingests internal documents into a vector store
- answers questions with RAG and source citations
- exposes structured service and incident data via GraphQL
- exposes safe operational actions through an MCP server
- routes questions and actions through an agent service
- evaluates retrieval and answer quality
- includes tests, Docker, CI, and production-oriented boundaries

## Architecture

```text
Client
  |
  v
FastAPI AI Gateway
  |----> RAG service ----> Embeddings ----> pgvector/Postgres
  |----> GraphQL API ----> Service + Incident repositories
  |----> MCP client -----> Ops MCP server ----> guarded tools
  |----> OpenAI Responses API
  |
  +----> observability + evals
```

## AI engineering skills demonstrated

- Python and FastAPI
- RAG and semantic retrieval
- OpenAI embeddings and Responses API
- MCP server design and tool contracts
- GraphQL with Strawberry
- PostgreSQL and pgvector
- agent/tool orchestration
- prompt grounding and citations
- retrieval evaluation
- hallucination controls
- clean architecture
- dependency injection
- async Python
- Pytest/TDD
- Docker and Docker Compose
- GitHub Actions CI
- structured logging
- health/readiness endpoints

## Project structure

```text
app/
  api/
  core/
  graphql/
  mcp/
  rag/
  services/
  main.py
scripts/
  ingest.py
evals/
tests/
docs/
```

## Quick start

1. Copy `.env.example` to `.env`.
2. Add `OPENAI_API_KEY`.
3. Start Postgres with `docker compose up -d db`.
4. Install dependencies with `pip install -e .[dev]`.
5. Run `python scripts/ingest.py`.
6. Start the API with `uvicorn app.main:app --reload`.
7. Start the MCP server with `python -m app.mcp.server`.

## Example RAG request

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"What should an engineer do when checkout latency breaches the SLO?"}'
```

## Example GraphQL query

```graphql
query {
  services {
    name
    owner
    tier
    status
  }
}
```

GraphQL is available at `/graphql`.

## MCP tools

The MCP server exposes guarded tools such as:

- `get_service_status`
- `list_open_incidents`
- `create_incident_draft`
- `search_runbooks`

The example intentionally uses draft-only mutation behavior so an AI agent cannot perform destructive production actions without an external approval layer.

## Evaluation

`evals/run_eval.py` measures retrieval hit rate and citation coverage against a small golden dataset. This gives the project a measurable quality loop rather than relying on subjective demos.

## Production extensions

A production deployment would add OIDC/RBAC, tenant isolation, Redis caching, background ingestion workers, OpenTelemetry exporters, reranking, document-level ACL filtering, secrets management, and a human approval workflow for high-risk MCP tools.
