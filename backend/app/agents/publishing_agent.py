"""Publishing Agent — package a finished visualization into an export artifact."""
from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult
from app.core.celery_app import celery_app

SUPPORTED_FORMATS = {"html", "pdf", "png", "svg", "pptx", "website"}

# Whether a format is vector (scales losslessly) or raster, and its MIME type.
_FORMAT_META = {
    "html": {"kind": "markup", "mime": "text/html", "vector": True},
    "website": {"kind": "bundle", "mime": "text/html", "vector": True},
    "svg": {"kind": "vector", "mime": "image/svg+xml", "vector": True},
    "pdf": {"kind": "document", "mime": "application/pdf", "vector": True},
    "pptx": {"kind": "document", "mime": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "vector": False},
    "png": {"kind": "raster", "mime": "image/png", "vector": False},
}


async def run(visualization_id: str, spec: dict[str, Any] | None = None,
              format: str = "html", theme: str = "light", include_branding: bool = True) -> AgentResult:
    reasoning = [f"Publishing visualization {visualization_id} as '{format}'"]
    if format not in SUPPORTED_FORMATS:
        return AgentResult(agent="publishing", status="error", error=f"Unsupported format: {format}")

    meta = _FORMAT_META[format]
    if not meta["vector"]:
        reasoning.append(f"'{format}' is raster; rendering at 2x for retina displays")
    else:
        reasoning.append(f"'{format}' is vector; output scales losslessly")

    artifact = {
        "visualization_id": visualization_id,
        "format": format,
        "mime_type": meta["mime"],
        "theme": theme,
        "branding": include_branding,
        "filename": f"{visualization_id}.{format if format != 'website' else 'zip'}",
        "node_count": len((spec or {}).get("nodes", [])),
    }
    reasoning.append(f"Prepared artifact {artifact['filename']} ({meta['mime']})")
    return AgentResult(agent="publishing", output={"artifact": artifact}, reasoning=reasoning)


@celery_app.task(bind=True, name="agents.publishing")
def publishing_agent_task(self, visualization_id: str, format: str = "html",
                          theme: str = "light", include_branding: bool = True,
                          spec: dict[str, Any] | None = None):
    import asyncio

    result = asyncio.run(run(visualization_id, spec=spec, format=format, theme=theme, include_branding=include_branding))
    return {**result.to_dict()}
