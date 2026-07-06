"""Tests for the agent layer, engines and pipeline orchestrator."""
import pytest

from app.agents import chart_agent, design_agent, fact_check_agent, publishing_agent, research_agent
from app.agents.pipeline import run_pipeline
from app.engines.visualization.engine import VisualizationEngine

ITEMS = [
    {"label": "Photosynthesis", "item_type": "process", "properties": {"precedes": "Respiration"},
     "description": "converts light", "source_id": "s1"},
    {"label": "Respiration", "item_type": "process", "properties": {}, "description": "releases energy", "source_id": "s1"},
    {"label": "Glucose", "item_type": "entity", "properties": {}, "description": "sugar", "source_id": "s1"},
]


@pytest.mark.asyncio
async def test_research_agent_builds_relations():
    result = await research_agent.run(ITEMS)
    assert result.status == "ok"
    # The explicit "precedes" property must yield a relation.
    types = {r["relation_type"] for r in result.output["relations"]}
    assert "precedes" in types
    assert result.reasoning


@pytest.mark.asyncio
async def test_design_agent_picks_timeline_for_temporal_data():
    research = await research_agent.run(ITEMS)
    design = await design_agent.run(ITEMS, relations=research.output["relations"])
    assert design.output["viz_type"] == "timeline"


@pytest.mark.asyncio
async def test_design_agent_respects_forced_type():
    result = await design_agent.run(ITEMS, viz_type="mind_map")
    assert result.output["viz_type"] == "mind_map"


@pytest.mark.asyncio
async def test_design_agent_rejects_unknown_type():
    result = await design_agent.run(ITEMS, viz_type="not_a_type")
    assert result.status == "error"


@pytest.mark.asyncio
async def test_chart_agent_produces_spec():
    result = await chart_agent.run("knowledge_graph", items=ITEMS)
    spec = result.output["spec"]
    assert spec["renderer"] == "d3-force"
    assert len(spec["nodes"]) == 3


@pytest.mark.asyncio
async def test_fact_check_flags_unsupported_claim():
    items = [{"label": "Unsourced claim", "item_type": "fact", "properties": {}}]
    result = await fact_check_agent.run(items)
    assert result.output["warnings"][0]["issue"] == "unsupported_claim"
    assert result.output["confidence"] == 0.0


@pytest.mark.asyncio
async def test_publishing_agent_rejects_bad_format():
    result = await publishing_agent.run("v1", format="exe")
    assert result.status == "error"


@pytest.mark.asyncio
async def test_visualization_engine_composes_design_and_chart():
    engine = VisualizationEngine()
    research = await research_agent.run(ITEMS)
    out = await engine.generate(ITEMS, relations=research.output["relations"])
    assert out["viz_type"] == "timeline"  # temporal relation -> timeline
    assert out["spec"]["nodes"]


@pytest.mark.asyncio
async def test_pipeline_runs_all_stages():
    # extraction needs no LLM to run (it degrades to zero items); the
    # downstream stages still execute and the run stays inspectable.
    result = await run_pipeline(sources=[])
    assert result["status"] == "ok"
    stage_names = [s["agent"] for s in result["trace"]]
    assert stage_names == ["extraction", "research", "story", "design", "chart", "fact_check", "publishing"]
