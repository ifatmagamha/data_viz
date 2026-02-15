from __future__ import annotations

import pandas as pd


def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def is_datetime(series: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(series)


def is_categorical(series: pd.Series, max_unique_ratio: float = 0.2) -> bool:
    # Heuristic: object/category or few uniques relative to length
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        return True
    n = len(series.dropna())
    if n == 0:
        return False
    unique = series.dropna().nunique()
    return (unique / n) <= max_unique_ratio
