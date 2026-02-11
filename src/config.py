from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    max_rows_preview: int = int(os.getenv("MAX_ROWS_PREVIEW", "30"))
    max_schema_cols: int = int(os.getenv("MAX_SCHEMA_COLS", "60"))
    max_example_len: int = int(os.getenv("MAX_EXAMPLE_LEN", "60"))

    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()


settings = Settings()
