from enum import Enum
from typing import List, Optional

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
    inferred_from_domain: Optional[bool] | None = None

class SampleLink(BaseModel):
    url: HttpUrl = None
    reason: Optional[str] = None

class CreateOrder(BaseModel):
    order_id: str = Field(..., description="Idempotency key")
    analysis_type: AnalysisType
    sample_link: List[HttpUrl]
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
    schema_registry: Optional[str] | None = None
    topic: Optional[str] | None = None
    topic_exists: Optional[bool] | None = None
    partitions: Optional[int] | None = None