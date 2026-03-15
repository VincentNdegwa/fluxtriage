import os
from fastapi import FastAPI, HTTPException, status

from config import settings
from db import init_db
from schemas import TriageRequest, TriageResponse
from tasks import enqueue_triage


app = FastAPI(title="FluxTriage Production API")


@app.on_event("startup")
def startup() -> None:
    if settings.langsmith_tracing:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    if settings.langsmith_endpoint:
        os.environ.setdefault("LANGCHAIN_ENDPOINT", settings.langsmith_endpoint)
    if settings.langsmith_api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
    if settings.langsmith_project:
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)

    init_db()


@app.post("/triage", response_model=TriageResponse, status_code=status.HTTP_202_ACCEPTED)
async def triage_endpoint(payload: TriageRequest):
    if not settings.celery_broker_url:
        raise HTTPException(
            status_code=500,
            detail="CELERY_BROKER_URL is not configured",
        )
    if not settings.database_url:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL is not configured",
        )
    job_id = enqueue_triage(payload)
    return TriageResponse(job_id=job_id, status="queued")


@app.get("/health")
def health():
    return {
        "status": "live",
        "providers": settings.llm_providers,
        "celery_broker": bool(settings.celery_broker_url),
        "database": bool(settings.database_url),
    }