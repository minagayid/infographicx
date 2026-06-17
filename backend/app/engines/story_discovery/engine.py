"""
Story Discovery Engine — determines narrative structure from extracted knowledge.

Identifies: timelines, cause-effect chains, comparisons, hierarchical structures,
and problem-solution patterns to create compelling data narratives.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class StoryType(str, Enum):
    TIMELINE = "timeline"
    CAUSE_EFFECT = "cause_effect"
    COMPARISON = "comparison"
    HIERARCHICAL = "hierarchical"
    PROBLEM_SOLUTION = "problem_solution"
    PROCESS_FLOW = "process_flow"
    DATA_OVERVIEW = "data_overview"
    NARRATIVE = "narrative"


@dataclass
class StoryArc:
    """A discovered narrative arc in the data."""
    story_type: StoryType
    title: str
    description: str
    key_elements: list[dict[str, Any]] = field(default_factory=list)
    recommended_viz_types: list[str] = field(default_factory=list)
    importance: float = 0.5


@dataclass
class StoryResult:
    """Complete story discovery result."""
    primary_story: StoryArc | None = None
    secondary_stories: list[StoryArc] = field(default_factory=list)
    theme: str = ""
    audience_level: str = "general"


STORY_SYSTEM_PROMPT = """You are a narrative analyst. Given extracted knowledge items and their relationships,
identify the most compelling story structures in the data.

Consider these story types:
- timeline: chronological sequence of events
- cause_effect: causal chains between items
- comparison: contrasting or comparing groups of items
- hierarchical: parent-child or containment relationships
- problem_solution: challenges and their resolutions
- process_flow: sequential steps in a process
- data_overview: broad statistical overview
- narrative: a flowing story with beginning, middle, end

For each discovered story, provide:
- story_type
- title
- description
- key_elements (referenced items)
- recommended_viz_types (e.g., timeline, flowchart, knowledge_graph, dashboard, mind_map)
- importance (0.0-1.0)

Return JSON: {
  "primary_story": {...most important story...},
  "secondary_stories": [...other stories...],
  "theme": "overall theme",
  "audience_level": "general|technical|executive"
}"""


class StoryDiscoveryEngine:
    """Discovers narrative structures in extracted knowledge."""

    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,  # higher temp for creative story discovery
            api_key=settings.OPENAI_API_KEY,
        )

    async def discover(
        self,
        items: list[dict[str, Any]],
        relations: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> StoryResult:
        """Discover the best narrative structure from knowledge items and relations."""
        import json

        items_summary = json.dumps(
            [{"label": i.get("label"), "type": i.get("item_type"), "description": i.get("description", "")[:200]}
             for i in items[:100]],
            indent=2,
            ensure_ascii=False,
        )

        relations_summary = ""
        if relations:
            relations_summary = json.dumps(
                [{"source": r.get("source_label"), "target": r.get("target_label"), "type": r.get("relation_type")}
                 for r in relations[:50]],
                indent=2,
                ensure_ascii=False,
            )

        messages = [
            SystemMessage(content=STORY_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Discover stories in this knowledge:\n\n"
                f"Items:\n{items_summary}\n\n"
                f"Relationships:\n{relations_summary}\n\n"
                f"Context: {json.dumps(context or {})}"
            )),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_response(response.content)
        except Exception as e:
            logger.error("Story discovery failed: %s", e)
            return StoryResult(theme="General Overview")

    def _parse_response(self, response_text: str) -> StoryResult:
        """Parse LLM response into StoryResult."""
        import json
        import re

        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return StoryResult()

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return StoryResult()

        primary = None
        if "primary_story" in data and data["primary_story"]:
            ps = data["primary_story"]
            primary = StoryArc(
                story_type=StoryType(ps.get("story_type", "data_overview")),
                title=ps.get("title", "Untitled Story"),
                description=ps.get("description", ""),
                key_elements=ps.get("key_elements", []),
                recommended_viz_types=ps.get("recommended_viz_types", []),
                importance=float(ps.get("importance", 0.5)),
            )

        secondary = []
        for ss in data.get("secondary_stories", []):
            try:
                secondary.append(StoryArc(
                    story_type=StoryType(ss.get("story_type", "data_overview")),
                    title=ss.get("title", ""),
                    description=ss.get("description", ""),
                    key_elements=ss.get("key_elements", []),
                    recommended_viz_types=ss.get("recommended_viz_types", []),
                    importance=float(ss.get("importance", 0.3)),
                ))
            except (ValueError, KeyError):
                continue

        return StoryResult(
            primary_story=primary,
            secondary_stories=secondary,
            theme=data.get("theme", ""),
            audience_level=data.get("audience_level", "general"),
        )
