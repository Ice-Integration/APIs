from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.security.prompt_guard import PromptGuard
from app.security.rbac import Principal, authorize


@dataclass(frozen=True)
class AgentDecision:
    route: str
    reason: str


class KnowledgeAgent(Protocol):
    async def answer(self, question: str, principal: Principal) -> dict: ...


class ToolAgent(Protocol):
    async def execute(self, command: str, principal: Principal) -> dict: ...


class AgentOrchestrator:
    """Routes user intent while keeping authorization outside the model."""

    TOOL_PREFIXES = ("create incident", "draft incident", "service status", "open incidents")

    def __init__(
        self,
        knowledge_agent: KnowledgeAgent,
        tool_agent: ToolAgent,
        guard: PromptGuard | None = None,
    ) -> None:
        self.knowledge_agent = knowledge_agent
        self.tool_agent = tool_agent
        self.guard = guard or PromptGuard()

    def classify(self, text: str) -> AgentDecision:
        lowered = text.strip().lower()
        if any(lowered.startswith(prefix) for prefix in self.TOOL_PREFIXES):
            return AgentDecision("tools", "operational_intent")
        return AgentDecision("knowledge", "knowledge_intent")

    async def run(self, text: str, principal: Principal) -> dict:
        inspection = self.guard.inspect(text)
        if not inspection.allowed:
            return {"status": "blocked", "reason": inspection.reason}

        decision = self.classify(text)
        if decision.route == "tools":
            authorize(principal, "service:read")
            result = await self.tool_agent.execute(text, principal)
        else:
            authorize(principal, "knowledge:read")
            result = await self.knowledge_agent.answer(text, principal)

        return {"status": "ok", "route": decision.route, "result": result}
