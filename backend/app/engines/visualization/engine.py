"""Visualization Engine — assemble a renderable visualization from knowledge.

Composes the deterministic Design and Chart agents: pick the best
visualization type for the knowledge shape, then produce a concrete chart
spec. No LLM required, so generation is fast, explainable and testable.
"""
from __future__ import annotations

from typing import Any


class VisualizationEngine:
    """Turns knowledge items + relations into a renderable visualization."""

    async def generate(
        self,
        items: list[dict[str, Any]],
        relations: list[dict[str, Any]] | None = None,
        viz_type: str = "auto",
    ) -> dict[str, Any]:
        from app.agents import chart_agent, design_agent

        relations = relations or []
        design = await design_agent.run(items, relations=relations, viz_type=viz_type)
        chosen = design.output.get("viz_type", "infographic")
        chart = await chart_agent.run(chosen, items=items, relations=relations)

        return {
            "viz_type": chosen,
            "theme": design.output.get("theme"),
            "spec": chart.output.get("spec", {}),
            "reasoning": design.reasoning + chart.reasoning,
        }


# Celery task entry point
from app.core.celery_app import celery_app  # noqa: E402


@celery_app.task(bind=True, name="visualization.generate")
def generate_visualization_task(
    self,
    project_id: str,
    viz_type: str = "auto",
    items: list[dict[str, Any]] | None = None,
    relations: list[dict[str, Any]] | None = None,
):
    """Celery task — generate a visualization for a project's knowledge graph."""
    import asyncio

    engine = VisualizationEngine()
    result = asyncio.run(engine.generate(items or [], relations=relations, viz_type=viz_type))
    return {"project_id": project_id, **result}
