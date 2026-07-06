"""Export service — resolve a rendered export artifact for download."""
from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import settings

# Export format -> (extension, media type).
_FORMAT_MEDIA = {
    "html": ("html", "text/html"),
    "website": ("zip", "application/zip"),
    "svg": ("svg", "image/svg+xml"),
    "pdf": ("pdf", "application/pdf"),
    "png": ("png", "image/png"),
    "pptx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
}


class ExportService:
    """Locates export artifacts produced by the Publishing Agent."""

    def __init__(self, export_dir: str | None = None):
        self.export_dir = Path(export_dir or settings.UPLOAD_DIR) / "exports"

    def media_type(self, format: str) -> str:
        return _FORMAT_MEDIA.get(format, ("bin", "application/octet-stream"))[1]

    async def get_export_file(self, visualization_id: uuid.UUID, format: str) -> tuple[str, str]:
        """Return (file_path, media_type) for a rendered export.

        Raises FileNotFoundError if the artifact has not been produced yet, so
        the endpoint can surface a clear 404 instead of streaming a missing file.
        """
        if format not in _FORMAT_MEDIA:
            raise ValueError(f"Unsupported format: {format}")
        ext, media = _FORMAT_MEDIA[format]
        path = self.export_dir / f"{visualization_id}.{ext}"
        if not path.exists():
            raise FileNotFoundError(f"Export not found for {visualization_id} ({format})")
        return str(path), media
