"""
Relationship Engine — discovers hidden relationships between extracted knowledge items.

Uses a combination of:
- Semantic similarity (embedding-based)
- Graph analysis (NetworkX)
- LLM-based relationship inference
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


class RelationType(str, Enum):
    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    RELATED_TO = "related_to"
    CONTAINS = "contains"
    PRECEDES = "precedes"
    COMPARES = "compares"
    BELONGS_TO = "belongs_to"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"


@dataclass
class DiscoveredRelation:
    """A discovered relationship between two knowledge items."""
    source_label: str
    target_label: str
    relation_type: RelationType
    label: str = ""
    weight: float = 1.0
    confidence: float = 0.5
    evidence: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class RelationshipResult:
    """Complete result of relationship discovery."""
    relations: list[DiscoveredRelation] = field(default_factory=list)
    clusters: list[list[str]] = field(default_factory=list)
    graph_metrics: dict[str, Any] = field(default_factory=dict)


class RelationshipEngine:
    """Finds hidden relationships between knowledge items using graph + LLM."""

    def __init__(self):
        self.graph = nx.DiGraph()

    async def discover(self, items: list[dict[str, Any]], raw_content: dict[str, Any] | None = None) -> RelationshipResult:
        """Discover relationships between extracted knowledge items."""
        self.graph.clear()

        # Add nodes
        for item in items:
            self.graph.add_node(item.get("label", ""), **item)

        # Step 1: Explicit relationships from extraction
        explicit_relations = self._find_explicit_relationships(items)

        # Step 2: Semantic similarity-based relationships
        semantic_relations = await self._find_semantic_relationships(items)

        # Step 3: LLM-inferred relationships
        llm_relations = await self._find_llm_relationships(items, raw_content)

        # Combine all
        all_relations = explicit_relations + semantic_relations + llm_relations

        # Add edges to graph
        for rel in all_relations:
            if rel.source_label in self.graph and rel.target_label in self.graph:
                self.graph.add_edge(rel.source_label, rel.target_label, **{
                    "relation_type": rel.relation_type.value,
                    "weight": rel.weight,
                    "confidence": rel.confidence,
                })

        # Compute clusters
        clusters = self._find_clusters()

        # Compute metrics
        metrics = self._compute_graph_metrics()

        return RelationshipResult(
            relations=all_relations,
            clusters=clusters,
            graph_metrics=metrics,
        )

    def _find_explicit_relationships(self, items: list[dict[str, Any]]) -> list[DiscoveredRelation]:
        """Find relationships explicitly mentioned in the extracted items."""
        relations = []
        for item in items:
            props = item.get("properties", {})
            for rel_key in ["depends_on", "causes", "contains", "precedes", "related_to"]:
                if rel_key in props:
                    targets = props[rel_key] if isinstance(props[rel_key], list) else [props[rel_key]]
                    for target in targets:
                        relations.append(DiscoveredRelation(
                            source_label=item["label"],
                            target_label=str(target),
                            relation_type=RelationType(rel_key),
                            confidence=0.9,
                            evidence="explicitly stated in source",
                        ))
        return relations

    async def _find_semantic_relationships(self, items: list[dict[str, Any]]) -> list[DiscoveredRelation]:
        """Find relationships based on shared properties or categories."""
        relations = []
        items_by_type: dict[str, list[dict]] = {}
        for item in items:
            t = item.get("item_type", "unknown")
            items_by_type.setdefault(t, []).append(item)

        # Items in the same category with shared properties are related
        for item_type, group in items_by_type.items():
            for i, item_a in enumerate(group):
                for item_b in group[i + 1:]:
                    shared = set(item_a.get("properties", {}).keys()) & set(item_b.get("properties", {}).keys())
                    if shared:
                        relations.append(DiscoveredRelation(
                            source_label=item_a["label"],
                            target_label=item_b["label"],
                            relation_type=RelationType.RELATED_TO,
                            weight=len(shared) / max(len(item_a.get("properties", {})), 1),
                            confidence=0.6,
                            evidence=f"shared properties: {shared}",
                        ))
        return relations

    async def _find_llm_relationships(self, items: list[dict[str, Any]], raw_content: dict[str, Any] | None) -> list[DiscoveredRelation]:
        """Use LLM to infer hidden relationships between items."""
        if not items or len(items) < 2:
            return []

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            from app.core.config import settings

            llm = ChatOpenAI(model="gpt-4o", temperature=0.1, api_key=settings.OPENAI_API_KEY)

            item_descriptions = "\n".join(
                f"- {item['label']} ({item.get('item_type', 'unknown')}): {item.get('description', '')}"
                for item in items[:50]  # limit items
            )

            messages = [
                SystemMessage(content=(
                    "You are a relationship discovery engine. Given a list of knowledge items, "
                    "find non-obvious but meaningful relationships between them. "
                    "Return a JSON list of relationships with: source_label, target_label, "
                    "relation_type (one of: depends_on, causes, related_to, contains, precedes, "
                    "compares, belongs_to, contradicts, supports, derived_from), weight (0-1), "
                    "and evidence (why you think this relationship exists)."
                )),
                HumanMessage(content=f"Find relationships between these items:\n\n{item_descriptions}"),
            ]

            response = await llm.ainvoke(messages)
            return self._parse_llm_relations(response.content)
        except Exception as e:
            logger.error("LLM relationship discovery failed: %s", e)
            return []

    def _parse_llm_relations(self, response_text: str) -> list[DiscoveredRelation]:
        """Parse LLM relationship response."""
        import json
        import re

        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            return []

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return []

        relations = []
        for item in data:
            try:
                relations.append(DiscoveredRelation(
                    source_label=item["source_label"],
                    target_label=item["target_label"],
                    relation_type=RelationType(item.get("relation_type", "related_to")),
                    weight=float(item.get("weight", 0.5)),
                    confidence=0.7,
                    evidence=item.get("evidence", "LLM-inferred"),
                ))
            except (KeyError, ValueError):
                continue
        return relations

    def _find_clusters(self) -> list[list[str]]:
        """Find clusters of related nodes using community detection."""
        if len(self.graph.nodes) < 2:
            return []

        try:
            undirected = self.graph.to_undirected()
            communities = nx.community.greedy_modularity_communities(undirected)
            return [list(community) for community in communities]
        except Exception as e:
            logger.warning("Community detection failed: %s", e)
            return []

    def _compute_graph_metrics(self) -> dict[str, Any]:
        """Compute graph-level metrics."""
        metrics: dict[str, Any] = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
        }
        if self.graph.number_of_nodes() > 0:
            try:
                metrics["density"] = nx.density(self.graph)
            except Exception:
                pass
            try:
                metrics["most_connected"] = sorted(
                    self.graph.degree(), key=lambda x: x[1], reverse=True
                )[:5]
            except Exception:
                pass
        return metrics
