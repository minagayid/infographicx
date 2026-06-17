"""Source endpoints — upload and manage input sources."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceRead, SourceProcessRequest
from app.services.source_service import SourceService

router = APIRouter()


@router.get("/{project_id}", response_model=list[SourceRead])
async def list_sources(
    project_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sources for a project."""
    result = await db.execute(select(Source).where(Source.project_id == project_id))
    return result.scalars().all()


@router.post("/{project_id}", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    project_id: uuid.UUID,
    source_in: SourceCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a URL-based source to a project."""
    source = Source(
        project_id=project_id,
        source_type=source_in.source_type,
        name=source_in.name,
        url=source_in.url,
        metadata_json=source_in.metadata,
    )
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return source


@router.post("/{project_id}/upload", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def upload_source(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file as a source for a project."""
    service = SourceService(db)
    source = await service.upload_file(project_id=project_id, file=file)
    return source


@router.post("/{project_id}/process")
async def process_sources(
    project_id: uuid.UUID,
    request: SourceProcessRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI processing of sources (async Celery task)."""
    from app.engines.universal_input import process_sources_task

    task = process_sources_task.delay(
        source_ids=[str(sid) for sid in request.source_ids],
        options=request.options,
    )
    return {"task_id": task.id, "status": "queued"}


@router.get("/detail/{source_id}", response_model=SourceRead)
async def get_source(
    source_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get source details by ID."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(source)
