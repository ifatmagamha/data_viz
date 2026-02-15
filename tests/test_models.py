"""
Unit tests for models (viz_spec).
"""
import pytest
from pydantic import ValidationError
from src.models.viz_spec import Proposal, ProposalsResponse, FilterSpec, FormattingSpec


def test_proposal_creation_minimal():
    """Test creating a minimal valid proposal."""
    proposal = Proposal(
        id=1,
        title="Test Chart",
        chart_type="bar",
        x="column1",
        reasoning="Test reasoning"
    )
    
    assert proposal.id == 1
    assert proposal.title == "Test Chart"
    assert proposal.chart_type == "bar"
    assert proposal.x == "column1"
    assert proposal.y is None
    assert proposal.color is None
    assert proposal.aggregation == "none"
    assert len(proposal.filters) == 0


def test_proposal_creation_full(sample_proposal_dict):
    """Test creating a complete proposal."""
    proposal = Proposal(**sample_proposal_dict)
    
    assert proposal.id == 1
    assert proposal.title == "Average Rating by Genre"
    assert proposal.chart_type == "bar"
    assert proposal.x == "genre"
    assert proposal.y == "rating"
    assert proposal.aggregation == "mean"


def test_proposal_invalid_chart_type():
    """Test that invalid chart types are rejected."""
    with pytest.raises(ValidationError):
        Proposal(
            id=1,
            title="Test",
            chart_type="invalid_type",  # Not in allowed types
            x="col1",
            reasoning="Test"
        )


def test_proposal_invalid_aggregation():
    """Test that invalid aggregation types are rejected."""
    with pytest.raises(ValidationError):
        Proposal(
            id=1,
            title="Test",
            chart_type="bar",
            x="col1",
            aggregation="invalid_agg",  # Not in allowed types
            reasoning="Test"
        )


def test_filter_spec_equality():
    """Test creating a filter with equality operator."""
    filter_spec = FilterSpec(col="genre", op="==", value="Action")
    
    assert filter_spec.col == "genre"
    assert filter_spec.op == "=="
    assert filter_spec.value == "Action"


def test_filter_spec_in_operator():
    """Test creating a filter with 'in' operator."""
    filter_spec = FilterSpec(col="genre", op="in", value=["Action", "Comedy"])
    
    assert filter_spec.col == "genre"
    assert filter_spec.op == "in"
    assert isinstance(filter_spec.value, list)
    assert len(filter_spec.value) == 2


def test_filter_spec_invalid_operator():
    """Test that invalid operators are rejected."""
    with pytest.raises(ValidationError):
        FilterSpec(col="genre", op="invalid", value="Action")


def test_formatting_spec_defaults():
    """Test FormattingSpec default values."""
    formatting = FormattingSpec()
    
    assert formatting.x_label is None
    assert formatting.y_label is None
    assert formatting.sort is None
    assert formatting.top_k == 20


def test_formatting_spec_custom():
    """Test FormattingSpec with custom values."""
    formatting = FormattingSpec(
        x_label="Custom X",
        y_label="Custom Y",
        sort="desc",
        top_k=10
    )
    
    assert formatting.x_label == "Custom X"
    assert formatting.y_label == "Custom Y"
    assert formatting.sort == "desc"
    assert formatting.top_k == 10


def test_formatting_spec_top_k_validation():
    """Test that top_k is validated."""
    # Should accept valid values
    formatting = FormattingSpec(top_k=50)
    assert formatting.top_k == 50
    
    # Should reject values outside range
    with pytest.raises(ValidationError):
        FormattingSpec(top_k=0)  # Below minimum
    
    with pytest.raises(ValidationError):
        FormattingSpec(top_k=300)  # Above maximum


def test_proposals_response(sample_proposals_response):
    """Test ProposalsResponse creation."""
    response = ProposalsResponse(**sample_proposals_response)
    
    assert len(response.proposals) == 3
    assert all(isinstance(p, Proposal) for p in response.proposals)
    assert response.proposals[0].id == 1
    assert response.proposals[1].id == 2
    assert response.proposals[2].id == 3


def test_proposals_response_empty():
    """Test ProposalsResponse with empty list."""
    response = ProposalsResponse(proposals=[])
    assert len(response.proposals) == 0


def test_proposal_with_filters():
    """Test proposal with multiple filters."""
    proposal = Proposal(
        id=1,
        title="Filtered Chart",
        chart_type="bar",
        x="col1",
        y="col2",
        filters=[
            FilterSpec(col="genre", op="==", value="Action"),
            FilterSpec(col="rating", op=">", value=7.0)
        ],
        reasoning="Test with filters"
    )
    
    assert len(proposal.filters) == 2
    assert proposal.filters[0].col == "genre"
    assert proposal.filters[1].col == "rating"
