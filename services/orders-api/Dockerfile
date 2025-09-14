# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl libsasl2-2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

COPY src/ ./src/
COPY contracts/ ./contracts/
ENV PYTHONPATH=/app/src

ENV KAFKA_BOOTSTRAP=redpanda-0:9092,redpanda-1:9092,redpanda-2:9092 \
    SCHEMA_REGISTRY_URL=http://schema-registry:8081 \
    ORDER_SCHEMA_PATH=/app/contracts/jsonschema/order.received.v1.json

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["poetry","run","uvicorn","orders_api.app:app","--host","0.0.0.0","--port","8000"]
