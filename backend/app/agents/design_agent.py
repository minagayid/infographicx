"""Design Agent — pick the visualization type best suited to the knowledge.

Rule-based and deterministic: it maps the shape of the extracted knowledge
(item count, relationship density, temporal/sequential/hierarchical signals)
to one of the supported visualization types, with a reasoning trace. This
makes visualization selection explainable and testable without an LLM.
"""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app

# Supported viz types (see app/models/visualization.py).
VIZ_TYPES = {
    "infographic", "mind_map", "knowledge_graph", "timeline",
    "flowchart", "dashboard", "decision_tree", "learning_path",
}

# Relationship types that signal a particular structure.
_TEMPORAL = {"precedes"}
_SEQUENTIAL = {"precedes", "causes", "depends_on"}
_HIERARCHICAL = {"contains", "belongs_to", "derived_from"}


def _select(items: list[dict[str, Any]], relations: list[dict[str, Any]]) -> tuple[str, list[str]]:
    reasoning: list[str] = []
    n_items = len(items)
    rel_types = [r.get("relation_type") for r in relations]
    reasoning.append(f"{n_items} items, {len(relations)} relations")

    if n_items == 0:
        reasoning.append("No items -> default infographic")
        return "infographic", reasoning

    temporal = sum(1 for t in rel_types if t in _TEMPORAL)
    sequential = sum(1 for t in rel_types if t in _SEQUENTIAL)
    hierarchical = sum(1 for t in rel_types if t in _HIERARCHICAL)
    density = len(relations) / n_items if n_items else 0
    reasoning.append(
        f"signals: temporal={temporal}, sequential={sequential}, hierarchical={hierarchical}, density={density:.2f}"
    )

    # Ordered from most to least specific signal.
    if temporal and temporal >= hierarchical:
        choice = "timeline"
    elif sequential and sequential > hierarchical:
        choice = "flowchart"
    elif hierarchical:
        choice = "mind_map"
    elif density >= 1.5:
        choice = "knowledge_graph"
    elif n_items >= 12:
        choice = "dashboard"
    else:
        choice = "infographic"

    reasoning.append(f"Selected '{choice}'")
    return choice, reasoning


async def run(
    items: list[dict[str, Any]],
    relations: list[dict[str, Any]] | None = None,
    viz_type: str = "auto",
) -> AgentResult:
    relations = relations or []
    if viz_type != "auto":
        if viz_type not in VIZ_TYPES:
            return AgentResult(agent="design", status="error", error=f"Unknown viz_type: {viz_type}")
        reasoning = [f"Caller forced viz_type '{viz_type}'"]
        chosen = viz_type
    else:
        chosen, reasoning = _select(items, relations)

    theme = "light" if len(items) <= 20 else "dense"
    reasoning.append(f"Theme: {theme}")
    return AgentResult(
        agent="design",
        output={"viz_type": chosen, "theme": theme, "item_count": len(items)},
        reasoning=reasoning,
    )


@celery_app.task(bind=True, name="agents.design")
def design_agent_task(self, project_id: str, viz_type: str = "auto",
                      items: list[dict[str, Any]] | None = None,
                      relations: list[dict[str, Any]] | None = None):
    import asyncio

    result = asyncio.run(run(items or [], relations=relations, viz_type=viz_type))
    return {"project_id": project_id, **result.to_dict()}
