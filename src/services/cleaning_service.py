"""
Data cleaning service for automatic dataset preprocessing.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

from src.config import settings

log = logging.getLogger(__name__)


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Automatically detect column types beyond pandas dtypes.
    
    Returns:
        Dict mapping column names to semantic types:
        - 'numeric': Numeric data
        - 'categorical': Categorical data
        - 'datetime': Date/time data
        - 'text': Free text
        - 'boolean': Boolean data
    """
    column_types = {}
    
    for col in df.columns:
        series = df[col].dropna()
        
        if len(series) == 0:
            column_types[col] = 'unknown'
            continue
        
        # Check for boolean
        if series.nunique() == 2 and set(series.unique()).issubset({0, 1, True, False, 'Yes', 'No', 'yes', 'no'}):
            column_types[col] = 'boolean'
        # Check for datetime
        elif pd.api.types.is_datetime64_any_dtype(series):
            column_types[col] = 'datetime'
        # Check for numeric
        elif pd.api.types.is_numeric_dtype(series):
            column_types[col] = 'numeric'
        # Check for categorical (low cardinality)
        elif series.nunique() / len(series) < 0.05 or series.nunique() < 20:
            column_types[col] = 'categorical'
        # Otherwise text
        else:
            column_types[col] = 'text'
    
    return column_types


def clean_missing_values(df: pd.DataFrame, threshold: float = None) -> Tuple[pd.DataFrame, List[str]]:
    """
    Clean missing values from dataset.
    
    Args:
        df: Input dataframe
        threshold: Drop columns with more than this fraction of missing values
    
    Returns:
        Cleaned dataframe and list of dropped columns
    """
    if threshold is None:
        threshold = settings.missing_threshold
    
    dropped_cols = []
    df_clean = df.copy()
    
    # Drop columns with too many missing values
    for col in df.columns:
        missing_pct = df[col].isna().sum() / len(df)
        if missing_pct > threshold:
            df_clean = df_clean.drop(columns=[col])
            dropped_cols.append(col)
            log.info(f"Dropped column '{col}' ({missing_pct:.1%} missing)")
    
    # Fill remaining missing values
    for col in df_clean.columns:
        if df_clean[col].isna().any():
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                # Fill numeric with median
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            else:
                # Fill categorical/text with mode or 'Unknown'
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col] = df_clean[col].fillna(mode_val[0])
                else:
                    df_clean[col] = df_clean[col].fillna('Unknown')
    
    return df_clean, dropped_cols


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Remove duplicate rows.
    
    Returns:
        Cleaned dataframe and number of duplicates removed
    """
    initial_len = len(df)
    df_clean = df.drop_duplicates()
    n_duplicates = initial_len - len(df_clean)
    
    if n_duplicates > 0:
        log.info(f"Removed {n_duplicates} duplicate rows")
    
    return df_clean, n_duplicates


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names: lowercase, replace spaces with underscores, remove special chars.
    """
    df_clean = df.copy()
    
    new_columns = {}
    for col in df.columns:
        # Convert to string, lowercase, replace spaces
        new_name = str(col).lower().strip()
        new_name = new_name.replace(' ', '_')
        new_name = new_name.replace('-', '_')
        # Remove special characters except underscore
        new_name = ''.join(c for c in new_name if c.isalnum() or c == '_')
        new_columns[col] = new_name
    
    df_clean = df_clean.rename(columns=new_columns)
    return df_clean


def auto_clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Automatically clean dataset with all cleaning operations.
    
    Returns:
        Cleaned dataframe and cleaning report
    """
    report = {
        'original_shape': df.shape,
        'dropped_columns': [],
        'duplicates_removed': 0,
        'columns_renamed': False,
        'final_shape': None
    }
    
    # Clean column names
    df_clean = clean_column_names(df)
    report['columns_renamed'] = True
    
    # Remove duplicates
    df_clean, n_duplicates = remove_duplicates(df_clean)
    report['duplicates_removed'] = n_duplicates
    
    # Clean missing values
    df_clean, dropped_cols = clean_missing_values(df_clean)
    report['dropped_columns'] = dropped_cols
    
    report['final_shape'] = df_clean.shape
    
    log.info(f"Cleaning complete: {report['original_shape']} → {report['final_shape']}")
    
    return df_clean, report


def get_data_quality_report(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate a data quality report.
    """
    report = {
        'n_rows': len(df),
        'n_columns': len(df.columns),
        'missing_values': {},
        'duplicates': df.duplicated().sum(),
        'column_types': detect_column_types(df),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }
    
    for col in df.columns:
        missing_pct = df[col].isna().sum() / len(df) * 100
        if missing_pct > 0:
            report['missing_values'][col] = f"{missing_pct:.1f}%"
    
    return report
