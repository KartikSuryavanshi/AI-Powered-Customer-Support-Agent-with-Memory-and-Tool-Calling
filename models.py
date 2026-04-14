from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    plan_tier: str
    region: str


class BillingStatus(BaseModel):
    customer_id: str
    status: str
    last_payment_date: str
    outstanding_amount: float


class TicketCreate(BaseModel):
    customer_id: str
    subject: str
    description: str
    priority: str = "medium"


class Ticket(BaseModel):
    ticket_id: int
    customer_id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime


class DraftResponse(BaseModel):
    ticket_id: int
    draft: str
    context: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime


class GenerateDraftRequest(BaseModel):
    ticket_id: int


class GenerateDraftResult(BaseModel):
    ticket_id: int
    draft: str
    tool_trace: list[dict[str, Any]] = Field(default_factory=list)
    kb_context: list[str] = Field(default_factory=list)
    memory_context: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    app: str


class TicketWithDraft(BaseModel):
    ticket: Ticket
    draft: DraftResponse | None = None
