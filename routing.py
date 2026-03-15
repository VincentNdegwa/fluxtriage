import httpx

from config import settings
from schemas import TriageResult


def dispatch_result(result: TriageResult, job_id: str) -> None:
    print(f"Dispatching result for job {job_id}: {result}")
    
    if result.urgency >= 5:
        url = settings.webhook_urgency_5_url
        route = "urgent"
    else:
        url = settings.webhook_standard_url
        route = "standard"

    if not url:
        raise RuntimeError("Webhook URL not configured")

    payload = {
        "job_id": job_id,
        "route": route,
        "category": result.category,
        "urgency": result.urgency,
        "sentiment_score": result.sentiment_score,
        "summary": result.summary,
    }

    with httpx.Client(timeout=10) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
