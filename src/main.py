"""Order automation service.

A FastAPI service that moves custom-print orders through a fixed pipeline:
created -> proof_generation -> production_queue -> shipping -> done.
Each order records a timestamped history of its stage transitions. Order creation
is idempotent when the client sends an ``Idempotency-Key`` header.

Storage is in memory and stage work is simulated with configurable delays, so the
service runs with no external dependencies.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from datetime import datetime, timezone
from enum import Enum

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, HttpUrl


class Stage(str, Enum):
    created = "created"
    proof_generation = "proof_generation"
    production_queue = "production_queue"
    shipping = "shipping"
    done = "done"


PIPELINE: list[Stage] = [
    Stage.proof_generation,
    Stage.production_queue,
    Stage.shipping,
    Stage.done,
]


def stage_delay_seconds() -> float:
    """Simulated work per stage; set STAGE_DELAY_SECONDS=0 in tests."""
    return float(os.getenv("STAGE_DELAY_SECONDS", "0.5"))


class Transition(BaseModel):
    stage: Stage
    at: datetime


class Order(BaseModel):
    id: str
    customer: str
    design_url: HttpUrl
    quantity: int
    stage: Stage = Stage.created
    history: list[Transition] = Field(default_factory=list)


class CreateOrder(BaseModel):
    customer: str = Field(min_length=1, max_length=200)
    design_url: HttpUrl
    quantity: int = Field(ge=1, le=100_000)


class OrderStore:
    """Thread-safe in-memory store with idempotency-key lookup."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._by_key: dict[str, str] = {}
        self._lock = threading.Lock()

    def create(self, req: CreateOrder, key: str | None) -> tuple[Order, bool]:
        with self._lock:
            if key and key in self._by_key:
                return self._orders[self._by_key[key]], False
            order = Order(id=str(uuid.uuid4()), customer=req.customer,
                          design_url=req.design_url, quantity=req.quantity)
            order.history.append(Transition(stage=Stage.created, at=_now()))
            self._orders[order.id] = order
            if key:
                self._by_key[key] = order.id
            return order, True

    def get(self, order_id: str) -> Order | None:
        with self._lock:
            return self._orders.get(order_id)

    def all(self) -> list[Order]:
        with self._lock:
            return list(self._orders.values())

    def advance(self, order_id: str, stage: Stage) -> None:
        with self._lock:
            order = self._orders[order_id]
            order.stage = stage
            order.history.append(Transition(stage=stage, at=_now()))


def _now() -> datetime:
    return datetime.now(timezone.utc)


store = OrderStore()
app = FastAPI(title="Order automation service", version="1.0.0")


def run_pipeline(order_id: str) -> None:
    for stage in PIPELINE:
        time.sleep(stage_delay_seconds())
        store.advance(order_id, stage)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/orders", status_code=201)
def create_order(req: CreateOrder, background: BackgroundTasks,
                 idempotency_key: str | None = Header(default=None)) -> Order:
    order, created = store.create(req, idempotency_key)
    if created:
        background.add_task(run_pipeline, order.id)
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: str) -> Order:
    order = store.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


@app.get("/orders")
def list_orders() -> list[Order]:
    return store.all()


@app.get("/stats")
def stats() -> dict[str, int]:
    counts = {s.value: 0 for s in Stage}
    for order in store.all():
        counts[order.stage.value] += 1
    return counts
