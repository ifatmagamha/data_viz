"""
Unified LLM Router - Handles multi-provider support and automatic fallbacks.
Supports Claude (Primary) and Gemini (Fallback).
"""
import logging
from typing import Dict, List, Optional
import json
from src.config import settings
from src.services import claude_service

log = logging.getLogger(__name__)

def generate_analysis_proposals(
    dataset_context: str,
    schema: str,
    sample_data: str,
    column_types: Dict[str, str],
    stats_summary: str
) -> List[Dict]:
    """
    Route proposal generation to the selected provider with automatic fallback.
    """
    primary = settings.llm_provider
    providers = ["claude", "gemini"] if primary == "claude" else ["gemini", "claude"]
    
    last_error = None
    
    for provider in providers:
        try:
            if provider == "claude":
                if not settings.claude_api_key or "your_claude" in settings.claude_api_key:
                    log.warning("Claude API key not configured or placeholder.")
                    continue
                log.info("Attempting analysis with Claude...")
                return claude_service.generate_analysis_proposals(
                    dataset_context, schema, sample_data, column_types, stats_summary
                )
            elif provider == "gemini":
                if not settings.gemini_api_key or "your_gemini" in settings.gemini_api_key:
                    log.warning("Gemini API key not configured or placeholder.")
                    continue
                log.info("Attempting analysis with Gemini...")
                return generate_proposals_gemini(
                    dataset_context, schema, sample_data, column_types, stats_summary
                )
        except Exception as e:
            last_error = e
            log.warning(f"{provider.capitalize()} failed: {e}")
            
    if last_error:
        # If we got a specific error like invalid key or billing, raise it clearly
        raise RuntimeError(f"Analysis failed: {str(last_error)}")
    else:
        raise RuntimeError("No valid LLM API keys found in .env. Please check CLAUDE_API_KEY or GEMINI_API_KEY.")

def generate_proposals_gemini(
    dataset_context: str,
    schema: str,
    sample_data: str,
    column_types: Dict[str, str],
    stats_summary: str
) -> List[Dict]:
    """
    Implementation for Gemini using the modern google-genai SDK.
    """
    try:
        from google import genai
    except ImportError:
        log.error("google-genai package not found. Falling back to legacy generativeai.")
        return generate_proposals_gemini_legacy(dataset_context, schema, sample_data, column_types, stats_summary)

    client = genai.Client(api_key=settings.gemini_api_key)
    
    # Use the same prompts from claude_service for consistency
    from src.services.claude_service import SENIOR_ANALYST_SYSTEM_PROMPT, PROPOSAL_GENERATION_PROMPT, extract_json_from_response
    
    types_desc = "\n".join([f"- {col}: {dtype}" for col, dtype in column_types.items()])
    
    user_prompt = PROPOSAL_GENERATION_PROMPT.format(
        context=dataset_context or 'No specific context provided',
        schema=schema,
        column_types=types_desc,
        sample_data=sample_data,
        stats_summary=stats_summary
    )
    
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=user_prompt,
            config={
                'system_instruction': SENIOR_ANALYST_SYSTEM_PROMPT,
                'temperature': settings.llm_temperature,
            }
        )
        
        return extract_json_from_response(response.text)
    except Exception as e:
        if "API key not valid" in str(e):
            raise ValueError("Gemini API key is invalid. Please check your .env file and ensure the key is correct.")
        raise e

def generate_proposals_gemini_legacy(
    dataset_context: str,
    schema: str,
    sample_data: str,
    column_types: Dict[str, str],
    stats_summary: str
) -> List[Dict]:
    """Fallback legacy implementation using google-generativeai."""
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    
    # In legacy SDK, system_instruction is passed to the model constructor
    # of newer models, but some versions/models might fail.
    # We wrap the whole process in a refined prompt for stability.
    
    types_desc = "\n".join([f"- {col}: {dtype}" for col, dtype in column_types.items()])
    
    from src.services.claude_service import SENIOR_ANALYST_SYSTEM_PROMPT, PROPOSAL_GENERATION_PROMPT, extract_json_from_response
    
    # For legacy, we combine system prompt + user prompt if constructor fails
    full_prompt = f"{SENIOR_ANALYST_SYSTEM_PROMPT}\n\n{PROPOSAL_GENERATION_PROMPT.format(context=dataset_context or 'No specific context provided', schema=schema, column_types=types_desc, sample_data=sample_data, stats_summary=stats_summary)}"

    try:
        model = genai.GenerativeModel(model_name=settings.gemini_model)
        response = model.generate_content(full_prompt)
        return extract_json_from_response(response.text)
    except Exception as e:
        if "403" in str(e):
             raise RuntimeError(f"Gemini API access forbidden. Ensure the model '{settings.gemini_model}' is enabled for your API key in Google AI Studio.")
        raise e
