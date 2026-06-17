"""Agent endpoints — trigger and monitor AI agent tasks."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db

router = APIRouter()


@router.post("/extract")
async def run_extraction_agent(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger the Extraction Agent to process all pending sources for a project."""
    from app.agents.extraction_agent import extraction_agent_task

    task = extraction_agent_task.delay(project_id=str(project_id))
    return {"task_id": task.id, "agent": "extraction", "status": "running"}


@router.post("/story")
async def run_story_agent(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Story Agent to discover narrative structure from extracted knowledge."""
    from app.agents.story_agent import story_agent_task

    task = story_agent_task.delay(project_id=str(project_id))
    return {"task_id": task.id, "agent": "story", "status": "running"}


@router.post("/design")
async def run_design_agent(
    project_id: uuid.UUID,
    viz_type: str = "auto",
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Design Agent to select visual design principles for a visualization."""
    from app.agents.design_agent import design_agent_task

    task = design_agent_task.delay(project_id=str(project_id), viz_type=viz_type)
    return {"task_id": task.id, "agent": "design", "status": "running"}


@router.post("/chart")
async def run_chart_agent(
    visualization_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Chart Agent to optimize chart specifications."""
    from app.agents.chart_agent import chart_agent_task

    task = chart_agent_task.delay(visualization_id=str(visualization_id))
    return {"task_id": task.id, "agent": "chart", "status": "running"}


@router.post("/research")
async def run_research_agent(
    project_id: uuid.UUID,
    query: str = "",
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Research Agent to enrich project knowledge with external data."""
    from app.agents.research_agent import research_agent_task

    task = research_agent_task.delay(project_id=str(project_id), query=query)
    return {"task_id": task.id, "agent": "research", "status": "running"}


@router.post("/fact-check")
async def run_fact_check_agent(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Fact Check Agent to validate extracted facts."""
    from app.agents.fact_check_agent import fact_check_agent_task

    task = fact_check_agent_task.delay(project_id=str(project_id))
    return {"task_id": task.id, "agent": "fact_check", "status": "running"}


@router.post("/publish")
async def run_publishing_agent(
    visualization_id: uuid.UUID,
    format: str = "html",
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Publishing Agent to export a visualization."""
    from app.agents.publishing_agent import publishing_agent_task

    task = publishing_agent_task.delay(visualization_id=str(visualization_id), format=format)
    return {"task_id": task.id, "agent": "publishing", "status": "running"}


@router.get("/status/{task_id}")
async def get_agent_task_status(task_id: str):
    """Get the status of an agent task by Celery task ID."""
    from celery.result import AsyncResult

    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
