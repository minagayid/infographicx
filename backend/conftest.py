"""Test bootstrap: importable backend + eager Celery (no broker needed)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Run Celery tasks synchronously in-process during tests.
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "1")

try:
    from app.core.celery_app import celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
except Exception:
    pass
