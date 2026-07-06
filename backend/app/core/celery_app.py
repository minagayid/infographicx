"""Celery application for InfographicX background agents.

Configured from settings so the same app works in development (Redis broker)
and in tests (eager mode, no broker required — set ``CELERY_TASK_ALWAYS_EAGER``
or call ``celery_app.conf.task_always_eager = True``).
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "infographicx",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=600,
    # Discover @celery_app.task functions in the engines and agents packages.
    imports=(
        "app.engines.universal_input.engine",
        "app.agents.extraction_agent",
        "app.agents.research_agent",
        "app.agents.story_agent",
        "app.agents.design_agent",
        "app.agents.chart_agent",
        "app.agents.fact_check_agent",
        "app.agents.publishing_agent",
    ),
)
