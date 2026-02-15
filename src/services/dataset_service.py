from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Optional, Union
import logging

from src.config import settings

log = logging.getLogger(__name__)


@dataclass
class DatasetInfo:
    df: pd.DataFrame
    schema_summary: str
    sample_data: str
    name: str = "dataset"


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load CSV file into DataFrame."""
    df = pd.read_csv(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def load_from_huggingface(dataset_name: str, split: str = "train", max_rows: int = None) -> pd.DataFrame:
    """
    Load dataset from HuggingFace datasets library.
    
    Args:
        dataset_name: Name of the dataset (e.g., "maharshipandya/spotify-tracks-dataset")
        split: Dataset split to load
        max_rows: Maximum number of rows to load
    
    Returns:
        DataFrame
    """
    try:
        from datasets import load_dataset
        
        log.info(f"Loading HuggingFace dataset: {dataset_name}")
        ds = load_dataset(dataset_name, split=split)
        
        # Convert to pandas
        df = ds.to_pandas()
        
        # Limit rows if specified
        if max_rows and len(df) > max_rows:
            df = df.head(max_rows)
            log.info(f"Limited dataset to {max_rows} rows")
        
        log.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except ImportError:
        raise RuntimeError("datasets library not installed. Run: pip install datasets")
    except Exception as e:
        raise RuntimeError(f"Failed to load HuggingFace dataset: {e}")


def build_schema_summary(df: pd.DataFrame) -> str:
    """
    Build a comprehensive schema summary.
    """
    cols = list(df.columns)[: settings.max_schema_cols]
    lines = []
    
    for c in cols:
        s = df[c].dropna()
        dtype = str(df[c].dtype)
        n_unique = df[c].nunique()
        
        # Get example value
        example = ""
        if len(s) > 0:
            example = str(s.iloc[0])[: settings.max_example_len]
        
        # Add cardinality info
        cardinality = f"({n_unique} unique)" if n_unique < 100 else f"({n_unique} unique values)"
        
        lines.append(f"- {c}: {dtype} {cardinality} | Example: {example}")
    
    if len(df.columns) > settings.max_schema_cols:
        lines.append(f"... (+{len(df.columns) - settings.max_schema_cols} more columns)")
    
    return "\n".join(lines)


def get_sample_data(df: pd.DataFrame, n_rows: int = 5) -> str:
    """
    Get sample data as formatted string.
    """
    sample = df.head(n_rows)
    return sample.to_string(max_cols=20, max_colwidth=50)


def prepare_dataset(
    source: Union[str, any],
    source_type: str = "csv",
    dataset_name: Optional[str] = None
) -> DatasetInfo:
    """
    Prepare dataset from various sources.
    
    Args:
        source: File upload, dataset name, or DataFrame
        source_type: Type of source ("csv", "huggingface", "dataframe")
        dataset_name: Optional name for the dataset
    
    Returns:
        DatasetInfo object
    """
    if source_type == "csv":
        df = load_csv(source)
        name = dataset_name or getattr(source, 'name', 'dataset')
    elif source_type == "huggingface":
        df = load_from_huggingface(source, max_rows=settings.max_rows_analysis)
        name = dataset_name or source.split('/')[-1]
    elif source_type == "dataframe":
        df = source
        name = dataset_name or "dataset"
    else:
        raise ValueError(f"Unknown source_type: {source_type}")
    
    schema = build_schema_summary(df)
    sample = get_sample_data(df)
    
    return DatasetInfo(
        df=df,
        schema_summary=schema,
        sample_data=sample,
        name=name
    )
