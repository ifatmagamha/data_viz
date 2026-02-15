"""
Pytest configuration and fixtures for the Auto DataViz project.
"""
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        'genre': ['Action', 'Comedy', 'Drama', 'Action', 'Comedy', 'Drama'],
        'rating': [8.5, 7.2, 9.1, 7.8, 6.9, 8.7],
        'revenue': [100, 50, 80, 120, 45, 90],
        'year': [2020, 2021, 2020, 2021, 2022, 2022],
        'director': ['A', 'B', 'C', 'A', 'B', 'C']
    })


@pytest.fixture
def sample_csv_file(tmp_path, sample_df):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_proposal_dict():
    """Sample proposal dictionary for testing."""
    return {
        "id": 1,
        "title": "Average Rating by Genre",
        "chart_type": "bar",
        "x": "genre",
        "y": "rating",
        "color": None,
        "aggregation": "mean",
        "filters": [],
        "reasoning": "This visualization shows the average rating for each genre.",
        "formatting": {
            "x_label": "Genre",
            "y_label": "Average Rating",
            "sort": "desc",
            "top_k": 20
        }
    }


@pytest.fixture
def sample_proposals_response():
    """Sample proposals response for testing."""
    return {
        "proposals": [
            {
                "id": 1,
                "title": "Average Rating by Genre",
                "chart_type": "bar",
                "x": "genre",
                "y": "rating",
                "aggregation": "mean",
                "filters": [],
                "reasoning": "Shows average rating per genre",
                "formatting": {"x_label": "Genre", "y_label": "Rating", "sort": "desc", "top_k": 20}
            },
            {
                "id": 2,
                "title": "Revenue Distribution",
                "chart_type": "hist",
                "x": "revenue",
                "aggregation": "none",
                "filters": [],
                "reasoning": "Shows revenue distribution",
                "formatting": {"x_label": "Revenue", "y_label": "Count", "sort": None, "top_k": 20}
            },
            {
                "id": 3,
                "title": "Rating vs Revenue",
                "chart_type": "scatter",
                "x": "rating",
                "y": "revenue",
                "color": "genre",
                "aggregation": "none",
                "filters": [],
                "reasoning": "Shows relationship between rating and revenue",
                "formatting": {"x_label": "Rating", "y_label": "Revenue", "sort": None, "top_k": 20}
            }
        ]
    }
