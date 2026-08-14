"""
MemoryOS Backend — Configuration
Loads all environment variables via Pydantic Settings.
See .env.example for the full list and where to get each value.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- App ---
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")

    # --- Database (Supabase PostgreSQL) ---
    database_url: str = Field(..., alias="DATABASE_URL")

    # --- Supabase ---
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_service_key: str = Field(..., alias="SUPABASE_SERVICE_KEY")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")

    # --- Qdrant Cloud ---
    qdrant_url: str = Field(..., alias="QDRANT_URL")
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")

    # --- Upstash Redis ---
    upstash_redis_rest_url: str = Field(default="", alias="UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token: str = Field(default="", alias="UPSTASH_REDIS_REST_TOKEN")

    # --- Gemini API ---
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")

    # --- Auth (JWT) ---
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=1440, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:5173", alias="CORS_ORIGINS"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # --- Embedding Config ---
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimension: int = 3072

    # --- LLM Config ---
    llm_model: str = "gemini-3-flash-preview"
    llm_max_output_tokens: int = 4096
    llm_temperature: float = 0.7

    # --- Retrieval Config ---
    retrieval_top_k: int = 8
    context_token_budget: int = 6000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — loaded once, reused everywhere."""
    return Settings()
