"""Story Agent — discover the narrative structure of the knowledge graph."""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app
from app.engines.story_discovery.engine import StoryDiscoveryEngine


async def run(
    items: list[dict[str, Any]],
    relations: list[dict[str, Any]] | None = None,
    context: dict[str, Any] | None = None,
) -> AgentResult:
    """Discover a narrative theme and structure over items + relations."""
    reasoning = [f"Discovering narrative from {len(items)} item(s) and {len(relations or [])} relation(s)"]
    # Story discovery is LLM-backed; if no model is configured the engine
    # can't even be constructed. Degrade to a default theme and record why,
    # rather than crashing the pipeline.
    try:
        engine = StoryDiscoveryEngine()
        result = await engine.discover(items, relations=relations, context=context)
        theme = getattr(result, "theme", "General Overview")
        reasoning.append(f"Selected theme: {theme!r}")
        return AgentResult(
            agent="story",
            output={"theme": theme, "story": getattr(result, "__dict__", {"theme": theme})},
            reasoning=reasoning,
        )
    except Exception as exc:
        reasoning.append(f"LLM story discovery unavailable ({type(exc).__name__}); using default theme")
        return AgentResult(
            agent="story",
            status="degraded",
            output={"theme": "General Overview", "story": {"theme": "General Overview"}},
            reasoning=reasoning,
        )


@celery_app.task(bind=True, name="agents.story")
def story_agent_task(self, project_id: str, items: list[dict[str, Any]] | None = None,
                     relations: list[dict[str, Any]] | None = None):
    import asyncio

    result = asyncio.run(run(items or [], relations=relations))
    return {"project_id": project_id, **result.to_dict()}
