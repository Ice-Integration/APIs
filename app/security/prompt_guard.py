from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    reason: str | None = None


class PromptGuard:
    """Small deterministic guardrail layer used before retrieval and tool execution.

    This is intentionally not presented as a complete security solution. It provides
    cheap, testable controls that can be combined with model-side policies, ACLs and
    human approval for state-changing tools.
    """

    _blocked_patterns = (
        re.compile(r"ignore (all|any|the) previous instructions", re.IGNORECASE),
        re.compile(r"reveal (the )?(system|developer) prompt", re.IGNORECASE),
        re.compile(r"print (all )?(secrets|credentials|api keys)", re.IGNORECASE),
        re.compile(r"bypass (authorization|rbac|access control)", re.IGNORECASE),
    )

    def inspect(self, text: str) -> GuardResult:
        normalized = " ".join(text.split())
        if len(normalized) > 8_000:
            return GuardResult(False, "prompt_too_large")
        for pattern in self._blocked_patterns:
            if pattern.search(normalized):
                return GuardResult(False, "prompt_injection_pattern")
        return GuardResult(True)
