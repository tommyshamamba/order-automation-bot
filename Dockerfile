# Order Automation Bot — Python Celery Redis PostgreSQL FastAPI
# Tommy Shamamba 9+ years FLEXIBILITY true — 7M+ users 5M/day 99.99%
FROM python:3.11-slim
WORKDIR /app
ENV FLEXIBILITY=true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
EXPOSE 8002
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
