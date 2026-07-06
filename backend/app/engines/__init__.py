"""Engines package — core processing engines for the InfographicX pipeline.

Engines are exported lazily (PEP 562): importing this package does not import
every engine's third-party dependencies, and importing one engine submodule
no longer drags in all its siblings. Access an engine by name to load it, e.g.
``from app.engines import RelationshipEngine``.
"""
from importlib import import_module
from typing import Any

# Public engine name -> "submodule:attribute".
_ENGINES = {
    "UniversalInputEngine": "universal_input.engine:UniversalInputEngine",
    "KnowledgeExtractionEngine": "knowledge_extraction.engine:KnowledgeExtractionEngine",
    "RelationshipEngine": "relationship.engine:RelationshipEngine",
    "StoryDiscoveryEngine": "story_discovery.engine:StoryDiscoveryEngine",
    "VisualizationEngine": "visualization.engine:VisualizationEngine",
}

__all__ = list(_ENGINES)


def __getattr__(name: str) -> Any:
    target = _ENGINES.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = target.split(":")
    module = import_module(f"{__name__}.{module_path}")
    return getattr(module, attr)


def __dir__() -> list[str]:
    return sorted(__all__)
