"""Visualization endpoints — generate, view, and manage visualizations."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.visualization import Visualization
from app.schemas.visualization import VisualizationCreate, VisualizationRead
from app.schemas.knowledge import KnowledgeGraphRead, KnowledgeNodeRead, KnowledgeEdgeRead

router = APIRouter()


@router.get("/{project_id}", response_model=list[VisualizationRead])
async def list_visualizations(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all visualizations for a project."""
    result = await db.execute(select(Visualization).where(Visualization.project_id == project_id))
    return result.scalars().all()


@router.post("/{project_id}", response_model=VisualizationRead, status_code=status.HTTP_201_CREATED)
async def create_visualization(
    project_id: uuid.UUID,
    viz_in: VisualizationCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new visualization (auto-generate or manual)."""
    viz = Visualization(
        project_id=project_id,
        viz_type=viz_in.viz_type,
        title=viz_in.title,
        description=viz_in.description,
        spec=viz_in.spec.model_dump(),
        theme=viz_in.theme,
    )
    db.add(viz)
    await db.flush()
    await db.refresh(viz)
    return viz


@router.post("/{project_id}/generate")
async def generate_visualization(
    project_id: uuid.UUID,
    viz_type: str = "auto",
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Auto-generate a visualization from project knowledge (async)."""
    from app.engines.visualization.engine import generate_visualization_task

    task = generate_visualization_task.delay(
        project_id=str(project_id),
        viz_type=viz_type,
        user_id=current_user["user_id"],
    )
    return {"task_id": task.id, "status": "generating"}


@router.get("/detail/{viz_id}", response_model=VisualizationRead)
async def get_visualization(
    viz_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a visualization by ID."""
    result = await db.execute(select(Visualization).where(Visualization.id == viz_id))
    viz = result.scalar_one_or_none()
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
    return viz


@router.get("/{viz_id}/graph", response_model=KnowledgeGraphRead)
async def get_knowledge_graph(
    viz_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the full knowledge graph (nodes + edges) for a visualization."""
    from app.models.knowledge_node import KnowledgeNode
    from app.models.knowledge_edge import KnowledgeEdge

    nodes_result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.visualization_id == viz_id))
    nodes = nodes_result.scalars().all()

    edges_result = await db.execute(select(KnowledgeEdge).where(KnowledgeEdge.source_node_id.in_([n.id for n in nodes])))
    edges = edges_result.scalars().all()

    return KnowledgeGraphRead(
        visualization_id=viz_id,
        nodes=[KnowledgeNodeRead.model_validate(n) for n in nodes],
        edges=[KnowledgeEdgeRead.model_validate(e) for e in edges],
    )
