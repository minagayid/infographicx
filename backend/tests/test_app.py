"""Smoke tests: the app imports and boots, and core modules resolve."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("healthy", "ok")


def test_lazy_engine_exports_resolve():
    import app.engines as engines

    assert engines.RelationshipEngine is not None
    assert engines.VisualizationEngine is not None


def test_unknown_engine_attribute_raises():
    import app.engines as engines

    try:
        engines.NoSuchEngine  # noqa: B018
        assert False, "expected AttributeError"
    except AttributeError:
        pass
