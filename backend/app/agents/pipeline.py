"""Agent pipeline orchestrator.

Chains the agents into the end-to-end InfographicX workflow:

    extraction -> research -> story -> design -> chart -> fact_check -> publishing

Each stage reads the accumulated context and contributes its output plus a
reasoning trace. A stage that errors is recorded and the run is marked
``partial`` rather than aborting, so the whole run stays inspectable — the
same resilient-orchestration pattern used across the platform.
"""
from __future__ import annotations

from typing import Any

from app.agents import (
    chart_agent,
    design_agent,
    extraction_agent,
    fact_check_agent,
    publishing_agent,
    research_agent,
    story_agent,
)


async def run_pipeline(
    sources: list[dict[str, Any]],
    export_format: str = "html",
    viz_type: str = "auto",
) -> dict[str, Any]:
    """Run the full workflow over a set of ingested sources."""
    trace: list[dict[str, Any]] = []
    failed: list[str] = []

    def record(result) -> Any:
        trace.append(result.to_dict())
        # "degraded" (e.g. no LLM configured) is expected and non-fatal; only a
        # hard "error" marks the run partial.
        if result.status == "error":
            failed.append(result.agent)
        return result

    extraction = record(await extraction_agent.run(sources))
    items = extraction.output.get("items", [])

    research = record(await research_agent.run(items))
    relations = research.output.get("relations", [])

    record(await story_agent.run(items, relations=relations))

    design = record(await design_agent.run(items, relations=relations, viz_type=viz_type))
    chosen_viz = design.output.get("viz_type", "infographic")

    chart = record(await chart_agent.run(chosen_viz, items=items, relations=relations))
    spec = chart.output.get("spec", {})

    record(await fact_check_agent.run(items, relations=relations))
    record(await publishing_agent.run("preview", spec=spec, format=export_format))

    return {
        "status": "ok" if not failed else "partial",
        "failed_stages": failed,
        "viz_type": chosen_viz,
        "item_count": len(items),
        "relation_count": len(relations),
        "trace": trace,
    }
