from mcp.server.fastmcp import FastMCP

from app.graphql.schema import INCIDENTS, SERVICES

mcp = FastMCP("OpsMind MCP")


@mcp.tool()
def get_service_status(service_name: str) -> dict:
    """Return current service ownership, tier and status."""
    for service in SERVICES:
        if service.name == service_name:
            return {
                "name": service.name,
                "owner": service.owner,
                "tier": service.tier,
                "status": service.status,
            }
    return {"error": "service_not_found", "service_name": service_name}


@mcp.tool()
def list_open_incidents() -> list[dict]:
    """List unresolved incidents available to the operations agent."""
    return [
        {
            "id": incident.id,
            "service": incident.service,
            "severity": incident.severity,
            "summary": incident.summary,
            "status": incident.status,
        }
        for incident in INCIDENTS
        if incident.status != "resolved"
    ]


@mcp.tool()
def create_incident_draft(service: str, severity: str, summary: str) -> dict:
    """Create a reviewable incident draft. This tool never publishes incidents directly."""
    return {
        "status": "draft",
        "requires_human_approval": True,
        "incident": {"service": service, "severity": severity, "summary": summary},
    }


@mcp.tool()
def search_runbooks(query: str) -> dict:
    """Return a request envelope for the RAG runbook search boundary."""
    return {
        "query": query,
        "next_step": "call the RAG retrieval service and return grounded source citations",
    }


if __name__ == "__main__":
    mcp.run()
