"""
Unit tests for viz_service module.
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
from src.services.viz_service import apply_filters, aggregate_if_needed, build_figure
from src.models.viz_spec import Proposal, FilterSpec, FormattingSpec


def test_apply_filters_equality(sample_df):
    """Test filtering with equality operator."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[FilterSpec(col="genre", op="==", value="Action")]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert len(filtered) == 2  # Only Action movies
    assert all(filtered['genre'] == 'Action')


def test_apply_filters_inequality(sample_df):
    """Test filtering with inequality operator."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[FilterSpec(col="genre", op="!=", value="Action")]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert all(filtered['genre'] != 'Action')


def test_apply_filters_greater_than(sample_df):
    """Test filtering with greater than operator."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[FilterSpec(col="rating", op=">", value=8.0)]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert all(filtered['rating'] > 8.0)


def test_apply_filters_less_than(sample_df):
    """Test filtering with less than operator."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[FilterSpec(col="rating", op="<", value=8.0)]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert all(filtered['rating'] < 8.0)


def test_apply_filters_in_operator(sample_df):
    """Test filtering with 'in' operator."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[FilterSpec(col="genre", op="in", value=["Action", "Comedy"])]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert all(filtered['genre'].isin(["Action", "Comedy"]))


def test_apply_filters_multiple(sample_df):
    """Test applying multiple filters."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        filters=[
            FilterSpec(col="genre", op="!=", value="Drama"),
            FilterSpec(col="rating", op=">", value=7.0)
        ]
    )
    
    filtered = apply_filters(sample_df, proposal)
    assert all(filtered['genre'] != 'Drama')
    assert all(filtered['rating'] > 7.0)


def test_aggregate_mean(sample_df):
    """Test mean aggregation."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        aggregation="mean"
    )
    
    aggregated = aggregate_if_needed(sample_df, proposal)
    assert len(aggregated) == 3  # 3 unique genres
    assert 'genre' in aggregated.columns
    assert 'rating' in aggregated.columns


def test_aggregate_sum(sample_df):
    """Test sum aggregation."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="revenue",
        aggregation="sum"
    )
    
    aggregated = aggregate_if_needed(sample_df, proposal)
    assert len(aggregated) == 3
    # Action revenue should be 100 + 120 = 220
    action_revenue = aggregated[aggregated['genre'] == 'Action']['revenue'].iloc[0]
    assert action_revenue == 220


def test_aggregate_with_sort(sample_df):
    """Test aggregation with sorting."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        aggregation="mean",
        formatting=FormattingSpec(sort="desc")
    )
    
    aggregated = aggregate_if_needed(sample_df, proposal)
    # Check that ratings are in descending order
    ratings = aggregated['rating'].tolist()
    assert ratings == sorted(ratings, reverse=True)


def test_aggregate_with_top_k(sample_df):
    """Test aggregation with top_k limit."""
    # Create a larger dataset
    large_df = pd.DataFrame({
        'category': [f'cat_{i}' for i in range(50)],
        'value': list(range(50))
    })
    
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="category",
        y="value",
        aggregation="mean",
        formatting=FormattingSpec(top_k=10)
    )
    
    aggregated = aggregate_if_needed(large_df, proposal)
    assert len(aggregated) <= 10


def test_build_figure_bar(sample_df, sample_proposal_dict):
    """Test building a bar chart."""
    proposal = Proposal(**sample_proposal_dict)
    fig = build_figure(sample_df, proposal)
    
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Average Rating by Genre"


def test_build_figure_scatter(sample_df):
    """Test building a scatter plot."""
    proposal = Proposal(
        id=1,
        title="Rating vs Revenue",
        chart_type="scatter",
        x="rating",
        y="revenue",
        color="genre"
    )
    
    fig = build_figure(sample_df, proposal)
    assert isinstance(fig, go.Figure)


def test_build_figure_histogram(sample_df):
    """Test building a histogram."""
    proposal = Proposal(
        id=1,
        title="Rating Distribution",
        chart_type="hist",
        x="rating"
    )
    
    fig = build_figure(sample_df, proposal)
    assert isinstance(fig, go.Figure)


def test_build_figure_line(sample_df):
    """Test building a line chart."""
    proposal = Proposal(
        id=1,
        title="Rating Over Time",
        chart_type="line",
        x="year",
        y="rating",
        aggregation="mean"
    )
    
    fig = build_figure(sample_df, proposal)
    assert isinstance(fig, go.Figure)


def test_build_figure_box(sample_df):
    """Test building a box plot."""
    proposal = Proposal(
        id=1,
        title="Rating Distribution by Genre",
        chart_type="box",
        x="genre",
        y="rating"
    )
    
    fig = build_figure(sample_df, proposal)
    assert isinstance(fig, go.Figure)


def test_build_figure_with_custom_labels(sample_df):
    """Test building figure with custom axis labels."""
    proposal = Proposal(
        id=1,
        title="Test",
        chart_type="bar",
        x="genre",
        y="rating",
        aggregation="mean",
        formatting=FormattingSpec(
            x_label="Movie Genre",
            y_label="Average Rating Score"
        )
    )
    
    fig = build_figure(sample_df, proposal)
    assert isinstance(fig, go.Figure)
    # Labels are applied through plotly express
