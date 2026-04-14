import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from config import settings


class Database:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.sqlite_db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    plan_tier TEXT NOT NULL,
                    region TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS billing_accounts (
                    customer_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_payment_date TEXT NOT NULL,
                    outstanding_amount REAL NOT NULL,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );

                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );

                CREATE TABLE IF NOT EXISTS drafts (
                    ticket_id INTEGER PRIMARY KEY,
                    draft TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
                );
                """
            )

    def seed_demo_data(self) -> None:
        customers = [
            ("CUST-1001", "Priya Sharma", "priya@example.com", "enterprise", "APAC"),
            ("CUST-1002", "Daniel Smith", "daniel@example.com", "pro", "US"),
            ("CUST-1003", "Elena Rossi", "elena@example.com", "starter", "EU"),
        ]
        billing_rows = [
            ("CUST-1001", "current", "2026-04-01", 0.0),
            ("CUST-1002", "overdue", "2026-02-11", 149.99),
            ("CUST-1003", "current", "2026-03-28", 0.0),
        ]
        tickets = [
            (
                "CUST-1002",
                "Billing mismatch for March",
                "I was charged twice in March and my dashboard still shows overdue. Please fix this.",
                "high",
            ),
            (
                "CUST-1001",
                "SSO login intermittently fails",
                "Our support team is getting signed out every 30 minutes after enabling SSO.",
                "high",
            ),
            (
                "CUST-1003",
                "Need invoice PDF",
                "Can you share the last two months of invoices in PDF format?",
                "low",
            ),
        ]

        with self.connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO customers(customer_id, name, email, plan_tier, region)
                VALUES (?, ?, ?, ?, ?)
                """,
                customers,
            )
            conn.executemany(
                """
                INSERT OR IGNORE INTO billing_accounts(customer_id, status, last_payment_date, outstanding_amount)
                VALUES (?, ?, ?, ?)
                """,
                billing_rows,
            )

            count = conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"]
            if count == 0:
                now = datetime.now(UTC).isoformat()
                conn.executemany(
                    """
                    INSERT INTO tickets(customer_id, subject, description, priority, status, created_at)
                    VALUES (?, ?, ?, ?, 'open', ?)
                    """,
                    [(c, s, d, p, now) for c, s, d, p in tickets],
                )

    def list_tickets(self, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM tickets"
        params: tuple[Any, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY created_at DESC"
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_ticket(self, ticket_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
        return dict(row) if row else None

    def create_ticket(self, customer_id: str, subject: str, description: str, priority: str) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tickets(customer_id, subject, description, status, priority, created_at)
                VALUES (?, ?, ?, 'open', ?, ?)
                """,
                (customer_id, subject, description, priority, now),
            )
            ticket_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
        return dict(row)

    def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
        return dict(row) if row else None

    def get_billing(self, customer_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM billing_accounts WHERE customer_id = ?", (customer_id,)).fetchone()
        return dict(row) if row else None

    def list_customer_tickets(self, customer_id: str, limit: int = 5) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM tickets
                WHERE customer_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (customer_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_draft(self, ticket_id: int, draft: str, context: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO drafts(ticket_id, draft, context_json, generated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ticket_id)
                DO UPDATE SET
                    draft = excluded.draft,
                    context_json = excluded.context_json,
                    generated_at = excluded.generated_at
                """,
                (ticket_id, draft, json.dumps(context), now),
            )
            row = conn.execute("SELECT * FROM drafts WHERE ticket_id = ?", (ticket_id,)).fetchone()
        return dict(row)

    def get_draft(self, ticket_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM drafts WHERE ticket_id = ?", (ticket_id,)).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["context"] = json.loads(payload.pop("context_json"))
        return payload
