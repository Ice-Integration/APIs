import strawberry


@strawberry.type
class Service:
    name: str
    owner: str
    tier: str
    status: str


@strawberry.type
class Incident:
    id: str
    service: str
    severity: str
    summary: str
    status: str


SERVICES = [
    Service(name="checkout-api", owner="payments", tier="tier-1", status="degraded"),
    Service(name="identity-api", owner="platform", tier="tier-1", status="healthy"),
]

INCIDENTS = [
    Incident(
        id="INC-1042",
        service="checkout-api",
        severity="SEV-2",
        summary="Elevated p95 latency in checkout",
        status="investigating",
    )
]


@strawberry.type
class Query:
    @strawberry.field
    def services(self) -> list[Service]:
        return SERVICES

    @strawberry.field
    def open_incidents(self) -> list[Incident]:
        return [incident for incident in INCIDENTS if incident.status != "resolved"]


schema = strawberry.Schema(query=Query)
