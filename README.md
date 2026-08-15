# OpsMind AI Platform

OpsMind is a production-style AI engineering portfolio project for enterprise engineering and SRE teams. It combines retrieval-augmented generation, governed MCP tools, GraphQL, agent routing, evaluations, security controls and backend engineering practices in one system.

## Task

Operational knowledge is usually fragmented across runbooks, incident records, service catalogs and internal APIs. Engineers lose time searching for the right procedure during incidents, while generic AI assistants can hallucinate, expose restricted knowledge or execute unsafe actions.

OpsMind provides a governed operations copilot that retrieves approved internal knowledge, cites its evidence, exposes structured operational data and routes controlled actions through MCP servers.

## Architecture

```text
                        +----------------------+
                        | Web / CLI / AI Client|
                        +----------+-----------+
                                   |
                                   v
+----------------------------------------------------------------+
|                    FastAPI AI Gateway                           |
|  prompt guard -> auth/RBAC -> agent router -> streaming/SSE    |
+---------+----------------------+--------------------+-----------+
          |                      |                    |
          v                      v                    v
+------------------+   +------------------+  +-------------------+
| Knowledge Agent  |   | GraphQL API      |  | Tool Agent        |
| RAG + citations  |   | services/incidents| | MCP client layer  |
+--------+---------+   +--------+---------+  +---------+---------+
         |                      |                      |
         v                      v                      v
+------------------+   +------------------+  +-------------------+
| Hybrid Retrieval |   | Postgres         |  | MCP servers       |
| semantic+lexical |   | pgvector         |  | knowledge/incident|
| RRF fusion       |   +------------------+  +-------------------+
+--------+---------+
         |
         v
+------------------+      +----------------+      +---------------+
| Document ACLs    |      | Redis memory   |      | OpenTelemetry |
| team filtering   |      | ingestion queue|      | traces        |
+------------------+      +----------------+      +---------------+
```

## AI engineering skills demonstrated

- Python 3.11 and async FastAPI
- RAG with grounded answers and citations
- OpenAI Responses API and embeddings
- PostgreSQL with pgvector
- hybrid semantic + lexical retrieval
- reciprocal-rank fusion reranking
- agent orchestration with deterministic policy boundaries
- multiple MCP servers and tool contracts
- human approval pattern for state-changing tools
- GraphQL with Strawberry
- Redis conversation memory
- background ingestion queue
- prompt-injection detection
- RBAC and team-level document ACLs
- streaming responses with Server-Sent Events
- OpenTelemetry instrumentation hooks
- AI quality evaluation and security test cases
- Pytest/TDD
- Docker and Docker Compose
- GitHub Actions CI

## Safety model

OpsMind deliberately keeps authorization and approval outside the language model.

1. Input is inspected by a deterministic prompt guard.
2. RBAC checks happen in Python before a tool or knowledge route executes.
3. Restricted documents can be filtered using team ACLs.
4. Read-only MCP tools may execute automatically.
5. State-changing operations produce drafts first.
6. A privileged approval path is required before downstream mutation.
7. Traces and evaluations provide an audit and quality loop.

The included MCP adapters are portfolio-safe examples. They do not modify a real production incident system until a downstream adapter and authentication layer are supplied.

## Project structure

```text
app/
  agents/             # policy-aware agent orchestration
  core/               # configuration
  graphql/            # structured operational API
  ingestion/          # background ingestion worker
  mcp/                # knowledge + incident MCP servers
  memory/             # Redis conversation memory
  observability/      # OpenTelemetry setup
  rag/                # RAG service + hybrid retrieval
  security/           # prompt guard, RBAC and ACLs
  main.py
scripts/
  ingest.py
  run_ingestion_worker.py
evals/
tests/
```

## Quick start

```bash
cp .env.example .env
# add OPENAI_API_KEY to .env

docker compose up -d db redis
pip install -e '.[dev]'
python scripts/ingest.py
uvicorn app.main:app --reload
```

Run the ingestion worker separately:

```bash
python -m scripts.run_ingestion_worker
```

Or start the local stack with Docker Compose:

```bash
docker compose up --build
```

## RAG API

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H 'content-type: application/json' \
  -d '{"question":"What should an engineer do when checkout latency breaches the SLO?"}'
```

Streaming is available from `POST /api/v1/ask/stream` using Server-Sent Events.

## GraphQL

GraphQL is available at `/graphql`.

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

## MCP servers

Start the knowledge server:

```bash
python -m app.mcp.knowledge_server
```

Start the incident server:

```bash
python -m app.mcp.incident_server
```

Example tools include `search_runbooks`, `get_service_status`, `list_open_incidents`, `create_incident_draft` and `approve_incident_draft`.

## Evaluation

The repository includes retrieval/answer evals plus deterministic security and retrieval-fusion unit tests. The goal is to treat AI quality as an engineering metric rather than judging the system by a single demo conversation.

Run checks with:

```bash
ruff check .
pytest -q
```

## Interview talking points

This project is designed to support deeper AI engineering discussion: why hybrid retrieval improves exact-term recall, why authorization must not be delegated to an LLM, how MCP separates tool contracts from model reasoning, how document ACLs affect retrieval, why state-changing tools use human approval, and how evals and tracing turn an AI prototype into an operable system.
