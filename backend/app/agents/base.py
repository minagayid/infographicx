"""Shared agent result type and reasoning helper."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    """Outcome of a single agent run."""

    agent: str
    status: str = "ok"  # "ok" | "error"
    output: dict[str, Any] = field(default_factory=dict)
    reasoning: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "status": self.status,
            "output": self.output,
            "reasoning": self.reasoning,
            "error": self.error,
        }
