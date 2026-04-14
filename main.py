from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query

from config import settings
from copilot import SupportCopilot
from database import Database
from memory import CustomerMemoryStore
from models import DraftResponse, GenerateDraftRequest, GenerateDraftResult, HealthResponse, TicketCreate
from rag import KnowledgeBaseRetriever


db = Database()
memory_store = CustomerMemoryStore()
kb = KnowledgeBaseRetriever()
copilot = SupportCopilot(db=db, memory_store=memory_store, kb=kb)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    db.seed_demo_data()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)


@app.get("/tickets")
def list_tickets(status: str | None = Query(default=None)):
    return db.list_tickets(status=status)


@app.post("/tickets")
def create_ticket(payload: TicketCreate):
    customer = db.get_customer(payload.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {payload.customer_id} not found")
    return db.create_ticket(
        customer_id=payload.customer_id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
    )


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.post("/drafts/generate", response_model=GenerateDraftResult)
def generate_draft(payload: GenerateDraftRequest) -> GenerateDraftResult:
    try:
        result = copilot.generate_draft(ticket_id=payload.ticket_id)
        return GenerateDraftResult(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/drafts/{ticket_id}", response_model=DraftResponse)
def get_draft(ticket_id: int) -> DraftResponse:
    draft = db.get_draft(ticket_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    generated_at = datetime.fromisoformat(draft["generated_at"])
    return DraftResponse(
        ticket_id=ticket_id,
        draft=draft["draft"],
        context=draft["context"],
        generated_at=generated_at,
    )
