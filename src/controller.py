from __future__ import annotations

from dataclasses import dataclass
from typing import List
import pandas as pd

from src.services.dataset_service import prepare_dataset, DatasetInfo
from src.services.profiling_service import quick_profile, profile_to_text
from src.services.llm_service import generate_three_proposals
from src.services.viz_service import build_figure
from src.services.export_service import figure_to_png_bytes, create_dashboard_html

from src.models.viz_spec import ProposalsResponse, Proposal


@dataclass
class AppState:
    dataset: DatasetInfo
    proposals: ProposalsResponse


def prepare_all(uploaded_file) -> tuple[DatasetInfo, str]:
    dataset = prepare_dataset(uploaded_file)
    prof = quick_profile(dataset.df)
    prof_text = profile_to_text(prof)
    return dataset, prof_text


def get_proposals(question: str, dataset: DatasetInfo, profile_text: str) -> ProposalsResponse:
    return generate_three_proposals(question=question, schema=dataset.schema_summary, profile_text=profile_text)


def get_figure(df: pd.DataFrame, proposal: Proposal):
    return build_figure(df, proposal)


def get_png(fig) -> bytes:
    return figure_to_png_bytes(fig)


def get_html_dashboard(df: pd.DataFrame, proposals: List[Proposal], question: str, dataset_name: str) -> str:
    """
    Generate an HTML dashboard with all 3 visualizations.
    
    Args:
        df: The dataset
        proposals: List of all 3 proposals
        question: The business question
        dataset_name: Name of the dataset
    
    Returns:
        HTML dashboard as string
    """
    figures = []
    titles = []
    
    for proposal in proposals:
        try:
            fig = build_figure(df, proposal)
            figures.append(fig)
            titles.append(f"{proposal.title} ({proposal.chart_type})")
        except Exception as e:
            # Skip proposals that fail to generate
            continue
    
    return create_dashboard_html(figures, titles, question, dataset_name)

