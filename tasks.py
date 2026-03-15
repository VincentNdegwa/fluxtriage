import uuid
from celery import Celery

from config import settings
from db import insert_event, update_event
from engine import run_triage
from routing import dispatch_result
from schemas import TriageRequest


celery_app = Celery(
    "fluxtriage",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend or settings.celery_broker_url,
)


def enqueue_triage(request: TriageRequest) -> str:
    job_id = uuid.uuid4().hex
    insert_event(job_id, request.model_dump())
    process_triage.delay(job_id, request.model_dump())
    return job_id


@celery_app.task(name="fluxtriage.process_triage")
def process_triage(job_id: str, request_dict: dict) -> None:
    error = None
    provider = None
    latency_ms = None
    result_payload = None

    try:
        result, provider, latency_ms = run_triage(request_dict["raw_content"])
        dispatch_result(result, job_id)
        result_payload = result.model_dump()
    except Exception as exc:
        error = str(exc)
    finally:
        update_event(
            job_id=job_id,
            result=result_payload,
            provider=provider,
            latency_ms=latency_ms,
            error=error,
        )
