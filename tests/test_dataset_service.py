"""
Unit tests for dataset_service module.
"""
import pytest
import pandas as pd
from src.services.dataset_service import load_csv, build_schema_summary, prepare_dataset, DatasetInfo


def test_load_csv(sample_csv_file):
    """Test CSV loading functionality."""
    df = load_csv(sample_csv_file)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6
    assert 'genre' in df.columns
    assert 'rating' in df.columns


def test_load_csv_strips_column_names(tmp_path):
    """Test that column names are stripped of whitespace."""
    # Create CSV with whitespace in column names
    csv_path = tmp_path / "test_whitespace.csv"
    with open(csv_path, 'w') as f:
        f.write(" genre , rating \n")
        f.write("Action,8.5\n")
    
    df = load_csv(csv_path)
    assert 'genre' in df.columns
    assert 'rating' in df.columns
    assert ' genre ' not in df.columns


def test_build_schema_summary(sample_df):
    """Test schema summary generation."""
    schema = build_schema_summary(sample_df)
    
    assert isinstance(schema, str)
    assert 'genre' in schema
    assert 'rating' in schema
    assert 'revenue' in schema
    # Check that dtype and example are included
    assert 'object' in schema or 'int' in schema or 'float' in schema


def test_build_schema_summary_with_max_cols(sample_df):
    """Test schema summary respects max_cols limit."""
    from src.config import settings
    
    # Create a DataFrame with more columns than max_schema_cols
    many_cols_df = pd.DataFrame({f'col_{i}': [1, 2, 3] for i in range(100)})
    schema = build_schema_summary(many_cols_df)
    
    # Should include a message about additional columns
    if len(many_cols_df.columns) > settings.max_schema_cols:
        assert 'autres colonnes' in schema


def test_prepare_dataset(sample_csv_file):
    """Test complete dataset preparation."""
    dataset_info = prepare_dataset(sample_csv_file)
    
    assert isinstance(dataset_info, DatasetInfo)
    assert isinstance(dataset_info.df, pd.DataFrame)
    assert isinstance(dataset_info.schema_summary, str)
    assert len(dataset_info.df) > 0
    assert len(dataset_info.schema_summary) > 0


def test_prepare_dataset_with_missing_values(tmp_path):
    """Test dataset preparation with missing values."""
    # Create CSV with missing values
    csv_path = tmp_path / "test_missing.csv"
    df = pd.DataFrame({
        'col1': [1, 2, None, 4],
        'col2': ['a', None, 'c', 'd']
    })
    df.to_csv(csv_path, index=False)
    
    dataset_info = prepare_dataset(csv_path)
    assert isinstance(dataset_info, DatasetInfo)
    assert dataset_info.df['col1'].isna().sum() == 1
    assert dataset_info.df['col2'].isna().sum() == 1
