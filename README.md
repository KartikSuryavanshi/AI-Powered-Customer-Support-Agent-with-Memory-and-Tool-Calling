# AI-Powered Customer Support Agent with Memory and Tool Calling

An agentic support copilot that reduces tool switching by combining:

- FastAPI backend for ticket workflows
- Streamlit dashboard for one-click drafting
- LangChain tool calling for CRM and billing lookups
- ChromaDB-backed RAG for knowledge retrieval
- Persistent customer memory (vector memory store)
- SQLite for tickets and draft storage
- Dockerized local/production deployment
- GitHub Actions CI/CD + AWS EC2 deployment pipeline

## Architecture Layers

- Presentation Layer:
  - `main.py` (FastAPI routes)
  - `app.py` (Streamlit dashboard)
- Application Layer:
  - `copilot.py` (orchestrator: memory + RAG + tools -> draft)
- Infrastructure Layer:
  - `database.py` (SQLite)
  - `memory.py` (customer memory in Chroma)
  - `rag.py` (knowledge base indexing + retrieval)
  - `tools.py` (mock CRM + billing tools)
  - `config.py` (settings)
- Domain Layer:
  - `models.py` (Pydantic schemas)

## Prerequisites

- Python 3.11+
- Docker + Docker Compose
- OpenAI API key (optional, enables LLM mode)
- Mem0 API key (optional placeholder for future external memory integration)

## Quick Start (Local Python)

1. Create env and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Create `.env` from template:

```bash
cp .env.example .env
```

1. Bootstrap demo data:

```bash
python scripts/bootstrap_data.py
```

1. Run backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

1. Run dashboard (new terminal):

```bash
streamlit run app.py --server.port 8501
```

1. Open:

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

## Docker (Local)

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Useful health checks:

```bash
curl -sf http://127.0.0.1/api/health
curl -I -s http://127.0.0.1:8501 | head -n 1
curl -I -s http://127.0.0.1/ | head -n 1
```

View logs:

```bash
docker compose logs -f api
docker compose logs -f dashboard
docker compose logs -f nginx
```

Stop stack:

```bash
docker compose down
```

Services:

- Nginx: `http://localhost`
- FastAPI via Nginx: `http://localhost/api/docs`
- Streamlit behind Nginx root: `http://localhost/`

## API Endpoints

- `GET /health`
- `GET /tickets`
- `POST /tickets`
- `GET /tickets/{ticket_id}`
- `POST /drafts/generate`
- `GET /drafts/{ticket_id}`

## GitHub Actions

### CI Workflow

- File: `.github/workflows/ci.yml`
- Trigger: push/PR to `main`
- Runs: dependency install + pytest

### Docker Validation Workflow

- File: `.github/workflows/docker-validate.yml`
- Trigger: push/PR to `main`
- Runs: Docker image build checks for API and dashboard (no push)

### EC2 Deploy Workflow

- File: `.github/workflows/deploy-ec2.yml`
- Trigger: manual `workflow_dispatch` only
- What it does:
  1. Builds API and dashboard images
  2. Pushes images to GHCR
  3. Copies production compose + Nginx config to EC2
  4. Writes runtime `.env` on EC2 from GitHub Secrets
  5. Pulls latest images and restarts the stack
- Safety gate: deployment runs when input `confirm_deploy` is set to `DEPLOY`

## AWS Deployment Steps (EC2 + GitHub Actions)

### 1) Prerequisites

- AWS EC2 Ubuntu instance
- Security Group inbound rules: `22`, `80`, `443`
- SSH keypair available locally
- Repository admin access for GitHub secrets
- `gh` CLI installed locally

### 2) One-time EC2 setup

Run this once after SSH-ing into your EC2 box:

```bash
cd ~
git clone https://github.com/KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling.git support-copilot || true
cd support-copilot
bash deploy/ec2_setup.sh
```

Then reconnect to EC2 so Docker group membership is applied.

### 3) Authenticate GitHub CLI locally

Authenticate once on your local machine:

```bash
gh auth login -h github.com -p https -w
gh auth status
```

### 4) Add required GitHub secrets

Repository: `KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling`

```bash
gh secret set EC2_HOST --body "<your-ec2-public-ip-or-dns>" -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling
gh secret set EC2_USER --body "ubuntu" -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling
gh secret set EC2_SSH_KEY --body "$(cat ~/.ssh/<your-private-key-file>)" -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling
gh secret set OPENAI_API_KEY --body "<your-openai-api-key>" -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling
gh secret set MEM0_API_KEY --body "<your-mem0-api-key>" -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling
```

### 5) Trigger deployment

Option A: trigger manually using GitHub UI (`Deploy to EC2` workflow) and set `confirm_deploy=DEPLOY`.

Option B: trigger manually via CLI and pass confirmation gate:

```bash
gh workflow run "Deploy to EC2" \
  -R KartikSuryavanshi/AI-Powered-Customer-Support-Agent-with-Memory-and-Tool-Calling \
  -f confirm_deploy=DEPLOY
```

### 6) Verify in GitHub Actions

- Open Actions tab and confirm:
  - `CI` passes (tests)
  - `Docker Validate` passes (image build checks)
  - `Deploy to EC2` passes

### 7) Verify on EC2

```bash
ssh -i ~/.ssh/<your-private-key-file> ubuntu@<your-ec2-host>
cd ~/support-copilot
docker compose -f docker-compose.prod.yml ps
curl -sf http://127.0.0.1/api/health
```

Expected health response:

```json
{"status":"ok","app":"Support Copilot API"}
```

### Troubleshooting

- `gh auth status` fails:
  - Re-run `gh auth login -h github.com -p https -w` and complete browser/device flow.
- GHCR push denied:
  - Ensure workflow has `packages: write` permission (already configured).
- SSH/scp step fails:
  - Confirm `EC2_HOST`, `EC2_USER`, and `EC2_SSH_KEY` secret values.
- Containers restart but app not reachable:
  - Check EC2 Security Group allows inbound `80`.
  - Inspect logs: `docker compose -f docker-compose.prod.yml logs --tail=200`.

## Daily Workflow

1. Develop and test locally with Docker:

```bash
docker compose up -d --build
```

2. Push changes to GitHub:

```bash
git add .
git commit -m "feat: update support copilot"
git push origin main
```

3. Confirm `CI` and `Docker Validate` pass in GitHub Actions.

4. When you want a production rollout, run `Deploy to EC2` manually with `confirm_deploy=DEPLOY`.

## What You Can Extend Next

- Replace mock CRM/billing tools with real APIs
- Add Mem0 managed memory provider integration
- Add auth (JWT + RBAC)
- Add human approval workflow for draft publishing
- Add monitoring (Prometheus + Grafana + OpenTelemetry)
