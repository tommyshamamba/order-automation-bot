# Order Automation Service

[![CI](https://github.com/tommyshamamba/order-automation-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/tommyshamamba/order-automation-bot/actions/workflows/ci.yml)

A small FastAPI service that moves custom-print orders through a fixed fulfilment pipeline.
Each stage change is recorded with a timestamp, and order creation is idempotent.

> Portfolio project. Storage is in memory and stage work is simulated with a configurable delay.
> It is not a production system and claims no usage figures.

## What it does

- `POST /orders` validates the request (customer, design URL, quantity 1–100,000) and creates an order.
  A repeated `Idempotency-Key` header returns the original order instead of creating a duplicate.
- A background task advances the order: `created → proof_generation → production_queue → shipping → done`.
- `GET /orders/{id}` returns the current stage and full transition history. `GET /orders` lists all orders.
- `GET /stats` counts orders per stage. `GET /healthz` is the liveness check.

## Architecture

```
client ─► FastAPI router ─► OrderStore (thread-safe dict + idempotency index)
                │
                └─► BackgroundTasks: run_pipeline() advances stages with STAGE_DELAY_SECONDS between them
```

The store and the pipeline runner are separate, so a database repository or a real queue
(for example Celery on Redis) could replace them without changing the API.

## Run

```sh
pip install -r requirements.txt
uvicorn src.main:app --reload            # http://localhost:8000/docs
# or
docker compose up --build
```

| Variable | Default | Meaning |
| --- | --- | --- |
| `STAGE_DELAY_SECONDS` | `0.5` | Simulated work time per stage |

## Tests

```sh
pip install -r requirements.txt -r requirements-dev.txt
ruff check . && pytest -q
```

The tests cover the full pipeline, idempotency, input validation, 404 handling and stage counts.
GitHub Actions runs lint, tests and a Docker build on every push.

## License

MIT
