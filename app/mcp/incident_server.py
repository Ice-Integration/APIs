from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("opsmind-incidents")


@dataclass(frozen=True)
class IncidentDraft:
    draft_id: str
    service: str
    title: str
    severity: str
    approved: bool = False


@mcp.tool()
async def get_service_status(service: str) -> dict:
    return {"service": service, "status": "unknown", "source": "service-catalog-adapter"}


@mcp.tool()
async def list_open_incidents(service: str | None = None) -> dict:
    return {"service": service, "incidents": [], "source": "incident-adapter"}


@mcp.tool()
async def create_incident_draft(service: str, title: str, severity: str = "SEV3") -> dict:
    draft = IncidentDraft(
        draft_id=str(uuid4()),
        service=service,
        title=title,
        severity=severity,
    )
    return {
        **asdict(draft),
        "requires_human_approval": True,
        "next_action": "approve_incident_draft",
    }


@mcp.tool()
async def approve_incident_draft(draft_id: str, approver: str) -> dict:
    """Adapter boundary for a privileged write path.

    A production implementation verifies the caller's incident:approve permission,
    records an audit event and performs an idempotent downstream write.
    """
    return {
        "draft_id": draft_id,
        "approver": approver,
        "status": "approval_adapter_required",
    }


if __name__ == "__main__":
    mcp.run()
