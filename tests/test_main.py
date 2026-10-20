import os

os.environ["STAGE_DELAY_SECONDS"] = "0"

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402

client = TestClient(app)
ORDER = {"customer": "Test Co", "design_url": "https://example.com/a.png", "quantity": 50}


def test_health():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_order_runs_full_pipeline():
    created = client.post("/orders", json=ORDER)
    assert created.status_code == 201
    order = client.get(f"/orders/{created.json()['id']}").json()
    assert order["stage"] == "done"
    assert [t["stage"] for t in order["history"]] == [
        "created", "proof_generation", "production_queue", "shipping", "done"]


def test_idempotency_key_returns_same_order():
    headers = {"Idempotency-Key": "abc-123"}
    first = client.post("/orders", json=ORDER, headers=headers).json()
    second = client.post("/orders", json=ORDER, headers=headers).json()
    assert first["id"] == second["id"]


def test_validation_rejects_bad_input():
    assert client.post("/orders", json={**ORDER, "quantity": 0}).status_code == 422
    assert client.post("/orders", json={**ORDER, "design_url": "nope"}).status_code == 422


def test_unknown_order_404():
    assert client.get("/orders/missing").status_code == 404


def test_stats_counts_stages():
    client.post("/orders", json=ORDER)
    stats = client.get("/stats").json()
    assert stats["done"] >= 1
    assert set(stats) == {"created", "proof_generation", "production_queue", "shipping", "done"}
