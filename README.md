# AI-Powered Customer Support Agent with Memory and Tool Calling

A production-oriented support copilot that reduces context switching for support teams by combining:

- ticket and customer data lookups (tool calling)
- knowledge-base retrieval (RAG)
- persistent customer memory (Mem0, with local fallback)
- one-click AI draft generation

The project uses a modular FastAPI backend, Streamlit dashboard, SQLite, ChromaDB, LangChain orchestration, Docker, and GitHub Actions deployment to AWS EC2.

## Product Preview

### Dashboard Screenshots

![Support Copilot Dashboard - View 1](https://github.com/user-attachments/assets/bdda916c-2a28-42fe-81c9-3c386dd3480c)

![Support Copilot Dashboard - View 2](https://github.com/user-attachments/assets/a4834317-35d6-4c65-a4f1-682131b57655)

### Demo Video

[Watch the product walkthrough](https://github.com/user-attachments/assets/7b64e404-12e6-4913-9c26-7c75a7ec320c)

## Why This Project

Support agents usually jump between CRM, billing, previous tickets, and help docs before writing a response. This app centralizes that flow:

1. Open a ticket
2. Click generate
3. Agent gathers context using tools + RAG + memory
4. LLM returns a ready-to-review response draft

## Current Implementation Status

Everything below is implemented in the current codebase:

- LangChain-based agent orchestration
- Tool calling for CRM and billing lookups
- RAG over local knowledge-base files
- Real Mem0 integration for memory (when `MEM0_API_KEY` is set)
- Automatic fallback to local Chroma memory when Mem0 is unavailable
- Groq-hosted LLM integration (`llama-3.1-8b-instant` by default)
- FastAPI + Streamlit app stack
- Docker local/prod compose files
- CI, Docker validation, and manual EC2 deploy workflow

## Architecture

### High-level Flow

```text
Ticket selected in dashboard
  -> Agent gathers tool context (customer profile, billing, ticket history)
  -> Agent retrieves KB context (RAG via Chroma)
  -> Agent fetches memory (Mem0 first, local Chroma fallback)
  -> LLM generates support draft
  -> Draft + trace + context saved to SQLite
  -> New memory added for future conversations
```

### Components

- `main.py`: FastAPI app and routes
- `copilot.py`: SupportCopilot orchestrator
- `tools.py`: LangChain tool definitions
- `rag.py`: knowledge-base retrieval and indexing
- `memory.py`: Mem0 integration + local memory fallback
- `embeddings.py`: sentence-transformer embedding adapter
- `database.py`: SQLite data layer
- `models.py`: Pydantic request/response schemas
- `app.py`: Streamlit dashboard UI

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| API | FastAPI | Backend endpoints |
| UI | Streamlit | Agent workspace dashboard |
| Orchestration | LangChain | Tool calling + prompt flow |
| LLM | Groq (`llama-3.1-8b-instant`) | Hosted response generation |
| Memory | Mem0 + Chroma fallback | Persistent customer context |
| RAG Store | ChromaDB | KB vector storage and retrieval |
| Primary DB | SQLite | Tickets, customers, billing, drafts |
| Containers | Docker + Compose | Local and production stack |
| CI/CD | GitHub Actions | Test/build/deploy pipeline |
| Hosting | AWS EC2 | Production runtime |

## Repository Structure

```text
.
├── app.py
├── config.py
├── copilot.py
├── database.py
├── embeddings.py
├── main.py
├── memory.py
├── models.py
├── rag.py
├── tools.py
├── requirements.txt
├── Dockerfile.api
├── Dockerfile.streamlit
├── docker-compose.yml
├── docker-compose.prod.yml
├── deploy/
│   ├── ec2_setup.sh
│   └── nginx/default.conf
├── data/knowledge_base/
├── scripts/bootstrap_data.py
├── tests/test_api.py
└── .github/workflows/
    ├── ci.yml
    ├── docker-validate.yml
    └── deploy-ec2.yml
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
APP_NAME=Support Copilot API
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

GROQ_API_KEY=
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MEM0_API_KEY=

CHROMA_PERSIST_DIR=./chroma
SQLITE_DB_PATH=./support_copilot.db
KNOWLEDGE_BASE_DIR=./data/knowledge_base
STREAMLIT_API_BASE_URL=http://localhost:8000
```

Notes:

- `GROQ_API_KEY` enables hosted LLM drafting.
- `MEM0_API_KEY` enables real Mem0 memory.
- If `MEM0_API_KEY` is empty or Mem0 is unavailable, memory automatically falls back to local Chroma.

## Local Setup (Python)

### 1. Create environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create local env file

```bash
cp .env.example .env
```

### 3. Bootstrap demo data

```bash
python scripts/bootstrap_data.py
```

### 4. Start API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start dashboard (new terminal)

```bash
streamlit run app.py --server.port 8501
```

### 6. Verify

- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/health`
- Dashboard: `http://localhost:8501`

## Docker Setup

### Local development stack

```bash
docker compose up -d --build
docker compose ps
```

Services:

- API on `:8000`
- Streamlit on `:8501`
- Nginx on `:80`

Stop stack:

```bash
docker compose down
```

### Production stack

Production deploy uses `docker-compose.prod.yml` with prebuilt GHCR images and mounted persistent data volume.

## API Endpoints

### Health

- `GET /health`

### Tickets

- `GET /tickets`
- `POST /tickets`
- `GET /tickets/{ticket_id}`

### Drafts

- `POST /drafts/generate`
- `GET /drafts/{ticket_id}`

## Memory Behavior (Important)

`CustomerMemoryStore` logic:

1. If Mem0 client initializes successfully (`MEM0_API_KEY` present), reads/writes go to Mem0.
2. If Mem0 fails or is not configured, local Chroma memory is used.
3. If both are unavailable, memory calls return safely without crashing app startup.

## RAG Behavior

- Knowledge files are loaded from `data/knowledge_base` (`.md` and `.txt`).
- Chunks are indexed into Chroma collection `support_kb_minilm`.
- Sentence-transformer embeddings are used (`all-MiniLM-L6-v2` by default).
- If vector retrieval is unavailable, a naive keyword search fallback is used.

## CI/CD Workflows

### CI

File: `.github/workflows/ci.yml`

- Runs on push/PR to `main`
- Installs dependencies and runs `pytest`

### Docker Validate

File: `.github/workflows/docker-validate.yml`

- Runs on push/PR to `main`
- Builds API and dashboard images without push

### Deploy to EC2

File: `.github/workflows/deploy-ec2.yml`

- Manual trigger only (`workflow_dispatch`)
- Requires input `confirm_deploy=DEPLOY`
- Builds/pushes GHCR images
- Copies compose and nginx files to EC2
- Writes `.env` on server with:
  - `GROQ_API_KEY`
  - `GROQ_MODEL`
  - `EMBEDDING_MODEL`
  - `MEM0_API_KEY`
- Pulls and restarts production stack

## AWS EC2 Deployment

### 1. One-time EC2 bootstrap

```bash
bash deploy/ec2_setup.sh
```

This script installs Docker and Docker Compose plugin, and prepares deploy directories.

### 2. Configure GitHub repository secrets

Required:

- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `GROQ_API_KEY`
- `MEM0_API_KEY`

### 3. Trigger deploy workflow

Use GitHub UI or CLI with `confirm_deploy=DEPLOY`.

## Testing

Current test file: `tests/test_api.py`

Covered now:

- Health endpoint
- Ticket listing endpoint

Run tests:

```bash
pytest
```

## Troubleshooting

### `/` returns 404 on API

Expected. Root route is not defined. Use `/docs` or `/health`.

### Draft generation falls back to template response

Likely causes:

- `GROQ_API_KEY` missing or invalid
- Groq service/network issue

### Mem0 not active

Check `MEM0_API_KEY` is set correctly. Without it, app will use local Chroma fallback.

### Embedding dimension mismatch in Chroma

If you changed embedding models between runs, reset local vectors:

```bash
rm -rf ./chroma
```

Then regenerate drafts to reindex KB and memory.

### Port already in use

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:8501 -sTCP:LISTEN
```

## Security Notes

- Never commit `.env`.
- Rotate keys if accidentally exposed.
- Keep `GROQ_API_KEY`, `MEM0_API_KEY`, and SSH keys in secrets managers.
