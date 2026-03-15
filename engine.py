import json
import time
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config import settings
from schemas import TriageResult


PROMPT = ChatPromptTemplate.from_template(
    """
You are a support ticket triage engine.
Return ONLY valid JSON matching this schema:
{{
    "category": "Technical|Billing|Security|Sales",
    "urgency": 1-5 (based on business impact),
    "sentiment_score": -1.0 to 1.0,
    "summary": "<= 12 words"
}}

Rules:
- Use urgency 5 for outages, security incidents, login broken, or revenue blocked.
- Use urgency 1 for minor typos or low-impact requests.
- Do not include any extra keys.

Ticket:
{text}
""".strip()
)


def _provider_list() -> list[str]:
    providers = [p.strip() for p in settings.llm_providers.split(",") if p.strip()]
    filtered: list[str] = []
    for provider in providers:
        if provider == "openai" and not settings.openai_api_key:
            continue
        if provider == "anthropic" and not settings.anthropic_api_key:
            continue
        filtered.append(provider)
    return filtered


def _build_model(provider: str):
    if provider == "openai":
        model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
        return model.with_structured_output(TriageResult)
    if provider == "anthropic":
        model = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
        )
        return model.with_structured_output(TriageResult)
    if provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            format="json",
            temperature=0,
        )
    raise ValueError(f"Unsupported provider: {provider}")


def _coerce_result(data: Any) -> TriageResult:
    if isinstance(data, TriageResult):
        result = data
    elif isinstance(data, dict):
        result = TriageResult.model_validate(data)
    elif isinstance(data, str):
        result = TriageResult.model_validate(json.loads(data))
    else:
        raise ValueError("Unexpected model response type")

    urgency = max(1, min(5, int(result.urgency)))
    sentiment = max(-1.0, min(1.0, float(result.sentiment_score)))
    return TriageResult(
        category=result.category,
        urgency=urgency,
        sentiment_score=sentiment,
        summary=result.summary,
    )


def run_triage(text: str) -> tuple[TriageResult, str, int]:
    last_error = None
    for provider in _provider_list():
        try:
            model = _build_model(provider)
            chain = PROMPT | model
            start = time.perf_counter()
            response = chain.invoke({"text": text})
            latency_ms = int((time.perf_counter() - start) * 1000)
            return _coerce_result(response), provider, latency_ms
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(f"All providers failed: {last_error}")