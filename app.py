import requests
import streamlit as st

from config import settings

st.set_page_config(page_title="Support Copilot", page_icon="🎧", layout="wide")

API_BASE = settings.streamlit_api_base_url.rstrip("/")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {
            --ink: #0f1720;
            --slate: #5c6773;
            --mist: #eef3f1;
            --card: rgba(255, 255, 255, 0.82);
            --line: rgba(15, 23, 32, 0.08);
            --teal: #0e766e;
            --amber: #dd8b12;
            --coral: #d95f43;
            --sky: #0f4c81;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(14, 118, 110, 0.10), transparent 24%),
                radial-gradient(circle at top right, rgba(217, 95, 67, 0.12), transparent 26%),
                linear-gradient(180deg, #f7fbfa 0%, #edf4f1 100%);
        }

        .stApp, .stApp p, .stApp li, .stApp label, .stApp span {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--ink);
        }

        .stApp h1, .stApp h2, .stApp h3 {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.03em;
            color: var(--ink);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .hero-shell {
            padding: 1.7rem 1.8rem;
            border: 1px solid rgba(255, 255, 255, 0.55);
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.86), rgba(244, 250, 248, 0.72)),
                linear-gradient(135deg, rgba(14, 118, 110, 0.08), rgba(217, 95, 67, 0.08));
            box-shadow: 0 26px 60px rgba(15, 23, 32, 0.08);
            margin-bottom: 1.2rem;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(15, 76, 129, 0.10);
            color: var(--sky);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: 2.4rem;
            line-height: 1.02;
            margin: 0;
            max-width: 11ch;
        }

        .hero-copy {
            margin: 0.7rem 0 0;
            max-width: 60ch;
            color: var(--slate);
            font-size: 1rem;
        }

        .metric-card {
            border-radius: 22px;
            padding: 1rem 1.05rem;
            background: var(--card);
            border: 1px solid var(--line);
            box-shadow: 0 18px 40px rgba(15, 23, 32, 0.05);
        }

        .metric-label {
            color: var(--slate);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            font-size: 1.9rem;
            font-weight: 700;
            line-height: 1;
        }

        .panel-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .ticket-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 14px 34px rgba(15, 23, 32, 0.05);
            margin-bottom: 0.9rem;
        }

        .ticket-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.7rem;
            margin-bottom: 0.4rem;
        }

        .ticket-subject {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0;
        }

        .ticket-meta {
            color: var(--slate);
            font-size: 0.88rem;
            margin-top: 0.65rem;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.75rem;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.26rem 0.66rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        .badge-priority-high { background: rgba(217, 95, 67, 0.14); color: var(--coral); }
        .badge-priority-medium { background: rgba(221, 139, 18, 0.14); color: var(--amber); }
        .badge-priority-low { background: rgba(15, 76, 129, 0.10); color: var(--sky); }
        .badge-status-open { background: rgba(14, 118, 110, 0.12); color: var(--teal); }
        .badge-status-other { background: rgba(15, 23, 32, 0.08); color: var(--ink); }

        .draft-shell {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 1.15rem;
            box-shadow: 0 20px 50px rgba(15, 23, 32, 0.06);
        }

        .draft-note {
            color: var(--slate);
            font-size: 0.95rem;
            margin-top: 0.3rem;
            margin-bottom: 1rem;
        }

        .context-chip {
            display: inline-block;
            margin-right: 0.5rem;
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
            background: rgba(15, 23, 32, 0.05);
            color: var(--slate);
            font-size: 0.78rem;
            font-family: 'IBM Plex Mono', monospace;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 18px;
            border: 1px solid rgba(15, 23, 32, 0.10);
            background: rgba(250, 252, 251, 0.94);
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
            caret-color: var(--ink);
            font-size: 0.95rem;
            line-height: 1.55;
        }

        div[data-testid="stTextArea"] textarea::placeholder {
            color: var(--slate);
            opacity: 1;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--slate) !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg, #0e766e, #0f4c81);
            color: white;
            font-weight: 700;
            padding: 0.55rem 1rem;
            box-shadow: 0 10px 22px rgba(15, 76, 129, 0.22);
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=10)
def fetch_tickets() -> list[dict]:
    response = requests.get(f"{API_BASE}/tickets", timeout=15)
    response.raise_for_status()
    return response.json()


def generate(ticket_id: int) -> dict:
    response = requests.post(
        f"{API_BASE}/drafts/generate",
        json={"ticket_id": ticket_id},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def priority_badge(priority: str) -> str:
    label = priority.lower()
    return f"badge-priority-{label}" if label in {"high", "medium", "low"} else "badge-priority-medium"


def status_badge(status: str) -> str:
    return "badge-status-open" if status.lower() == "open" else "badge-status-other"


inject_styles()

if "active_result" not in st.session_state:
    st.session_state["active_result"] = None
if "active_ticket_id" not in st.session_state:
    st.session_state["active_ticket_id"] = None

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <section class="hero-shell">
        <div class="hero-kicker">Agentic support workspace</div>
        <h1 class="hero-title">Support replies with customer memory built&nbsp;in.</h1>
        <p class="hero-copy">
            Pull CRM context, billing data, historical ticket signals,
            retrieval-augmented knowledge, and long-term memory into a single
            draft workspace for faster support operations.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────────
try:
    tickets = fetch_tickets()
except requests.RequestException as exc:
    st.error(f"Could not reach the API at {API_BASE}. Details: {exc}")
    st.stop()

# ── KPI strip ─────────────────────────────────────────────────────────────────
current_result = st.session_state.get("active_result") or {}
open_count     = len(tickets)
high_priority  = sum(1 for t in tickets if t.get("priority", "").lower() == "high")
retrieval_hits = len(current_result.get("kb_context", [])) + len(current_result.get("memory_context", []))
tool_calls     = len(current_result.get("tool_trace", []))

PRIORITY_COLORS = {
    "high":   ("#d95f43", "rgba(217,95,67,0.14)"),
    "medium": ("#dd8b12", "rgba(221,139,18,0.14)"),
    "low":    ("#0f4c81", "rgba(15,76,129,0.10)"),
}

for col, (label, value) in zip(
    st.columns(4),
    [("Open queue", open_count), ("High priority", high_priority),
     ("Context hits", retrieval_hits), ("Tool calls", tool_calls)],
):
    col.metric(label, value)

st.write("")

# ── Main layout ───────────────────────────────────────────────────────────────
left, right = st.columns([0.95, 1.25], gap="large")

# ── Left: ticket queue ────────────────────────────────────────────────────────
with left:
    st.markdown("### Incoming ticket queue")
    if not tickets:
        st.info("No tickets available.")

    for row in tickets:
        is_selected = st.session_state.get("active_ticket_id") == row["ticket_id"]
        priority    = row["priority"].lower()
        fg, bg      = PRIORITY_COLORS.get(priority, ("#0f1720", "rgba(15,23,32,0.08)"))

        with st.container(border=True):
            hdr_left, hdr_right = st.columns([3, 1])
            with hdr_left:
                st.markdown(
                    f"**#{row['ticket_id']} &mdash; {row['subject']}**"
                    + (" &nbsp;`selected`" if is_selected else "")
                )
            with hdr_right:
                st.markdown(
                    f'<span style="display:inline-block;padding:0.2rem 0.55rem;'
                    f'border-radius:999px;font-size:0.78rem;font-weight:700;'
                    f'background:{bg};color:{fg}">{priority.upper()}</span>',
                    unsafe_allow_html=True,
                )

            st.write(row["description"])
            st.caption(
                f"Customer: **{row['customer_id']}** &nbsp;|&nbsp; "
                f"Status: **{row['status'].upper()}**"
            )

            if st.button(
                "Generate reply draft",
                key=f"gen-{row['ticket_id']}",
                use_container_width=True,
            ):
                with st.spinner("Generating draft with tools, memory, and RAG context..."):
                    result = generate(row["ticket_id"])
                st.session_state["active_result"] = result
                st.session_state["active_ticket_id"] = row["ticket_id"]
                st.rerun()

# ── Right: draft workspace ────────────────────────────────────────────────────
with right:
    st.markdown("### Draft workspace")
    result = st.session_state.get("active_result")

    if not result:
        st.info(
            "Choose a ticket and click **Generate reply draft**. "
            "This panel will show the AI draft, tool activity, "
            "knowledge retrieval, and customer memory."
        )
    else:
        # Chip row
        chips = (
            f'<span style="display:inline-block;margin:0 0.3rem 0.4rem 0;padding:0.2rem 0.55rem;'
            f'border-radius:999px;background:rgba(15,23,32,0.07);font-size:0.78rem;'
            f'font-family:monospace">ticket&nbsp;{result["ticket_id"]}</span>'
            f'<span style="display:inline-block;margin:0 0.3rem 0.4rem 0;padding:0.2rem 0.55rem;'
            f'border-radius:999px;background:rgba(15,23,32,0.07);font-size:0.78rem;'
            f'font-family:monospace">kb&nbsp;{len(result.get("kb_context", []))}</span>'
            f'<span style="display:inline-block;margin:0 0.3rem 0.4rem 0;padding:0.2rem 0.55rem;'
            f'border-radius:999px;background:rgba(15,23,32,0.07);font-size:0.78rem;'
            f'font-family:monospace">memory&nbsp;{len(result.get("memory_context", []))}</span>'
            f'<span style="display:inline-block;margin:0 0.3rem 0.4rem 0;padding:0.2rem 0.55rem;'
            f'border-radius:999px;background:rgba(15,23,32,0.07);font-size:0.78rem;'
            f'font-family:monospace">tools&nbsp;{len(result.get("tool_trace", []))}</span>'
        )
        st.markdown(chips, unsafe_allow_html=True)

        draft_tab, tools_tab, kb_tab, memory_tab = st.tabs(
            ["Reply Draft", "Tool Trace", "Knowledge Base", "Customer Memory"]
        )

        with draft_tab:
            st.text_area("AI Draft", value=result["draft"], height=380, label_visibility="collapsed")

        with tools_tab:
            trace = result.get("tool_trace", [])
            if trace:
                st.json(trace)
            else:
                st.info("No tool calls were required for this draft.")

        with kb_tab:
            kb_items = result.get("kb_context", [])
            if kb_items:
                for idx, chunk in enumerate(kb_items, start=1):
                    with st.expander(f"Source {idx}", expanded=(idx == 1)):
                        st.write(chunk)
            else:
                st.info("No matching knowledge base chunks were retrieved.")

        with memory_tab:
            memory_items = result.get("memory_context", [])
            if memory_items:
                for idx, item in enumerate(memory_items, start=1):
                    with st.expander(f"Memory {idx}", expanded=(idx == 1)):
                        st.write(item)
            else:
                st.info("No prior customer memory matched this request.")
