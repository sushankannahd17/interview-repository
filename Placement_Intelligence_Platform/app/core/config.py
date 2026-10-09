from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Placement Intelligence Platform"
    environment: str = "development"
    cors_allowed_origins: str = "http://localhost,http://localhost:5173,http://localhost:3000"

    # Supabase connection (primary data store via REST SDK)
    supabase_url: str = "https://your-project.supabase.co"
    supabase_key: str = "your-anon-or-service-role-key"

    # RabbitMQ / CloudAMQP connection
    amqp_url: str = "amqp://guest:guest@localhost:5672/"
    # v2 is durable; keep it separate from the old non-durable exp_queue during rollout.
    amqp_queue: str = "exp_queue_v2"
    dry_run: bool = False

    # Security and AI pipeline
    # Empty disables protected internal routes until a deployment key is set.
    internal_api_key: str = ""
    llm_api_key: str | None = None

    # LLM / embedding configuration
    llm_model: str = "gemini-3.5-flash-lite"
    embedding_model: str = "text-embedding-004"

    # Feature flags
    web_search_enabled: bool = False
    vector_search_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Return a cached Settings instance so env vars are read once at startup
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
