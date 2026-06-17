"""
Knowledge Extraction Engine — identifies entities, processes, relationships,
dependencies, events, and metrics from ingested content.

Uses LLM-based extraction with structured output (via LangChain).
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractedType(str, Enum):
    ENTITY = "entity"
    PROCESS = "process"
    RELATIONSHIP = "relationship"
    DEPENDENCY = "dependency"
    EVENT = "event"
    METRIC = "metric"
    CONCEPT = "concept"


@dataclass
class ExtractedItem:
    """A single piece of extracted knowledge."""
    item_type: ExtractedType
    label: str
    description: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.5
    source_ref: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class ExtractionResult:
    """Complete extraction result from a source."""
    items: list[ExtractedItem] = field(default_factory=list)
    summary: str = ""
    key_topics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


EXTRACTION_SYSTEM_PROMPT = """You are a knowledge extraction specialist. Given raw content from a source, 
extract all meaningful entities, processes, relationships, dependencies, events, and metrics.

For each extracted item, provide:
- item_type: one of [entity, process, relationship, dependency, event, metric, concept]
- label: short name
- description: brief explanation
- properties: relevant attributes as key-value pairs
- importance_score: 0.0-1.0 based on centrality to the content
- confidence: 0.0-1.0 based on extraction certainty

Return your response as a JSON object with:
{
  "items": [...extracted items...],
  "summary": "brief summary of the content",
  "key_topics": ["topic1", "topic2", ...]
}"""


class KnowledgeExtractionEngine:
    """Extracts structured knowledge from raw content using LLM."""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY,
        )

    async def extract(self, raw_content: dict[str, Any], source_metadata: dict[str, Any] | None = None) -> ExtractionResult:
        """Extract knowledge from raw source content."""
        content_text = self._serialize_content(raw_content)

        if not content_text.strip():
            logger.warning("Empty content provided for extraction")
            return ExtractionResult()

        messages = [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=f"Extract knowledge from the following content:\n\n{content_text[:50000]}"),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            parsed = self._parse_llm_response(response.content)
            return parsed
        except Exception as e:
            logger.error("Knowledge extraction failed: %s", e)
            return ExtractionResult(summary=f"Extraction failed: {e}")

    async def batch_extract(self, sources: list[dict[str, Any]]) -> list[ExtractionResult]:
        """Extract knowledge from multiple sources in sequence."""
        results = []
        for source in sources:
            result = await self.extract(source.get("raw_content", {}), source.get("metadata"))
            results.append(result)
        return results

    def _serialize_content(self, content: dict[str, Any]) -> str:
        """Convert structured content dict to text for LLM processing."""
        import json

        if isinstance(content, dict):
            # Flatten for LLM consumption
            parts = []
            for key, value in content.items():
                if isinstance(value, str):
                    parts.append(value)
                elif isinstance(value, list):
                    for item in value[:200]:  # limit items
                        if isinstance(item, dict):
                            parts.append(json.dumps(item, indent=2, default=str, ensure_ascii=False))
                        else:
                            parts.append(str(item))
                elif isinstance(value, dict):
                    parts.append(json.dumps(value, indent=2, default=str, ensure_ascii=False))
                else:
                    parts.append(str(value))
            return "\n\n".join(parts)
        return str(content)

    def _parse_llm_response(self, response_text: str) -> ExtractionResult:
        """Parse the LLM response into a structured ExtractionResult."""
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return ExtractionResult(summary=response_text[:500])

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return ExtractionResult(summary=response_text[:500])

        items = []
        for item_data in data.get("items", []):
            try:
                items.append(ExtractedItem(
                    item_type=ExtractedType(item_data.get("item_type", "entity")),
                    label=item_data.get("label", "Unknown"),
                    description=item_data.get("description", ""),
                    properties=item_data.get("properties", {}),
                    importance_score=float(item_data.get("importance_score", 0.5)),
                    confidence=float(item_data.get("confidence", 1.0)),
                ))
            except (ValueError, KeyError) as e:
                logger.warning("Skipping malformed item: %s", e)
                continue

        return ExtractionResult(
            items=items,
            summary=data.get("summary", ""),
            key_topics=data.get("key_topics", []),
        )
