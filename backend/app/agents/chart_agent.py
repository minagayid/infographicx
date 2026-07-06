"""Chart Agent — turn a chosen visualization type into a concrete chart spec."""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app

# How each visualization type maps to a renderable layout primitive.
_LAYOUT = {
    "timeline": {"renderer": "d3-timeline", "layout": "horizontal", "axis": "time"},
    "flowchart": {"renderer": "mermaid", "layout": "top-down", "axis": None},
    "mind_map": {"renderer": "d3-tree", "layout": "radial", "axis": None},
    "knowledge_graph": {"renderer": "d3-force", "layout": "force-directed", "axis": None},
    "dashboard": {"renderer": "grid", "layout": "grid", "axis": None},
    "decision_tree": {"renderer": "d3-tree", "layout": "top-down", "axis": None},
    "learning_path": {"renderer": "d3-path", "layout": "linear", "axis": None},
    "infographic": {"renderer": "svg-compose", "layout": "vertical", "axis": None},
}


async def run(viz_type: str, items: list[dict[str, Any]] | None = None,
              relations: list[dict[str, Any]] | None = None) -> AgentResult:
    items = items or []
    relations = relations or []
    reasoning = [f"Building chart spec for '{viz_type}'"]

    base = _LAYOUT.get(viz_type, _LAYOUT["infographic"])
    if viz_type not in _LAYOUT:
        reasoning.append(f"Unknown viz_type '{viz_type}'; falling back to infographic layout")

    # Node/edge budget guards keep the rendered output legible.
    node_cap = 60
    nodes = [{"id": i.get("label", f"n{idx}"), "label": i.get("label", "")} for idx, i in enumerate(items[:node_cap])]
    if len(items) > node_cap:
        reasoning.append(f"Capped nodes at {node_cap} (had {len(items)}) for legibility")

    edges = [
        {"source": r.get("source_label"), "target": r.get("target_label"), "type": r.get("relation_type")}
        for r in relations
        if r.get("source_label") and r.get("target_label")
    ]
    reasoning.append(f"Spec: {len(nodes)} nodes, {len(edges)} edges via {base['renderer']}")

    spec = {"viz_type": viz_type, **base, "nodes": nodes, "edges": edges}
    return AgentResult(agent="chart", output={"spec": spec}, reasoning=reasoning)


@celery_app.task(bind=True, name="agents.chart")
def chart_agent_task(self, visualization_id: str, viz_type: str = "infographic",
                     items: list[dict[str, Any]] | None = None,
                     relations: list[dict[str, Any]] | None = None):
    import asyncio

    result = asyncio.run(run(viz_type, items=items, relations=relations))
    return {"visualization_id": visualization_id, **result.to_dict()}
