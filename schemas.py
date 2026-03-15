from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    email = "email"
    chat = "chat"
    web = "web"
    other = "other"


class Category(str, Enum):
    technical = "Technical"
    billing = "Billing"
    security = "Security"
    sales = "Sales"


class TriageRequest(BaseModel):
    source: SourceType
    raw_content: str
    metadata: dict[str, Any] | None = None


class TriageResult(BaseModel):
    category: Category = Field(description="Technical, Billing, Security, or Sales")
    urgency: int = Field(description="1 (Low) to 5 (High)")
    sentiment_score: float = Field(description="-1.0 to 1.0")
    summary: str = Field(description="Max 12 word summary")


class TriageResponse(BaseModel):
    job_id: str
    status: str


class TriageEvent(BaseModel):
    job_id: str
    request: TriageRequest
    result: TriageResult | None = None
    provider: str | None = None
    latency_ms: int | None = None
    error: str | None = None
