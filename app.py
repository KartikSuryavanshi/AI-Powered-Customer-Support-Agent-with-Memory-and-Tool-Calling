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
            --ink: #101826;
            --slate: #64748b;
            --mist: #f4efe7;
            --card: rgba(255, 251, 247, 0.78);
            --line: rgba(16, 24, 38, 0.10);
            --teal: #0d9488;
            --amber: #d97706;
            --coral: #dc5d43;
            --sky: #1d4ed8;
            --navy: #102033;
            --sand: #f6ecdf;
            --gold: #c48b2f;
        }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="collapsedControl"] {
            display: none;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(196, 139, 47, 0.16), transparent 26%),
                radial-gradient(circle at top right, rgba(13, 148, 136, 0.14), transparent 24%),
                linear-gradient(180deg, #fbf7f1 0%, #f3ede3 42%, #eef4f3 100%);
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
            padding-top: 1.4rem;
            padding-bottom: 2.4rem;
            max-width: 1360px;
        }

        .stage-shell {
            border-radius: 34px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.5);
            background:
                linear-gradient(135deg, rgba(16, 32, 51, 0.96), rgba(15, 76, 129, 0.92) 48%, rgba(13, 148, 136, 0.78)),
                linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            box-shadow: 0 34px 80px rgba(16, 24, 38, 0.18);
            margin-bottom: 1.25rem;
        }

        .stage-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.9fr);
            gap: 1rem;
            padding: 1.4rem;
        }

        .hero-shell {
            padding: 1.3rem 1.35rem;
            border-radius: 28px;
            background:
                radial-gradient(circle at top right, rgba(196, 139, 47, 0.18), transparent 30%),
                rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
        }

        .hero-kicker {
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.72);
            font-weight: 700;
            margin-bottom: 0.55rem;
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 0.95;
            margin: 0;
            color: #fdfbf7;
            max-width: 11ch;
        }

        .hero-copy {
            margin: 0.9rem 0 0;
            max-width: 58ch;
            color: rgba(248, 250, 252, 0.78);
            font-size: 1rem;
            line-height: 1.58;
        }

        .hero-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1rem;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.75rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            color: #f8fafc;
            font-weight: 700;
            font-size: 0.83rem;
            border: 1px solid rgba(255,255,255,0.10);
        }

        .hero-pill-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: #34d399;
        }

        .spotlight-shell {
            display: grid;
            gap: 0.85rem;
        }

        .spotlight-card {
            border-radius: 26px;
            padding: 1rem 1.05rem;
            background: rgba(255, 250, 246, 0.92);
            border: 1px solid rgba(255,255,255,0.16);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.4);
        }

        .spotlight-kicker {
            color: var(--sky);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .spotlight-title {
            font-size: 1.25rem;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }

        .spotlight-copy {
            color: var(--slate);
            line-height: 1.5;
            margin: 0;
        }

        .stat-shell {
            border-radius: 24px;
            padding: 1rem 1.05rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.76), rgba(255,255,255,0.52));
            border: 1px solid rgba(16, 24, 38, 0.08);
            box-shadow: 0 18px 36px rgba(16, 24, 38, 0.06);
        }

        .stat-label {
            color: var(--slate);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            margin-bottom: 0.45rem;
        }

        .stat-value {
            font-size: 1.9rem;
            font-weight: 700;
            line-height: 1;
        }

        .stat-footnote {
            margin-top: 0.35rem;
            color: var(--slate);
            font-size: 0.82rem;
        }

        .section-shell {
            border-radius: 30px;
            padding: 1.2rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(250,247,242,0.78));
            border: 1px solid rgba(16, 24, 38, 0.08);
            box-shadow: 0 24px 56px rgba(16, 24, 38, 0.08);
        }

        .section-head {
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.9rem;
        }

        .section-kicker {
            color: var(--sky);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-weight: 700;
            margin-bottom: 0.28rem;
        }

        .section-title {
            font-size: 1.65rem;
            line-height: 1;
            margin: 0;
        }

        .section-copy {
            color: var(--slate);
            margin: 0;
            line-height: 1.5;
            font-size: 0.94rem;
        }

        .filter-shell {
            border-radius: 24px;
            padding: 1rem;
            background: linear-gradient(180deg, rgba(16,32,51,0.96), rgba(19,45,70,0.94));
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 22px 48px rgba(16,24,38,0.18);
            margin-bottom: 0.95rem;
        }

        .filter-title {
            color: #f8fafc;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .filter-copy {
            color: rgba(248,250,252,0.68);
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 0.85rem;
        }

        .panel-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .ticket-card {
            position: relative;
            background: linear-gradient(180deg, rgba(255,255,255,0.86), rgba(249,244,236,0.8));
            border: 1px solid rgba(16, 24, 38, 0.08);
            border-radius: 24px;
            padding: 1.05rem 1.1rem;
            box-shadow: 0 14px 34px rgba(15, 23, 32, 0.05);
            margin-bottom: 0.9rem;
        }

        .ticket-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 5px;
            border-radius: 24px 0 0 24px;
            background: linear-gradient(180deg, var(--gold), var(--teal));
            opacity: 0.65;
        }

        .ticket-card.selected {
            border-color: rgba(29, 78, 216, 0.22);
            box-shadow: 0 24px 48px rgba(29, 78, 216, 0.12);
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(239,247,244,0.94));
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

        .workspace-shell {
            background:
                radial-gradient(circle at top right, rgba(196,139,47,0.10), transparent 28%),
                linear-gradient(180deg, rgba(255,255,255,0.88), rgba(248,244,238,0.84));
            border: 1px solid rgba(16, 24, 38, 0.08);
            border-radius: 28px;
            padding: 1.15rem;
            box-shadow: 0 18px 44px rgba(15, 23, 32, 0.06);
            margin-bottom: 1rem;
        }

        .workspace-eyebrow {
            color: var(--sky);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.76rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .workspace-title {
            font-size: 1.45rem;
            line-height: 1.05;
            margin-bottom: 0.45rem;
        }

        .workspace-copy {
            color: var(--slate);
            margin: 0;
            line-height: 1.55;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.7rem;
            margin: 0.95rem 0 0;
        }

        .mini-stat {
            background: rgba(15, 23, 32, 0.03);
            border: 1px solid rgba(15, 23, 32, 0.07);
            border-radius: 18px;
            padding: 0.8rem 0.85rem;
        }

        .mini-label {
            color: var(--slate);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .mini-value {
            font-size: 1.05rem;
            font-weight: 700;
        }

        .empty-state {
            border-radius: 28px;
            padding: 1.4rem;
            background:
                radial-gradient(circle at top right, rgba(15, 76, 129, 0.10), transparent 30%),
                linear-gradient(180deg, rgba(255,255,255,0.9), rgba(242,248,246,0.92));
            border: 1px solid var(--line);
            box-shadow: 0 18px 44px rgba(15, 23, 32, 0.06);
        }

        .empty-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .empty-copy {
            color: var(--slate);
            line-height: 1.55;
            max-width: 58ch;
        }

        .trace-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(250,246,240,0.88));
            border: 1px solid rgba(16, 24, 38, 0.08);
            border-radius: 22px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
        }

        .trace-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 0.65rem;
        }

        .trace-name {
            font-weight: 700;
            font-size: 1rem;
        }

        .trace-label {
            color: var(--slate);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .trace-body {
            color: var(--ink);
            line-height: 1.55;
            font-size: 0.93rem;
            white-space: pre-wrap;
            word-break: break-word;
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
            background: rgba(16, 32, 51, 0.08);
            color: var(--navy);
            font-size: 0.78rem;
            font-family: 'IBM Plex Mono', monospace;
        }

        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {
            color: rgba(248,250,252,0.72) !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700 !important;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 18px;
            border: 1px solid rgba(15, 23, 32, 0.10);
            background: rgba(255, 252, 248, 0.94);
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

        div[data-testid="stTextInput"] input {
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: rgba(255,255,255,0.08) !important;
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(248,250,252,0.45) !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 16px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: rgba(255,255,255,0.08) !important;
            color: #f8fafc !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg, #c48b2f, #0d9488 55%, #1d4ed8);
            color: white;
            font-weight: 700;
            padding: 0.55rem 1rem;
            box-shadow: 0 12px 26px rgba(29, 78, 216, 0.18);
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
            border-radius: 999px;
            padding: 0.4rem 0.7rem;
        }

        button[role="tab"][aria-selected="true"] {
            color: var(--navy) !important;
            background: rgba(196, 139, 47, 0.14) !important;
        }

        @media (max-width: 900px) {
            .stage-grid {
                grid-template-columns: 1fr;
            }

            .mini-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .hero-title {
                font-size: 2.25rem;
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


@st.cache_data(ttl=10)
def fetch_health() -> dict:
    response = requests.get(f"{API_BASE}/health", timeout=10)
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


def summarize_text(value: str, limit: int = 160) -> str:
    compact = " ".join(value.split())
    return compact if len(compact) <= limit else f"{compact[:limit - 3]}..."


def selected_ticket_from(tickets: list[dict], ticket_id: int | None) -> dict | None:
    if ticket_id is None:
        return None
    for item in tickets:
        if item["ticket_id"] == ticket_id:
            return item
    return None


def render_stat_card(column, label: str, value: int, footnote: str) -> None:
    column.markdown(
        f"""
        <div class="stat-shell">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-footnote">{footnote}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

if "active_result" not in st.session_state:
    st.session_state["active_result"] = None
if "active_ticket_id" not in st.session_state:
    st.session_state["active_ticket_id"] = None

# ── Data ──────────────────────────────────────────────────────────────────────
try:
    tickets = fetch_tickets()
except requests.RequestException as exc:
    st.error(f"Could not reach the API at {API_BASE}. Details: {exc}")
    st.stop()

try:
    health = fetch_health()
except requests.RequestException:
    health = None

selected_ticket = selected_ticket_from(tickets, st.session_state.get("active_ticket_id"))

status_markup = (
    f'<span class="hero-pill"><span class="hero-pill-dot"></span> API online · {health.get("app", "Support Copilot API")}</span>'
    if health
    else '<span class="hero-pill"><span class="hero-pill-dot" style="background:#fb7185"></span> API status unknown</span>'
)

spotlight_title = "No ticket selected"
spotlight_copy = "Pick a ticket from the queue to open a richer response workspace with memory, tool activity, and retrieved guidance."
if selected_ticket:
    spotlight_title = f"#{selected_ticket['ticket_id']} · {selected_ticket['subject']}"
    spotlight_copy = summarize_text(selected_ticket["description"], limit=180)

st.markdown(
    f"""
    <section class="stage-shell">
        <div class="stage-grid">
            <div class="hero-shell">
                <div class="hero-kicker">Support operations cockpit</div>
                <h1 class="hero-title">Faster support replies, with context that actually matters.</h1>
                <p class="hero-copy">
                    Pull ticket details, customer memory, billing signals, and knowledge-base guidance into one polished workspace built for real support operations.
                </p>
                <div class="hero-strip">
                    {status_markup}
                    <span class="hero-pill">{len(tickets)} tickets in queue</span>
                    <span class="hero-pill">Groq-backed drafting</span>
                </div>
            </div>
            <div class="spotlight-shell">
                <div class="spotlight-card">
                    <div class="spotlight-kicker">Current focus</div>
                    <div class="spotlight-title">{spotlight_title}</div>
                    <p class="spotlight-copy">{spotlight_copy}</p>
                </div>
                <div class="spotlight-card">
                    <div class="spotlight-kicker">Workspace mode</div>
                    <div class="spotlight-title">Operator-first layout</div>
                    <p class="spotlight-copy">Filter the queue, open a ticket, and regenerate the draft without losing the tool trace or retrieved context.</p>
                </div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

filter_col, spacer_col = st.columns([0.9, 1.1], gap="large")
with filter_col:
    st.markdown(
        """
        <div class="filter-shell">
            <div class="filter-title">Queue filters</div>
            <div class="filter-copy">Tighten the worklist before you open a ticket workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    search_query = st.text_input("Search queue", placeholder="Search by subject, customer, or issue")
    filter_left, filter_right = st.columns(2)
    with filter_left:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with filter_right:
        status_filter = st.selectbox("Status", ["All", "Open", "Closed"])
    if st.button("Reset view", use_container_width=True):
        st.session_state["active_result"] = None
        st.session_state["active_ticket_id"] = None
        st.rerun()
with spacer_col:
    st.markdown("")

filtered_tickets = []
for ticket in tickets:
    haystack = " ".join(
        [
            str(ticket.get("ticket_id", "")),
            ticket.get("subject", ""),
            ticket.get("customer_id", ""),
            ticket.get("description", ""),
            ticket.get("status", ""),
            ticket.get("priority", ""),
        ]
    ).lower()
    if search_query and search_query.lower() not in haystack:
        continue
    if priority_filter != "All" and ticket.get("priority", "").lower() != priority_filter.lower():
        continue
    if status_filter != "All" and ticket.get("status", "").lower() != status_filter.lower():
        continue
    filtered_tickets.append(ticket)

# ── KPI strip ─────────────────────────────────────────────────────────────────
current_result = st.session_state.get("active_result") or {}
open_count     = len([t for t in tickets if t.get("status", "").lower() == "open"])
high_priority  = sum(1 for t in tickets if t.get("priority", "").lower() == "high")
retrieval_hits = len(current_result.get("kb_context", [])) + len(current_result.get("memory_context", []))
tool_calls     = len(current_result.get("tool_trace", []))
visible_count  = len(filtered_tickets)

PRIORITY_COLORS = {
    "high":   ("#d95f43", "rgba(217,95,67,0.14)"),
    "medium": ("#dd8b12", "rgba(221,139,18,0.14)"),
    "low":    ("#0f4c81", "rgba(15,76,129,0.10)"),
}

metric_cols = st.columns(4)
render_stat_card(metric_cols[0], "Open queue", open_count, "Tickets still awaiting action")
render_stat_card(metric_cols[1], "Visible now", visible_count, "Items matching current filters")
render_stat_card(metric_cols[2], "Context hits", retrieval_hits, "KB chunks plus memory recalled")
render_stat_card(metric_cols[3], "Tool calls", tool_calls, "Live enrichment actions in draft")

st.write("")

# ── Main layout ───────────────────────────────────────────────────────────────
left, right = st.columns([0.95, 1.25], gap="large")

# ── Left: ticket queue ────────────────────────────────────────────────────────
with left:
    st.markdown(
        """
        <div class="section-shell">
            <div class="section-head">
                <div>
                    <div class="section-kicker">Work queue</div>
                    <h2 class="section-title">Incoming tickets</h2>
                </div>
                <p class="section-copy">Open a ticket to promote it into the draft workspace.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not filtered_tickets:
        st.info("No tickets match the current filters.")

    for row in filtered_tickets:
        is_selected = st.session_state.get("active_ticket_id") == row["ticket_id"]
        priority    = row["priority"].lower()
        fg, bg      = PRIORITY_COLORS.get(priority, ("#0f1720", "rgba(15,23,32,0.08)"))

        card_class = "ticket-card selected" if is_selected else "ticket-card"
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        with st.container():
            hdr_left, hdr_right = st.columns([3, 1])
            with hdr_left:
                st.markdown(
                    f"**#{row['ticket_id']} - {row['subject']}**"
                    + (" &nbsp;`active`" if is_selected else "")
                )
            with hdr_right:
                st.markdown(
                    f'<span style="display:inline-block;padding:0.2rem 0.55rem;'
                    f'border-radius:999px;font-size:0.78rem;font-weight:700;'
                    f'background:{bg};color:{fg}">{priority.upper()}</span>',
                    unsafe_allow_html=True,
                )

            st.write(summarize_text(row["description"], limit=180))
            meta_left, meta_right = st.columns(2)
            meta_left.caption(f"Customer: **{row['customer_id']}**")
            meta_right.caption(f"Status: **{row['status'].upper()}**")

            if st.button(
                "Regenerate draft" if is_selected and st.session_state.get("active_result") else "Open workspace",
                key=f"gen-{row['ticket_id']}",
                use_container_width=True,
            ):
                with st.spinner("Generating draft with tools, memory, and RAG context..."):
                    result = generate(row["ticket_id"])
                st.session_state["active_result"] = result
                st.session_state["active_ticket_id"] = row["ticket_id"]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Right: draft workspace ────────────────────────────────────────────────────
with right:
    result = st.session_state.get("active_result")
    selected_ticket = selected_ticket_from(tickets, st.session_state.get("active_ticket_id"))

    st.markdown(
        """
        <div class="section-shell">
            <div class="section-head">
                <div>
                    <div class="section-kicker">Response studio</div>
                    <h2 class="section-title">Draft workspace</h2>
                </div>
                <p class="section-copy">Review the draft, trace enrichment steps, and inspect supporting context.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not result:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-title">No active draft yet</div>
                <div class="empty-copy">
                    Pick a ticket from the queue to generate a response workspace. Once selected, this pane will surface the draft, tool activity, retrieved knowledge, and customer memory in one place.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if selected_ticket:
            st.markdown(
                f"""
                <div class="workspace-shell">
                    <div class="workspace-eyebrow">Active ticket</div>
                    <div class="workspace-title">#{selected_ticket['ticket_id']} · {selected_ticket['subject']}</div>
                    <p class="workspace-copy">{selected_ticket['description']}</p>
                    <div class="mini-grid">
                        <div class="mini-stat"><div class="mini-label">Customer</div><div class="mini-value">{selected_ticket['customer_id']}</div></div>
                        <div class="mini-stat"><div class="mini-label">Priority</div><div class="mini-value">{selected_ticket['priority'].upper()}</div></div>
                        <div class="mini-stat"><div class="mini-label">Status</div><div class="mini-value">{selected_ticket['status'].upper()}</div></div>
                        <div class="mini-stat"><div class="mini-label">Signals</div><div class="mini-value">{len(result.get('kb_context', [])) + len(result.get('memory_context', []))}</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
            action_left, action_right = st.columns([1, 1])
            with action_left:
                if selected_ticket and st.button("Refresh this draft", use_container_width=True):
                    with st.spinner("Refreshing draft with latest context..."):
                        refreshed = generate(selected_ticket["ticket_id"])
                    st.session_state["active_result"] = refreshed
                    st.rerun()
            with action_right:
                st.caption("Generated from live ticket data, tool calls, KB chunks, and memory.")
            st.text_area("AI Draft", value=result["draft"], height=380, label_visibility="collapsed")

        with tools_tab:
            trace = result.get("tool_trace", [])
            if trace:
                for index, step in enumerate(trace, start=1):
                    st.markdown(
                        f"""
                        <div class="trace-card">
                            <div class="trace-header">
                                <div class="trace-name">Step {index}: {step.get('tool', 'tool')}</div>
                                <span class="context-chip">{len(str(step.get('result', '')))} chars</span>
                            </div>
                            <div class="trace-label">Arguments</div>
                            <div class="trace-body">{step.get('args', {})}</div>
                            <div class="trace-label" style="margin-top:0.7rem;">Result</div>
                            <div class="trace-body">{step.get('result', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
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
    st.markdown("</div>", unsafe_allow_html=True)
