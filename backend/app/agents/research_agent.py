"""Research Agent — discover relationships between extracted knowledge items."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app
from app.engines.relationship.engine import RelationshipEngine


def _rel_to_dict(rel: Any) -> dict[str, Any]:
    if is_dataclass(rel):
        d = asdict(rel)
        # RelationType is an enum; serialise to its value.
        rt = d.get("relation_type")
        d["relation_type"] = getattr(rt, "value", rt)
        return d
    return dict(rel)


async def run(items: list[dict[str, Any]], raw_content: dict[str, Any] | None = None) -> AgentResult:
    """Build the relationship graph over knowledge items.

    Uses the Relationship Engine's explicit + semantic passes (which run
    without any LLM); LLM inference is attempted only when configured and
    degrades gracefully otherwise.
    """
    reasoning = [f"Discovering relationships among {len(items)} item(s)"]
    engine = RelationshipEngine()
    result = await engine.discover(items, raw_content=raw_content)

    relations = [_rel_to_dict(r) for r in result.relations]
    reasoning.append(f"Found {len(relations)} relationship(s)")
    reasoning.append(f"Identified {len(result.clusters)} cluster(s)")
    if result.graph_metrics:
        reasoning.append(f"Graph: {result.graph_metrics.get('node_count', 0)} nodes / {result.graph_metrics.get('edge_count', 0)} edges")

    return AgentResult(
        agent="research",
        output={"relations": relations, "clusters": result.clusters, "graph_metrics": result.graph_metrics},
        reasoning=reasoning,
    )


@celery_app.task(bind=True, name="agents.research")
def research_agent_task(self, project_id: str, items: list[dict[str, Any]] | None = None):
    import asyncio

    result = asyncio.run(run(items or []))
    return {"project_id": project_id, **result.to_dict()}
