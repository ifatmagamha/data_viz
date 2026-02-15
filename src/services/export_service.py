"""
Export service for generating professional data reports.
"""
from __future__ import annotations

import plotly.graph_objects as go
from typing import List, Optional
from datetime import datetime
import base64
import json

def create_dashboard_html(
    figures: List[go.Figure],
    titles: List[str],
    interpretations: List[str],
    recommendations: List[str],
    question: str,
    dataset_name: Optional[str] = None,
) -> str:
    """
    Create a professional HTML report with senior analyst aesthetics and insights.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convert each figure and its analysis to HTML
    analysis_htmls = []
    for i, (fig, title, interp, rec) in enumerate(zip(figures, titles, interpretations, recommendations)):
        chart_html = fig.to_html(
            include_plotlyjs='cdn' if i == 0 else False,
            full_html=False,
            div_id=f"chart_{i}"
        )
        analysis_htmls.append(f"""
        <div class="analysis-block">
            <h3 class="block-title">{i+1}. {title}</h3>
            <div class="chart-container">
                {chart_html}
            </div>
            <div class="insight-container">
                <div class="insight-section">
                    <h4>Senior Analyst Interpretation</h4>
                    <p>{interp}</p>
                </div>
                <div class="recommendation-section">
                    <h4>Actionable Recommendations</h4>
                    <p>{rec}</p>
                </div>
            </div>
        </div>
        """)
    
    content_section = "\n".join(analysis_htmls)
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Data Analysis Report - {dataset_name or 'Auto DataViz'}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #f8fafc;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --primary: #3b82f6;
                --card-bg: #ffffff;
                --border: #e2e8f0;
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text-main);
                line-height: 1.6;
                padding-bottom: 5rem;
            }}
            
            .container {{ max-width: 1000px; margin: 0 auto; padding: 0 1.5rem; }}
            
            header {{
                padding: 5rem 0 3rem 0;
                border-bottom: 2px solid var(--border);
                margin-bottom: 4rem;
            }}
            
            header h1 {{
                font-size: 3rem;
                font-weight: 800;
                letter-spacing: -0.04em;
                margin-bottom: 1rem;
            }}
            
            .metadata {{ color: var(--text-muted); font-weight: 500; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.1em; }}
            
            .context-box {{
                background: white;
                padding: 2.5rem;
                border-radius: 16px;
                border: 1px solid var(--border);
                margin-bottom: 4rem;
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05);
            }}
            
            .context-box h2 {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 1rem; }}
            
            .analysis-block {{ margin-bottom: 6rem; }}
            .block-title {{ font-size: 1.75rem; font-weight: 700; margin-bottom: 2rem; color: var(--text-main); }}
            
            .chart-container {{
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                border: 1px solid var(--border);
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            }}
            
            .insight-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
            }}
            
            .insight-section, .recommendation-section {{
                padding: 2rem;
                background: white;
                border-radius: 16px;
                border: 1px solid var(--border);
            }}
            
            .insight-section {{ border-left: 5px solid var(--primary); }}
            .recommendation-section {{ border-left: 5px solid #ec4899; }}
            
            h4 {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1.5rem; font-weight: 700; }}
            .insight-section h4 {{ color: var(--primary); }}
            .recommendation-section h4 {{ color: #ec4899; }}
            
            p {{ font-size: 1.05rem; color: #334155; }}
            
            footer {{ text-align: center; color: var(--text-muted); padding-top: 5rem; border-top: 2px solid var(--border); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="metadata">Analysis Report • {timestamp}</div>
                <h1>{dataset_name or 'Auto DataViz'} Results</h1>
            </header>
            
            <div class="context-box">
                <h2>Business Context</h2>
                <p>{question or 'Comprehensive exploratory data analysis focused on discovering significant patterns and strategic insights.'}</p>
            </div>
            
            {content_section}
            
            <footer>
                <p>Generated by Auto DataViz Senior Analyst Engine</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html_template
