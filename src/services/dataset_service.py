from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Optional

from src.config import settings


@dataclass
class DatasetInfo:
    df: pd.DataFrame
    schema_summary: str


def load_csv(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def build_schema_summary(df: pd.DataFrame) -> str:
    cols = list(df.columns)[: settings.max_schema_cols]
    lines = []
    for c in cols:
        s = df[c].dropna()
        example = ""
        if len(s) > 0:
            example = str(s.iloc[0])[: settings.max_example_len]
        lines.append(f"- {c}:{df[c].dtype}:{example}")

    if len(df.columns) > settings.max_schema_cols:
        lines.append(f"... (+{len(df.columns) - settings.max_schema_cols} autres colonnes)")
    return "\n".join(lines)


def prepare_dataset(uploaded_file) -> DatasetInfo:
    df = load_csv(uploaded_file)
    schema = build_schema_summary(df)
    return DatasetInfo(df=df, schema_summary=schema)
