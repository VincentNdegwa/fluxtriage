FluxTriage
===========

Production-ready support ticket triage with multi-provider LLM fallback, async processing, persistence, and routing.

Key Features
------------
- Multi-provider fallback: Ollama -> OpenAI -> Anthropic (configurable)
- Async processing via Celery (202 Accepted, background triage)
- Strict structured output using Pydantic + JSON guardrails
- Observability via LangSmith tracing
- Postgres persistence for auditability
- Actionable routing via webhooks

Architecture
------------
```mermaid
flowchart LR
		A[Clients] -->|POST /triage| B[FastAPI]
		B -->|enqueue| C[Celery Worker]
		C --> D[LLM Fallback Engine]
		D -->|Triage Result| C
		C -->|persist| E[(Postgres)]
		C -->|dispatch| F[Webhook Router]
		F --> G[Urgent Alert]
		F --> H[Standard Queue]
		C --> I[LangSmith]
```

Environment Variables
---------------------
Set these in your shell or `.env` file:

```
# LLM Providers
LLM_PROVIDERS=ollama,openai,anthropic
OLLAMA_MODEL=llama3.1
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-3-5-sonnet-latest

# Persistence
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.your-supabase-host:5432/postgres
TRIAGE_TABLE=triage_events

# Async (Celery)
CELERY_BROKER_URL=redis://:password@your-redis:6379/0
CELERY_RESULT_BACKEND=redis://:password@your-redis:6379/0

# Webhooks
WEBHOOK_URGENCY_5_URL=https://hooks.slack.com/services/...
WEBHOOK_STANDARD_URL=https://your-standard-queue/endpoint

# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=fluxtriage
```

Run
---
1) Start the API

```
uvicorn main:app --reload
```

2) Start Celery worker

```
celery -A tasks.celery_app worker --loglevel=info
```

API Example
-----------
```
curl -X POST http://localhost:8000/triage \
	-H "Content-Type: application/json" \
	-d '{"source":"email","raw_content":"Login is down for all users.","metadata":{"account":"acme"}}'
```
