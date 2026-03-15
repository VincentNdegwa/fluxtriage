from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM providers in fallback order, e.g. "ollama,openai,anthropic"
    llm_providers: str = "ollama,openai"
    ollama_model: str = "llama3.1"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"

    # Observability (LangSmith)
    langsmith_tracing: bool = True
    langsmith_endpoint: str | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str = "fluxtriage"

    # Persistence
    database_url: str | None = None
    triage_table: str = "triage_events"

    # Async processing
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    # Routing webhooks
    webhook_urgency_5_url: str | None = None
    webhook_standard_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()