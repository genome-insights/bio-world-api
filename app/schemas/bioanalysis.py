from pydantic import BaseModel

from app.schemas.customer import Customer


class BioAnalysisIn(BaseModel):
    analysis_type: str
    customer: Customer
    file: str
    urgency: str
    order_status: str
