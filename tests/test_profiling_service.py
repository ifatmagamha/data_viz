"""
Unit tests for profiling_service module.
"""
import pytest
import pandas as pd
from src.services.profiling_service import quick_profile, profile_to_text, Profile


def test_quick_profile_basic(sample_df):
    """Test basic profiling functionality."""
    profile = quick_profile(sample_df)
    
    assert isinstance(profile, Profile)
    assert isinstance(profile.column_profile, dict)
    assert 'genre' in profile.column_profile
    assert 'rating' in profile.column_profile


def test_quick_profile_column_info(sample_df):
    """Test that profile contains correct column information."""
    profile = quick_profile(sample_df)
    
    # Check genre column (categorical)
    genre_info = profile.column_profile['genre']
    assert 'dtype' in genre_info
    assert 'missing_pct' in genre_info
    assert 'n_unique' in genre_info
    assert genre_info['n_unique'] == 3  # Action, Comedy, Drama
    
    # Check rating column (numeric)
    rating_info = profile.column_profile['rating']
    assert 'dtype' in rating_info
    assert 'min' in rating_info
    assert 'max' in rating_info
    assert 'mean' in rating_info


def test_quick_profile_missing_values():
    """Test profiling with missing values."""
    df = pd.DataFrame({
        'col1': [1, 2, None, 4, None],
        'col2': ['a', 'b', 'c', 'd', 'e']
    })
    
    profile = quick_profile(df)
    col1_info = profile.column_profile['col1']
    
    assert col1_info['missing_pct'] == 40.0  # 2 out of 5 are missing


def test_quick_profile_max_cols():
    """Test that profiling respects max_cols parameter."""
    # Create DataFrame with many columns
    df = pd.DataFrame({f'col_{i}': [1, 2, 3] for i in range(100)})
    
    profile = quick_profile(df, max_cols=10)
    
    # Should only profile first 10 columns
    assert len(profile.column_profile) == 10


def test_profile_to_text(sample_df):
    """Test conversion of profile to text format."""
    profile = quick_profile(sample_df)
    text = profile_to_text(profile)
    
    assert isinstance(text, str)
    assert 'genre' in text
    assert 'rating' in text
    assert 'dtype' in text
    assert 'missing%' in text
    assert 'unique' in text


def test_profile_to_text_numeric_columns(sample_df):
    """Test that numeric columns include min/max/mean in text."""
    profile = quick_profile(sample_df)
    text = profile_to_text(profile)
    
    # Numeric columns should have min, max, mean
    assert 'min=' in text
    assert 'max=' in text
    assert 'mean=' in text


def test_profile_to_text_empty_dataframe():
    """Test profiling an empty DataFrame."""
    df = pd.DataFrame()
    profile = quick_profile(df)
    text = profile_to_text(profile)
    
    assert isinstance(text, str)
    assert text == ""  # No columns to profile


def test_quick_profile_all_numeric():
    """Test profiling DataFrame with all numeric columns."""
    df = pd.DataFrame({
        'int_col': [1, 2, 3, 4, 5],
        'float_col': [1.1, 2.2, 3.3, 4.4, 5.5]
    })
    
    profile = quick_profile(df)
    
    for col in ['int_col', 'float_col']:
        info = profile.column_profile[col]
        assert 'min' in info
        assert 'max' in info
        assert 'mean' in info
        assert info['min'] <= info['max']
