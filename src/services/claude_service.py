"""
Enhanced Claude service for senior data analyst approach.
Proposes multiple relevant visualizations with comprehensive interpretations.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional
import anthropic
import json

from src.config import settings

log = logging.getLogger(__name__)


SENIOR_ANALYST_SYSTEM_PROMPT = """You are a senior data analyst with 15+ years of experience in data visualization and business intelligence.

Your role is to:
1. Analyze datasets comprehensively
2. Propose the MOST RELEVANT visualizations based on data characteristics
3. Provide deep, actionable insights like a senior analyst would
4. Consider business context and practical implications
5. Generate clean, executable Python code using plotly

Guidelines:
- Propose 3-5 different visualizations that tell a complete story
- Each visualization should reveal different aspects of the data
- Prioritize clarity and business value over complexity
- Use modern, professional aesthetics (blue gradient theme)
- Include detailed interpretations with specific numbers
- Suggest actionable recommendations

Available libraries (already imported):
- pandas as pd
- plotly.express as px
- plotly.graph_objects as go
- numpy as np
- statsmodels.api as sm
"""


PROPOSAL_GENERATION_PROMPT = """Analyze this dataset and propose the most relevant visualizations.

**Dataset Context:**
{context}

**Dataset Schema:**
{schema}

**Column Types:**
{column_types}

**Sample Data:**
{sample_data}

**Statistical Summary:**
{stats_summary}

**Your Task:**
As a senior data analyst, propose 3-5 visualizations that would provide the most valuable insights from this data.

For each visualization, provide:
1. **Title**: Clear, descriptive title
2. **Type**: Chart type (bar, line, scatter, box, heatmap, etc.)
3. **Purpose**: What business question does this answer?
4. **Code**: Complete Python code using plotly (assign to variable 'fig')
5. **Interpretation**: Detailed analysis with specific insights (3-5 sentences)
6. **Recommendations**: Actionable next steps based on findings

Return your response as a JSON array with this structure:
```json
[
  {{
    "title": "...",
    "chart_type": "...",
    "purpose": "...",
    "code": "...",
    "interpretation": "...",
    "recommendations": "..."
  }},
  ...
]
```

Focus on visualizations that:
- Reveal patterns and trends
- Identify outliers or anomalies
- Show relationships between variables
- Support data-driven decision making
- Are appropriate for the data types present

Return ONLY the JSON array, no additional text.
"""


def _ensure_claude_key() -> None:
    """Ensure Claude API key is configured."""
    if not settings.claude_api_key:
        raise RuntimeError("CLAUDE_API_KEY missing. Add it to your .env file.")


def generate_analysis_proposals(
    dataset_context: str,
    schema: str,
    sample_data: str,
    column_types: Dict[str, str],
    stats_summary: str
) -> List[Dict]:
    """
    Generate multiple visualization proposals as a senior data analyst.
    
    Args:
        dataset_context: User-provided context about the data
        schema: Dataset schema description
        sample_data: Sample rows from dataset
        column_types: Detected column types
        stats_summary: Statistical summary of the data
    
    Returns:
        List of visualization proposals with code and interpretations
    """
    _ensure_claude_key()
    
    client = anthropic.Anthropic(api_key=settings.claude_api_key)
    
    # Build column types description
    types_desc = "\n".join([f"- {col}: {dtype}" for col, dtype in column_types.items()])
    
    user_prompt = PROPOSAL_GENERATION_PROMPT.format(
        context=dataset_context or "No specific context provided",
        schema=schema,
        column_types=types_desc,
        sample_data=sample_data,
        stats_summary=stats_summary
    )
    
    last_error = None
    for attempt in range(settings.llm_max_retries):
        try:
            response = client.messages.create(
                model=settings.claude_model,
                max_tokens=4000,
                temperature=settings.llm_temperature,
                system=SENIOR_ANALYST_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            content = response.content[0].text
            
            # Extract JSON from response
            proposals = extract_json_from_response(content)
            
            if not proposals or not isinstance(proposals, list):
                raise ValueError("Invalid response format")
            
            log.info(f"Generated {len(proposals)} visualization proposals")
            return proposals
            
        except Exception as e:
            last_error = e
            log.warning(f"Proposal generation attempt {attempt + 1} failed: {e}")
    
    raise RuntimeError(f"Failed to generate proposals after {settings.llm_max_retries} attempts: {last_error}")


def generate_visualization_code(
    question: str,
    schema: str,
    sample_data: str,
    column_types: Dict[str, str]
) -> str:
    """
    Generate Python code for a specific visualization request.
    
    Args:
        question: User's specific question
        schema: Dataset schema
        sample_data: Sample data
        column_types: Column types
    
    Returns:
        Executable Python code
    """
    _ensure_claude_key()
    
    client = anthropic.Anthropic(api_key=settings.claude_api_key)
    
    types_desc = "\n".join([f"- {col}: {dtype}" for col, dtype in column_types.items()])
    
    user_prompt = f"""
Generate Python code to create a visualization that answers this question:

**Question**: {question}

**Dataset Schema**:
{schema}

**Column Types**:
{types_desc}

**Sample Data**:
{sample_data}

Requirements:
1. Create ONE visualization using plotly
2. Use modern, professional styling (blue gradient theme preferred)
3. Include clear titles, labels, and legends
4. Apply appropriate aggregations if needed
5. Assign the figure to variable 'fig'

Return ONLY the Python code, no explanations.
"""
    
    try:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=2000,
            temperature=settings.llm_temperature,
            system=SENIOR_ANALYST_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        code = response.content[0].text
        code = extract_code_from_markdown(code)
        
        log.info(f"Generated visualization code ({len(code)} chars)")
        return code
        
    except Exception as e:
        log.error(f"Failed to generate code: {e}")
        raise


def generate_comprehensive_interpretation(
    visualization_title: str,
    chart_type: str,
    data_summary: str,
    context: str = ""
) -> Dict[str, str]:
    """
    Generate comprehensive interpretation for a visualization.
    
    Returns:
        Dict with 'interpretation' and 'recommendations'
    """
    _ensure_claude_key()
    
    client = anthropic.Anthropic(api_key=settings.claude_api_key)
    
    user_prompt = f"""
Provide a comprehensive analysis of this visualization:

**Visualization**: {visualization_title} ({chart_type})
**Context**: {context or "General data analysis"}
**Data Summary**: {data_summary}

Provide:
1. **Key Findings** (3-5 specific insights with numbers)
2. **Interpretation** (What does this mean for the business/domain?)
3. **Recommendations** (2-3 actionable next steps)

Be specific, use data points, and think like a senior analyst presenting to stakeholders.

Return as JSON:
{{
  "interpretation": "...",
  "recommendations": "..."
}}
"""
    
    try:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=1500,
            temperature=0.3,
            system=SENIOR_ANALYST_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = response.content[0].text
        result = extract_json_from_response(content)
        
        return result if isinstance(result, dict) else {
            "interpretation": content,
            "recommendations": "See interpretation above."
        }
        
    except Exception as e:
        log.error(f"Failed to generate interpretation: {e}")
        return {
            "interpretation": "Unable to generate interpretation at this time.",
            "recommendations": "Please review the visualization manually."
        }


def extract_json_from_response(text: str):
    """
    Extract JSON from Claude's response.
    """
    # Try to find JSON in code blocks
    json_pattern = r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    # Try to find JSON without code blocks
    try:
        # Find first [ or {
        start_idx = min(
            (text.find('[') if '[' in text else len(text)),
            (text.find('{') if '{' in text else len(text))
        )
        
        if start_idx < len(text):
            # Find matching closing bracket
            if text[start_idx] == '[':
                end_char = ']'
            else:
                end_char = '}'
            
            # Simple bracket matching
            count = 0
            for i in range(start_idx, len(text)):
                if text[i] == text[start_idx]:
                    count += 1
                elif text[i] == end_char:
                    count -= 1
                    if count == 0:
                        json_str = text[start_idx:i+1]
                        return json.loads(json_str)
    except:
        pass
    
    # If all else fails, try to parse the whole thing
    try:
        return json.loads(text)
    except:
        raise ValueError("Could not extract valid JSON from response")


def extract_code_from_markdown(text: str) -> str:
    """
    Extract Python code from markdown code blocks.
    """
    pattern = r'```(?:python)?\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    return text.strip()


def validate_code_safety(code: str) -> bool:
    """
    Basic safety check for generated code.
    """
    dangerous_patterns = [
        r'\bimport\s+os\b',
        r'\bimport\s+sys\b',
        r'\bimport\s+subprocess\b',
        r'\bexec\s*\(',
        r'\beval\s*\(',
        r'\b__import__\s*\(',
        r'\bopen\s*\(',
        r'\.write\s*\(',
        r'\.remove\s*\(',
        r'\.delete\s*\(',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            log.warning(f"Potentially unsafe code detected: {pattern}")
            return False
    
    return True
