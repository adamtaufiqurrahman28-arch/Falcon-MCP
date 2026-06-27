import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def str_to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Seraphim Digital Technology MCP")
    app_env: str = os.getenv("APP_ENV", "development")
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://103.93.129.20:8000/mcp")
    default_limit: int = int(os.getenv("DEFAULT_LIMIT", "10"))

    llm_enabled: bool = str_to_bool(os.getenv("LLM_ENABLED"), False)
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Redis audit trail
    redis_url: str | None = os.getenv("REDIS_URL")
    audit_enabled: bool = str_to_bool(os.getenv("AUDIT_ENABLED"), False)
    audit_stream_key: str = os.getenv("AUDIT_STREAM_KEY", "seraphim:mcp:audit")
    audit_max_len: int = int(os.getenv("AUDIT_MAX_LEN", "1000"))


settings = Settings()
