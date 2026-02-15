"""
Safe code execution service for running generated visualization code.
"""
from __future__ import annotations

import sys
import io
import logging
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import statsmodels.api as sm
from contextlib import redirect_stdout, redirect_stderr

from src.config import settings

log = logging.getLogger(__name__)


def execute_visualization_code(
    code: str,
    df: pd.DataFrame,
    timeout: int = None
) -> Tuple[Optional[go.Figure], Optional[str], Optional[str]]:
    """
    Safely execute generated visualization code.
    
    Args:
        code: Python code to execute
        df: DataFrame to make available to the code
        timeout: Maximum execution time in seconds
    
    Returns:
        Tuple of (figure, stdout, error_message)
    """
    if timeout is None:
        timeout = settings.max_code_execution_time
    
    if not settings.enable_code_execution:
        return None, None, "Code execution is disabled in settings"
    
    # Prepare execution environment
    exec_globals = {
        'pd': pd,
        'px': px,
        'go': go,
        'np': np,
        'sm': sm,
        'df': df,
        'fig': None
    }
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Execute the code
            exec(code, exec_globals)
        
        # Get the figure
        fig = exec_globals.get('fig')
        
        if fig is None:
            return None, stdout_capture.getvalue(), "Code did not produce a 'fig' variable"
        
        if not isinstance(fig, (go.Figure, type(px.scatter(pd.DataFrame())))):
            return None, stdout_capture.getvalue(), f"'fig' is not a plotly Figure (got {type(fig)})"
        
        log.info("Code executed successfully")
        return fig, stdout_capture.getvalue(), None
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        log.error(f"Code execution failed: {error_msg}")
        return None, stdout_capture.getvalue(), error_msg


def test_code_execution() -> bool:
    """
    Test if code execution is working properly.
    
    Returns:
        True if test passes, False otherwise
    """
    test_code = """
import plotly.express as px
fig = px.scatter(df, x=df.columns[0], y=df.columns[1] if len(df.columns) > 1 else df.columns[0])
"""
    
    test_df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 6, 8, 10]
    })
    
    fig, stdout, error = execute_visualization_code(test_code, test_df)
    
    if error:
        log.error(f"Code execution test failed: {error}")
        return False
    
    if fig is None:
        log.error("Code execution test failed: No figure produced")
        return False
    
    log.info("Code execution test passed")
    return True


def format_code_for_display(code: str) -> str:
    """
    Format code for nice display in the UI.
    """
    # Remove excessive blank lines
    lines = code.split('\n')
    formatted_lines = []
    prev_blank = False
    
    for line in lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        formatted_lines.append(line)
        prev_blank = is_blank
    
    return '\n'.join(formatted_lines)


def extract_imports(code: str) -> list[str]:
    """
    Extract import statements from code.
    """
    import_lines = []
    for line in code.split('\n'):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            import_lines.append(stripped)
    return import_lines
