<!-- a16307d0-986b-4eba-b40f-26e30e8f1262 1fcf9d9e-d71a-40b5-b38c-b4a2a4376402 -->
### Slim API-Only Docker + Local Test + CI

#### Goals
- Build a small, reliable API image (FastAPI + DB + email + scheduler)
- Remove heavy ML/RAG deps from the image
- Keep LLM/Ollama external (host-only), not inside the image
- Test locally with Docker, then add CI (build + lint + test)

#### Changes (files to edit/add)
- `backend/requirements-server.txt` (new): minimal deps for the API only.
- `backend/Dockerfile` (edit): install from `requirements-server.txt`, keep multi-stage, non-root, healthcheck, entrypoint.
- `docker-compose.yml` (confirm): only `db` and `api`; envs sourced from root `.env`; healthchecks; volumes only for data/logs.
- `backend/docker-entrypoint.sh` (confirm): wait-for-DB loop, run migrations/create tables, then start Uvicorn.
- `.env` (local): API/db/email vars; no MLflow; no heavy RAG vars.
- `.github/workflows/ci.yml` (new): lint, type-check, unit tests, and Docker build on push to `main`.

#### Minimal content (concise snippets)
- `backend/requirements-server.txt`
```text
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.34
psycopg2-binary==2.9.9
pydantic==2.9.2
email-validator==2.1.0
httpx==0.27.2
python-dotenv==1.0.1
apscheduler==3.10.4
```

- `backend/Dockerfile` (key edits only)
```Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements-server.txt ./requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser && \
    apt-get update && apt-get install -y --no-install-recommends libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /home/appuser/.local
COPY app ./app
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["/app/docker-entrypoint.sh"]
```

- `.env` (local)
```text
ENVIRONMENT=development
LOG_LEVEL=INFO
API_PORT=8000
POSTGRES_USER=defi_user
POSTGRES_PASSWORD=usersafety
POSTGRES_DB=defi_risk_assessment
POSTGRES_PORT=5432
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASSWORD=app_password
EMAIL_FROM=you@example.com
EMAIL_FROM_NAME=SafeFi Alert System
# LLM kept external; not baked into image
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
```

- `.github/workflows/ci.yml` (high level)
```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install deps (server-only)
        run: |
          pip install -r backend/requirements-server.txt
      - name: Lint & Type check
        run: |
          pip install ruff mypy
          ruff check backend/app
          mypy backend/app --ignore-missing-imports
      - name: Unit tests
        run: |
          pip install pytest
          pytest -q
      - name: Docker build api
        run: |
          docker build -t safefi-api:ci -f backend/Dockerfile backend
```

#### Local test steps
1) From project root: `cp backend/requirements-server.txt backend/requirements.txt` (optional, if Dockerfile copies requirements-server.txt directly, skip).
2) Ensure `.env` exists at root (values above).
3) `docker compose down`
4) `docker compose build --no-cache api`
5) `docker compose up -d`
6) `docker compose ps` and `docker compose logs -f api`
7) Verify: `curl http://localhost:8000/health` and `curl "http://localhost:8000/protocols?limit=5"`.

#### VM deploy (manual, after local success)
- SSH, `git pull`, ensure `.env` at `/var/lib/postgresql/SafeFi_project1`, then:
```
cd /var/lib/postgresql/SafeFi_project1
sudo docker compose down --volumes --remove-orphans
sudo docker compose build --no-cache api
sudo docker compose up -d
sudo docker compose ps
sudo docker compose logs -f api
```

#### Notes
- Frontend remains in GCS; no change here.
- If disk space issues occur on the VM, prune Docker and rebuild.
- LLM can run on host (Ollama) if needed; API calls it via OLLAMA_BASE_URL.


### To-dos

- [ ] Add backend/requirements-server.txt with slim API deps
- [ ] Edit backend/Dockerfile to install requirements-server.txt
- [ ] Verify .env and docker-compose.yml (db+api only)
- [ ] Build and run docker locally; verify health endpoints
- [ ] Add .github/workflows/ci.yml for lint, tests, docker build
- [ ] Manual deploy on VM: pull, build, up, verify