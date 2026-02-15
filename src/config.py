from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # LLM Configuration - Support both Claude and Gemini
    llm_provider: Literal["claude", "gemini"] = os.getenv("LLM_PROVIDER", "claude").strip().lower()
    
    # Claude Configuration
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "").strip()
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022").strip()
    
    # Gemini Configuration (fallback)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

    # Dataset Configuration
    max_rows_preview: int = int(os.getenv("MAX_ROWS_PREVIEW", "50"))
    max_rows_analysis: int = int(os.getenv("MAX_ROWS_ANALYSIS", "10000"))
    max_schema_cols: int = int(os.getenv("MAX_SCHEMA_COLS", "100"))
    max_example_len: int = int(os.getenv("MAX_EXAMPLE_LEN", "80"))
    
    # Data Cleaning
    auto_clean: bool = os.getenv("AUTO_CLEAN", "true").lower() == "true"
    missing_threshold: float = float(os.getenv("MISSING_THRESHOLD", "0.5"))
    
    # LLM Settings
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # Application Settings
    log_level: str = os.getenv("LOG_LEVEL", "INFO").strip()
    enable_code_execution: bool = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    max_code_execution_time: int = int(os.getenv("MAX_CODE_EXECUTION_TIME", "30"))


settings = Settings()
