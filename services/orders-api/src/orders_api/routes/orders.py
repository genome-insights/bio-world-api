import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient
from confluent_kafka.serialization import SerializationContext, MessageField
from fastapi import Request, HTTPException

from fastapi import APIRouter
from orders_api.domain import OrderAck, CreateOrder, HealthResponse

router = APIRouter(prefix="/orders", tags=["orders"])
ORDER_TOPIC = "orders.received.v1"


def _producer(request: Request) -> AIOKafkaProducer:
    prod = getattr(request.app.state, "producer", None)
    if prod is None:
        raise HTTPException(status_code=404, detail="Kafka producer not available")
    return prod


@router.post("create_order", response_model=OrderAck, summary="Create/Queue an order")
async def create_order(request: Request, body: CreateOrder):
    """
    Validates and publishes an `order.received.v1` event to Kafka.
    The `order_id` acts as the key for partitioning/idempotence.
    """
    producer = _producer(request)

    ctx = SerializationContext(ORDER_TOPIC, MessageField.VALUE)
    value_bytes = await asyncio.to_thread(
        request.app.state.value_serializer,
        body,
        ctx
    )
    key_bytes = request.app.state.key_serializer(body.order_id)
    headers = [("source", b"orders-api")]

    await producer.send_and_wait(
        ORDER_TOPIC,
        key=key_bytes,
        value=value_bytes,
        headers=headers
    )
    return OrderAck(status="queued", order_id=body.order_id)


health_router = APIRouter(prefix="/health", tags=["health"])

@health_router.post("", response_model=HealthResponse, summary="Get the health of the orders API service")
async def get_health(request: Request):
    """
    Get Order API health:
    - producer: initialized?
    - kafka: can list topics? does ORDER_TOPIC exist? partition count?
    - schema_registry: reachable?
    """
    prod_ok = bool(getattr(request.app.state, "producer", None))
    kafka_status = "down"
    topic_exists = False
    partitions = None

    try:
        admin: AIOKafkaAdminClient = request.app.state.admin
        md = await admin.list_topics(timeout=5)
        kafka_status = "up"

        if ORDER_TOPIC in md.topics:
            topic_exists = True
            partitions = len(md.topics[ORDER_TOPIC].partitions)
    except Exception:
        kafka_status = "down"

    sr_status = "down"
    try:
        await asyncio.to_thread(request.app.state.sr_client.get_subjects)
        sr_status = "up"
    except Exception:
        sr_status = "down"

    status = "ok" if (prod_ok and kafka_status == "up" and sr_status == "up") else "degrade"
    return HealthResponse(
        status=status,
        kafka=kafka_status,
        schema_registry=sr_status,
        topic=ORDER_TOPIC,
        topic_exists=topic_exists,
        partitions=partitions,
    )