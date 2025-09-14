from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class AnalysisType(str, Enum):
    BCR_ABL = "bcr_abl"
    SNP = "snp"
    OTHER = "other"

class Urgency(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Customer(BaseModel):
    name: str = None
    company: str = None
    email: str = None
    inferred_from_domain: bool | None = None

class CreateOrder(BaseModel):
    order_id: str = Field(..., description="Idempotency key")
    analysis_type: AnalysisType
    sample_link: HttpUrl
    customer: Customer
    urgency: Urgency = Urgency.MEDIUM
    summary: str
    notes: str
    confidence: float

class OrderAck(BaseModel):
    order_id: str
    status: str

class HealthResponse(BaseModel):
    status: str
    kafka: str
    schema_registry: str | None = None
    topic: str | None = None
    topic_exists: bool | None = None
    partitions: int | None = None