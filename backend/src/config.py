from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResearchFlow API"
    app_env: str = "development"
    allowed_origin: str = "http://localhost:5173"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.moonshot.cn/v1"
    llm_model: str = "kimi-k2.5"
    llm_timeout_seconds: float = 60.0
    llm_retry_attempts: int = 3
    llm_retry_base_delay_seconds: float = 1.0
    llm_enable_query_rewrite: bool = True
    llm_enable_report_polish: bool = False
    search_provider: str = "tavily"
    search_fallback_provider: str = "duckduckgo"
    search_api_key: str = ""
    search_base_url: str = "https://api.tavily.com"
    search_top_k: int = 5
    search_snippet_max_chars: int = 400
    search_timeout_seconds: float = 20.0
    history_storage_dir: str = "workspace/history"
    export_storage_dir: str = "workspace/exports"
    cache_storage_dir: str = "workspace/cache"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
