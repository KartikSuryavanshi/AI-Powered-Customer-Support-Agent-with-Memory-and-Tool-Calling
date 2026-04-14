import json
from typing import Any

from langchain_core.tools import tool

from database import Database


def create_support_tools(db: Database) -> tuple[list[Any], dict[str, Any]]:
    @tool
    def get_customer_profile(customer_id: str) -> str:
        """Fetch customer profile details from the CRM mock store."""
        profile = db.get_customer(customer_id)
        if not profile:
            return json.dumps({"error": f"Customer {customer_id} not found"})
        return json.dumps(profile)

    @tool
    def get_billing_status(customer_id: str) -> str:
        """Fetch billing details and outstanding information for a customer."""
        billing = db.get_billing(customer_id)
        if not billing:
            return json.dumps({"error": f"Billing data not found for {customer_id}"})
        return json.dumps(billing)

    @tool
    def get_recent_tickets(customer_id: str) -> str:
        """Return recent support tickets for historical customer context."""
        rows = db.list_customer_tickets(customer_id=customer_id, limit=5)
        return json.dumps(rows)

    tool_list = [get_customer_profile, get_billing_status, get_recent_tickets]
    registry = {t.name: t for t in tool_list}
    return tool_list, registry
