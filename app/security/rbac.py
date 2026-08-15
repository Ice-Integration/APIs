from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ENGINEER = "engineer"
    INCIDENT_MANAGER = "incident_manager"
    ADMIN = "admin"


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: Role
    teams: frozenset[str]


PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.VIEWER: frozenset({"knowledge:read"}),
    Role.ENGINEER: frozenset({"knowledge:read", "service:read", "incident:draft"}),
    Role.INCIDENT_MANAGER: frozenset(
        {"knowledge:read", "service:read", "incident:draft", "incident:approve"}
    ),
    Role.ADMIN: frozenset({"*"}),
}


def authorize(principal: Principal, permission: str) -> None:
    allowed = PERMISSIONS[principal.role]
    if "*" not in allowed and permission not in allowed:
        raise PermissionError(f"missing permission: {permission}")


def can_read_document(principal: Principal, acl_teams: set[str] | None) -> bool:
    if principal.role == Role.ADMIN or not acl_teams:
        return True
    return bool(principal.teams.intersection(acl_teams))
