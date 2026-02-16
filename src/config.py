import os
from dataclasses import dataclass
from typing import Literal, Any
from dotenv import load_dotenv

load_dotenv()

def get_config_value(key: str, default: Any) -> Any:
    """
    Retrieve configuration value with priority:
    1. Streamlit Secrets (for Streamlit Cloud)
    2. Environment Variables (for local .env)
    3. Default value
    """
    try:
        # Check Streamlit Secrets
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        # Not in Streamlit environment or secrets not loaded
        pass
        
    # Fallback to OS environment
    val = os.getenv(key)
    if val is not None:
        return val
        
    return default

@dataclass(frozen=True)
class Settings:
    # LLM Configuration - Support both Claude and Gemini
    llm_provider: Literal["claude", "gemini"] = str(get_config_value("LLM_PROVIDER", "claude")).strip().lower()
    
    # Claude Configuration
    claude_api_key: str = str(get_config_value("CLAUDE_API_KEY", "")).strip()
    claude_model: str = str(get_config_value("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")).strip()
    
    # Gemini Configuration (fallback)
    gemini_api_key: str = str(get_config_value("GEMINI_API_KEY", "")).strip()
    gemini_model: str = str(get_config_value("GEMINI_MODEL", "gemini-flash-latest")).strip()

    # OpenAI Configuration (Optional)
    openai_api_key: str = str(get_config_value("OPENAI_API_KEY", "")).strip()
    openai_model: str = str(get_config_value("OPENAI_MODEL", "gpt-4-turbo-preview")).strip()

    # Dataset Configuration
    max_rows_preview: int = int(get_config_value("MAX_ROWS_PREVIEW", "50"))
    max_rows_analysis: int = int(get_config_value("MAX_ROWS_ANALYSIS", "10000"))
    max_schema_cols: int = int(get_config_value("MAX_SCHEMA_COLS", "100"))
    max_example_len: int = int(get_config_value("MAX_EXAMPLE_LEN", "80"))
    
    # Data Cleaning
    auto_clean: bool = str(get_config_value("AUTO_CLEAN", "true")).lower() == "true"
    missing_threshold: float = float(get_config_value("MISSING_THRESHOLD", "0.5"))
    
    # LLM Settings
    llm_max_retries: int = int(get_config_value("LLM_MAX_RETRIES", "3"))
    llm_temperature: float = float(get_config_value("LLM_TEMPERATURE", "0.1"))
    
    # Application Settings
    log_level: str = str(get_config_value("LOG_LEVEL", "INFO")).strip()
    enable_code_execution: bool = str(get_config_value("ENABLE_CODE_EXECUTION", "true")).lower() == "true"
    max_code_execution_time: int = int(get_config_value("MAX_CODE_EXECUTION_TIME", "30"))


settings = Settings()
