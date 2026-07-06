"""Extraction Agent — turn raw source content into structured knowledge items."""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app
from app.engines.knowledge_extraction.engine import KnowledgeExtractionEngine


async def run(sources: list[dict[str, Any]]) -> AgentResult:
    """Extract knowledge from a batch of already-ingested sources.

    Each source is ``{"raw_content": {...}, "metadata": {...}}``. The agent
    delegates to the Knowledge Extraction Engine (which degrades gracefully
    when no LLM is configured) and aggregates the items it produced.
    """
    reasoning = [f"Extracting knowledge from {len(sources)} source(s)"]
    if not sources:
        return AgentResult(agent="extraction", output={"items": []}, reasoning=reasoning + ["No sources to process"])

    # Extraction is LLM-backed; degrade gracefully when no model is configured.
    try:
        engine = KnowledgeExtractionEngine()
        results = await engine.batch_extract(sources)
    except Exception as exc:
        reasoning.append(f"LLM extraction unavailable ({type(exc).__name__}); returning no items")
        return AgentResult(agent="extraction", status="degraded", output={"items": [], "source_count": len(sources)}, reasoning=reasoning)

    items: list[dict[str, Any]] = []
    for idx, result in enumerate(results):
        extracted = getattr(result, "items", None) or []
        items.extend(item if isinstance(item, dict) else vars(item) for item in extracted)
        reasoning.append(f"Source {idx}: extracted {len(extracted)} item(s)")

    reasoning.append(f"Total knowledge items: {len(items)}")
    return AgentResult(agent="extraction", output={"items": items, "source_count": len(sources)}, reasoning=reasoning)


@celery_app.task(bind=True, name="agents.extraction")
def extraction_agent_task(self, project_id: str, sources: list[dict[str, Any]] | None = None):
    """Celery entry point: extract knowledge for a project's pending sources."""
    import asyncio

    result = asyncio.run(run(sources or []))
    return {"project_id": project_id, **result.to_dict()}
