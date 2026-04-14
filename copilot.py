import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from config import settings
from database import Database
from memory import CustomerMemoryStore
from rag import KnowledgeBaseRetriever
from tools import create_support_tools

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover
    ChatOpenAI = None


class SupportCopilot:
    def __init__(self, db: Database, memory_store: CustomerMemoryStore, kb: KnowledgeBaseRetriever) -> None:
        self.db = db
        self.memory_store = memory_store
        self.kb = kb
        self.tools, self.tool_registry = create_support_tools(db)

    def generate_draft(self, ticket_id: int) -> dict[str, Any]:
        ticket = self.db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")

        kb_context = self.kb.search(ticket["description"], k=4)
        memory_context = self.memory_store.get_relevant_memories(
            customer_id=ticket["customer_id"],
            query=ticket["description"],
            k=3,
        )

        if settings.openai_api_key and ChatOpenAI:
            draft, trace = self._generate_with_llm(ticket, kb_context, memory_context)
        else:
            draft = self._fallback_draft(ticket, kb_context, memory_context)
            trace = []

        self.memory_store.add_memory(
            customer_id=ticket["customer_id"],
            memory_text=f"Ticket {ticket_id}: {ticket['subject']} | Draft summary: {draft[:160]}",
        )

        context_payload = {
            "tool_trace": trace,
            "kb_context": kb_context,
            "memory_context": memory_context,
        }
        self.db.save_draft(ticket_id=ticket_id, draft=draft, context=context_payload)

        return {
            "ticket_id": ticket_id,
            "draft": draft,
            **context_payload,
        }

    def _generate_with_llm(
        self,
        ticket: dict[str, Any],
        kb_context: list[str],
        memory_context: list[str],
    ) -> tuple[str, list[dict[str, Any]]]:
        llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
        llm_with_tools = llm.bind_tools(self.tools)

        prompt = (
            "Use available tools to gather customer, billing, and history context. "
            "Then draft a concise, empathetic support response with clear next steps.\n\n"
            f"Ticket ID: {ticket['ticket_id']}\n"
            f"Customer ID: {ticket['customer_id']}\n"
            f"Subject: {ticket['subject']}\n"
            f"Description: {ticket['description']}\n\n"
            f"Knowledge Base Context: {kb_context}\n"
            f"Memory Context: {memory_context}\n"
        )

        messages: list[Any] = [
            SystemMessage(
                content=(
                    "You are an expert customer support copilot. Always include: "
                    "1) acknowledgement, 2) findings, 3) exact actions, 4) timeline."
                )
            ),
            HumanMessage(content=prompt),
        ]

        trace: list[dict[str, Any]] = []
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        if getattr(ai_msg, "tool_calls", None):
            for call in ai_msg.tool_calls:
                tool_name = call["name"]
                tool_args = call.get("args", {})
                result = self.tool_registry[tool_name].invoke(tool_args)
                trace.append({"tool": tool_name, "args": tool_args, "result": result})
                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=call["id"],
                        name=tool_name,
                    )
                )
            final_msg = llm_with_tools.invoke(messages)
            draft = final_msg.content if isinstance(final_msg.content, str) else str(final_msg.content)
        else:
            draft = ai_msg.content if isinstance(ai_msg.content, str) else str(ai_msg.content)

        return draft.strip(), trace

    def _fallback_draft(
        self,
        ticket: dict[str, Any],
        kb_context: list[str],
        memory_context: list[str],
    ) -> str:
        kb_hint = kb_context[0][:180] if kb_context else "No KB match found."
        mem_hint = memory_context[0][:180] if memory_context else "No prior memory found."
        return (
            f"Hi {ticket['customer_id']},\n\n"
            f"Thanks for reaching out about '{ticket['subject']}'. I reviewed your request and we are already checking this with priority {ticket['priority']}.\n\n"
            "What we found:\n"
            f"- Ticket details: {ticket['description']}\n"
            f"- Relevant knowledge base guidance: {kb_hint}\n"
            f"- Prior context: {mem_hint}\n\n"
            "Next steps:\n"
            "1. Validate account and billing/service state.\n"
            "2. Apply fix or provide workaround.\n"
            "3. Send a confirmed update within 24 hours.\n\n"
            "Best,\nSupport Copilot"
        )
