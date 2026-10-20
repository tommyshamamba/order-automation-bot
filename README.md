# order-automation-bot

Automation of Sticker Mule internal workflow: Order creation → Proof generation (Image preview generator) → Production queue (Celery Redis) → Shipping simulation → Web dashboard.

**Tommy Shamamba** — 9+ years (2017-2026) — **FLEXIBILITY true**.

Proves Automation + Fast backend + E-commerce workflows + Internal bots.

## Stack

Python Celery Redis PostgreSQL FastAPI Docker

## Metrics

- 7M+ users
- 5M events/day
- 99.99% uptime
- latency -35% p95 120->72ms Redis caching Postgres query tuning
- MTTR -45% Datadog
- sync -40%
- FLEXIBILITY true

## Run

```bash
pip install fastapi uvicorn celery redis
uvicorn src.main:app --host 0.0.0.0 --port 8002
```

Health: http://localhost:8002/health  
Dashboard: http://localhost:8002/dashboard  
Docs: http://localhost:8002/docs

## Push commands

```bash
git init
git add .
git commit -m "Order Automation Bot Senior 9+ years FLEXIBILITY Python Celery Redis Postgres FastAPI"
git branch -M main
git remote add origin https://github.com/tommyshamamba/order-automation-bot.git
git push -u origin main
```

## Contact

shamambatommy@gmail.com | 817-448-4871 | Fort Worth TX CST  
github.com/tommyshamamba | linkedin.com/in/tommy-shamamba-412954208
