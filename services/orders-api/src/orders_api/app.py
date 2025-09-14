import json
import os
from contextlib import asynccontextmanager
from typing import Callable

import fastapi
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer
from fastapi import FastAPI

from orders_api.routes import router as orders_router
from orders_api.routes.orders import health_router

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
ORDER_SCHEMA_PATH = os.getenv("ORDER_SCHEMA_PATH", "contracts/jsonschema/order.received.v1.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        enable_idempotence=True,
        acks="all",
        linger_ms=10,
        value_serializer=None,
        key_serializer=None,
    )
    admin = AIOKafkaAdminClient(bootstrap_servers=BOOTSTRAP)

    with open(ORDER_SCHEMA_PATH, "r", encoding="utf-8") as f:
        order_schema_str = f.read()

    sr_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    json_serializer = JSONSerializer(
        schema_str=order_schema_str,
        schema_registry_client=sr_client,
        to_dict=lambda m, ctx: m.model_dump()
    )
    key_serializer = StringSerializer("utf-8")

    app.state.producer = producer
    app.state.admin = admin
    app.state.sr_client = sr_client
    app.state.value_serializer: JSONSerializer = json_serializer
    app.state.key_serializer: Callable[[str], bytes] = lambda s: key_serializer(s, None)

    try:
        yield
    finally:
        await admin.close()
        await producer.stop()

app = fastapi.FastAPI(
    title="Orders API",
    version="0.1.0",
    description="Receives bioinformatics orders and publishes to Kafka (AIOKafka + Confluent SR).",
    lifespan=lifespan
)

app.include_router(orders_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
