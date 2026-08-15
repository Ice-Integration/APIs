from app.mcp.server import create_incident_draft, get_service_status


def test_incident_creation_is_guarded_by_human_approval() -> None:
    result = create_incident_draft("checkout-api", "SEV-2", "Latency breach")
    assert result["status"] == "draft"
    assert result["requires_human_approval"] is True


def test_service_status_lookup() -> None:
    result = get_service_status("checkout-api")
    assert result["owner"] == "payments"
    assert result["status"] == "degraded"
