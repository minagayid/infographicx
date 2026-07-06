"""AI agents for the InfographicX pipeline.

Each agent is a thin, testable coordination layer over one of the processing
engines (or a rule-based decision step). Every agent exposes:

* an ``async run(...)`` coroutine with the real logic — usable directly in
  tests and from the pipeline orchestrator, with no broker or LLM required;
* a Celery task wrapper (``*_agent_task``) that the API endpoints dispatch
  via ``.delay(...)``.

All agents return an :class:`AgentResult` carrying their output plus a
reasoning trace, so a run can be inspected end to end.
"""
from app.agents.base import AgentResult

__all__ = ["AgentResult"]
