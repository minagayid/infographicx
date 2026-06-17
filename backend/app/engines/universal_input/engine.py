"""
Universal Input Engine — accepts and normalizes any input source.

Supported source types:
- Documents: PDF, DOCX, PPTX, CSV, XLSX
- Media: Video, Audio
- Code: Git Repository
- Web: Website URL, Research Paper URL/DOI
- Data: API endpoint, Database connection
"""

import logging
import tempfile
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles

from app.core.config import settings

logger = logging.getLogger(__name__)


class SourceType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    CSV = "csv"
    XLSX = "xlsx"
    VIDEO = "video"
    AUDIO = "audio"
    GIT_REPO = "git_repo"
    WEBSITE = "website"
    RESEARCH_PAPER = "research_paper"
    API = "api"
    DATABASE = "database"


class InputProcessor(ABC):
    """Base class for all input processors."""

    source_type: SourceType

    @abstractmethod
    async def validate(self, source_data: dict[str, Any]) -> bool:
        """Validate that the source data is processable."""
        ...

    @abstractmethod
    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """Extract raw content from the source."""
        ...

    @abstractmethod
    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata about the source."""
        ...


class PdfProcessor(InputProcessor):
    source_type = SourceType.PDF

    async def validate(self, source_data: dict[str, Any]) -> bool:
        file_path = source_data.get("file_path")
        return file_path is not None and Path(file_path).suffix.lower() == ".pdf"

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from pypdf import PdfReader

        file_path = source_data["file_path"]
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            pages.append({
                "page_number": page.page_number,
                "text": page.extract_text() or "",
                "tables": [],  # TODO: table extraction
                "images": [],  # TODO: image extraction
            })
        return {"pages": pages, "total_pages": len(reader.pages)}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from pypdf import PdfReader

        reader = PdfReader(source_data["file_path"])
        meta = reader.metadata
        return {
            "title": meta.title if meta else None,
            "author": meta.author if meta else None,
            "page_count": len(reader.pages),
            "file_size": Path(source_data["file_path"]).stat().st_size,
        }


class DocxProcessor(InputProcessor):
    source_type = SourceType.DOCX

    async def validate(self, source_data: dict[str, Any]) -> bool:
        file_path = source_data.get("file_path")
        return file_path is not None and Path(file_path).suffix.lower() == ".docx"

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from docx import Document

        doc = Document(source_data["file_path"])
        paragraphs = [{"text": p.text, "style": p.style.name} for p in doc.paragraphs if p.text.strip()]
        tables = []
        for table in doc.tables:
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            tables.append(rows)
        return {"paragraphs": paragraphs, "tables": tables}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from docx import Document

        doc = Document(source_data["file_path"])
        return {
            "paragraph_count": len(doc.paragraphs),
            "table_count": len(doc.tables),
            "file_size": Path(source_data["file_path"]).stat().st_size,
        }


class PptxProcessor(InputProcessor):
    source_type = SourceType.PPTX

    async def validate(self, source_data: dict[str, Any]) -> bool:
        file_path = source_data.get("file_path")
        return file_path is not None and Path(file_path).suffix.lower() == ".pptx"

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from pptx import Presentation

        prs = Presentation(source_data["file_path"])
        slides = []
        for i, slide in enumerate(prs.slides):
            shapes = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    shapes.append({"text": shape.text, "shape_type": str(shape.shape_type)})
            slides.append({"slide_number": i + 1, "shapes": shapes})
        return {"slides": slides, "total_slides": len(prs.slides)}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from pptx import Presentation

        prs = Presentation(source_data["file_path"])
        return {
            "slide_count": len(prs.slides),
            "file_size": Path(source_data["file_path"]).stat().st_size,
        }


class CsvProcessor(InputProcessor):
    source_type = SourceType.CSV

    async def validate(self, source_data: dict[str, Any]) -> bool:
        file_path = source_data.get("file_path")
        return file_path is not None and Path(file_path).suffix.lower() == ".csv"

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        import csv

        rows = []
        with open(source_data["file_path"], "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            for row in reader:
                rows.append(dict(row))
        return {"headers": headers, "rows": rows, "row_count": len(rows)}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        file_path = source_data["file_path"]
        return {
            "file_size": Path(file_path).stat().st_size,
            "source_type": "csv",
        }


class XlsxProcessor(InputProcessor):
    source_type = SourceType.XLSX

    async def validate(self, source_data: dict[str, Any]) -> bool:
        file_path = source_data.get("file_path")
        return file_path is not None and Path(file_path).suffix.lower() == ".xlsx"

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from openpyxl import load_workbook

        wb = load_workbook(source_data["file_path"], read_only=True)
        sheets = {}
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = []
            for row in ws.iter_rows(values_only=True):
                rows.append(list(row))
            sheets[sheet_name] = {"rows": rows, "row_count": len(rows)}
        wb.close()
        return {"sheets": sheets, "sheet_names": list(sheets.keys())}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from openpyxl import load_workbook

        wb = load_workbook(source_data["file_path"], read_only=True)
        names = wb.sheetnames
        wb.close()
        return {"sheet_names": names, "file_size": Path(source_data["file_path"]).stat().st_size}


class VideoProcessor(InputProcessor):
    source_type = SourceType.VIDEO

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("file_path") or source_data.get("url"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        import whisper

        model = whisper.load_model("base")
        file_path = source_data.get("file_path", "")
        result = model.transcribe(file_path)
        return {
            "transcript": result["text"],
            "segments": result.get("segments", []),
            "language": result.get("language", "unknown"),
        }

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "file_path": source_data.get("file_path"),
            "url": source_data.get("url"),
        }


class AudioProcessor(InputProcessor):
    source_type = SourceType.AUDIO

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("file_path") or source_data.get("url"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        import whisper

        model = whisper.load_model("base")
        file_path = source_data.get("file_path", "")
        result = model.transcribe(file_path)
        return {
            "transcript": result["text"],
            "segments": result.get("segments", []),
            "language": result.get("language", "unknown"),
        }

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "file_path": source_data.get("file_path"),
            "url": source_data.get("url"),
        }


class GitRepoProcessor(InputProcessor):
    source_type = SourceType.GIT_REPO

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("repo_url"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from git import Repo

        repo_url = source_data["repo_url"]
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Repo.clone_from(repo_url, tmp_dir, depth=1)
            files = {}
            for item in Path(tmp_dir).rglob("*"):
                if item.is_file() and not any(p.startswith(".") for p in item.parts):
                    try:
                        content = item.read_text(encoding="utf-8", errors="ignore")
                        rel = str(item.relative_to(tmp_dir))
                        files[rel] = content[:50000]  # cap per-file size
                    except Exception:
                        continue
        return {"files": files, "file_count": len(files)}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {"repo_url": source_data.get("repo_url")}


class WebsiteProcessor(InputProcessor):
    source_type = SourceType.WEBSITE

    async def validate(self, source_data: dict[str, Any]) -> bool:
        url = source_data.get("url", "")
        return url.startswith("http://") or url.startswith("https://")

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        from bs4 import BeautifulSoup
        import httpx

        url = source_data["url"]
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=30)

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        images = [img.get("src") for img in soup.find_all("img", src=True)]
        headings = [(h.name, h.get_text(strip=True)) for h in soup.find_all(["h1", "h2", "h3", "h4"])]

        return {
            "text": text,
            "links": links[:500],
            "images": images[:200],
            "headings": headings,
            "url": url,
        }

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {"url": source_data.get("url")}


class ResearchPaperProcessor(InputProcessor):
    source_type = SourceType.RESEARCH_PAPER

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("url") or source_data.get("doi") or source_data.get("file_path"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        # First try as PDF if file_path provided
        if source_data.get("file_path"):
            pdf_proc = PdfProcessor()
            return await pdf_proc.extract_raw_content(source_data)

        # Otherwise fetch from URL (e.g., arXiv)
        url = source_data.get("url", "")
        if "arxiv.org" in url:
            return await self._fetch_arxiv(url)
        return {"text": "", "source": url}

    async def _fetch_arxiv(self, url: str) -> dict[str, Any]:
        import httpx

        abstract_url = url.replace("/pdf/", "/abs/")
        async with httpx.AsyncClient() as client:
            response = await client.get(abstract_url, follow_redirects=True, timeout=30)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        abstract_tag = soup.find("blockquote", class_="abstract")
        abstract = abstract_tag.get_text(strip=True) if abstract_tag else ""
        title_tag = soup.find("h1", class_="title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        return {"title": title, "abstract": abstract, "url": url}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {"url": source_data.get("url"), "doi": source_data.get("doi")}


class ApiProcessor(InputProcessor):
    source_type = SourceType.API

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("url"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        import httpx

        url = source_data["url"]
        headers = source_data.get("headers", {})
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
        return {"data": response.json(), "url": url}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {"url": source_data.get("url")}


class DatabaseProcessor(InputProcessor):
    source_type = SourceType.DATABASE

    async def validate(self, source_data: dict[str, Any]) -> bool:
        return bool(source_data.get("connection_string") and source_data.get("query"))

    async def extract_raw_content(self, source_data: dict[str, Any]) -> dict[str, Any]:
        import sqlalchemy

        engine = sqlalchemy.create_engine(source_data["connection_string"])
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(source_data["query"]))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {"columns": columns, "rows": rows, "row_count": len(rows)}

    async def get_metadata(self, source_data: dict[str, Any]) -> dict[str, Any]:
        return {"connection_string": "***", "query": source_data.get("query")}


# Registry of all processors
PROCESSOR_REGISTRY: dict[SourceType, type[InputProcessor]] = {
    SourceType.PDF: PdfProcessor,
    SourceType.DOCX: DocxProcessor,
    SourceType.PPTX: PptxProcessor,
    SourceType.CSV: CsvProcessor,
    SourceType.XLSX: XlsxProcessor,
    SourceType.VIDEO: VideoProcessor,
    SourceType.AUDIO: AudioProcessor,
    SourceType.GIT_REPO: GitRepoProcessor,
    SourceType.WEBSITE: WebsiteProcessor,
    SourceType.RESEARCH_PAPER: ResearchPaperProcessor,
    SourceType.API: ApiProcessor,
    SourceType.DATABASE: DatabaseProcessor,
}


class UniversalInputEngine:
    """Orchestrates ingestion from any supported source type."""

    def __init__(self):
        self.processors: dict[SourceType, InputProcessor] = {
            st: cls() for st, cls in PROCESSOR_REGISTRY.items()
        }

    def get_processor(self, source_type: SourceType) -> InputProcessor:
        processor = self.processors.get(source_type)
        if not processor:
            raise ValueError(f"No processor available for source type: {source_type}")
        return processor

    async def ingest(self, source_type: SourceType, source_data: dict[str, Any]) -> dict[str, Any]:
        """Ingest a source, validate, extract content, and return normalized output."""
        processor = self.get_processor(source_type)

        if not await processor.validate(source_data):
            raise ValueError(f"Source validation failed for type {source_type}")

        metadata = await processor.get_metadata(source_data)
        raw_content = await processor.extract_raw_content(source_data)

        return {
            "source_id": str(uuid.uuid4()),
            "source_type": source_type.value,
            "metadata": metadata,
            "raw_content": raw_content,
            "status": "ingested",
        }

    async def upload_and_ingest(self, source_type: SourceType, file_path: str) -> dict[str, Any]:
        """Upload a file and run the ingestion pipeline."""
        return await self.ingest(source_type, {"file_path": file_path})


# Celery task entry point
from app.core.celery_app import celery_app


@celery_app.task(bind=True, name="universal_input.process_sources")
def process_sources_task(self, source_ids: list[str], options: dict | None = None):
    """Celery task — process a batch of sources through the Universal Input Engine."""
    import asyncio

    async def _run():
        engine = UniversalInputEngine()
        results = []
        for sid in source_ids:
            try:
                result = await engine.ingest(
                    SourceType.PDF, {"source_id": sid}
                )
                results.append({"source_id": sid, "status": "processed", "result": result})
            except Exception as e:
                results.append({"source_id": sid, "status": "failed", "error": str(e)})
        return results

    return asyncio.run(_run())
