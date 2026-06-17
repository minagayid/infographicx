"""Export endpoints — publish visualizations in multiple formats."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user

router = APIRouter()

SUPPORTED_FORMATS = ["html", "pdf", "png", "svg", "pptx", "website"]


@router.post("/{visualization_id}/export")
async def export_visualization(
    visualization_id: uuid.UUID,
    format: str = "html",
    theme: str | None = None,
    include_branding: bool = True,
    current_user: dict = Depends(get_current_user),
):
    """Export a visualization in the specified format (async via Publishing Agent)."""
    if format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Supported: {SUPPORTED_FORMATS}",
        )

    from app.agents.publishing_agent import publishing_agent_task

    task = publishing_agent_task.delay(
        visualization_id=str(visualization_id),
        format=format,
        theme=theme,
        include_branding=include_branding,
    )
    return {"task_id": task.id, "format": format, "status": "exporting"}


@router.get("/{visualization_id}/download/{format}")
async def download_export(
    visualization_id: uuid.UUID,
    format: str,
    current_user: dict = Depends(get_current_user),
):
    """Download an already-exported visualization file."""
    from app.services.export_service import ExportService

    service = ExportService()
    file_path, media_type = await service.get_export_file(visualization_id, format)
    if not file_path:
        raise HTTPException(status_code=404, detail="Export not found. Run export first.")

    import aiofiles
    async with aiofiles.open(file_path, "rb") as f:
        content = await f.read()

    filename = f"{visualization_id}.{format}"
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
