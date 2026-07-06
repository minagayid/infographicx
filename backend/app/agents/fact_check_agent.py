"""Fact-Check Agent — flag knowledge items that lack supporting evidence.

Deterministic quality gate before publishing: it scores each item's
grounding (does it cite a source / carry evidence / participate in a
supported relationship) and raises warnings for unsupported or contradicted
claims, with a reasoning trace.
"""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app


async def run(items: list[dict[str, Any]], relations: list[dict[str, Any]] | None = None) -> AgentResult:
    relations = relations or []
    reasoning = [f"Fact-checking {len(items)} item(s) against {len(relations)} relation(s)"]

    contradicted = {
        r.get("source_label")
        for r in relations
        if r.get("relation_type") == "contradicts"
    }
    supported = {
        r.get("target_label")
        for r in relations
        if r.get("relation_type") == "supports"
    }

    warnings: list[dict[str, Any]] = []
    grounded = 0
    for item in items:
        label = item.get("label", "")
        has_source = bool(item.get("source_id") or item.get("properties", {}).get("source"))
        has_evidence = bool(item.get("evidence") or item.get("description"))
        if label in contradicted:
            warnings.append({"item": label, "issue": "contradicted_by_another_item", "severity": "high"})
        elif not has_source and not has_evidence and label not in supported:
            warnings.append({"item": label, "issue": "unsupported_claim", "severity": "medium"})
        else:
            grounded += 1

    reasoning.append(f"{grounded} grounded, {len(warnings)} flagged")
    confidence = grounded / len(items) if items else 1.0
    reasoning.append(f"Overall grounding confidence: {confidence:.2f}")

    return AgentResult(
        agent="fact_check",
        output={"warnings": warnings, "grounded_count": grounded, "confidence": round(confidence, 3)},
        reasoning=reasoning,
    )


@celery_app.task(bind=True, name="agents.fact_check")
def fact_check_agent_task(self, project_id: str, items: list[dict[str, Any]] | None = None,
                          relations: list[dict[str, Any]] | None = None):
    import asyncio

    result = asyncio.run(run(items or [], relations=relations))
    return {"project_id": project_id, **result.to_dict()}
