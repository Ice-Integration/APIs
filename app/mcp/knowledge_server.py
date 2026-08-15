from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("opsmind-knowledge")


@mcp.tool()
async def search_runbooks(query: str, team: str | None = None) -> dict:
    """Search approved runbooks. Production wiring delegates to the RAG retriever."""
    return {
        "query": query,
        "team": team,
        "matches": [],
        "note": "adapter hook: connect HybridRetriever here",
    }


@mcp.resource("opsmind://policies/tool-safety")
def tool_safety_policy() -> str:
    return (
        "Read operations may execute automatically. State-changing operations return "
        "drafts and require explicit human approval before commit."
    )


if __name__ == "__main__":
    mcp.run()
