from __future__ import annotations

import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Profile:
    column_profile: Dict[str, Dict[str, Any]]


def quick_profile(df: pd.DataFrame, max_cols: int = 80) -> Profile:
    """
    Fast stats: dtype, missing rate, unique count, numeric min/max.
    """
    profile: Dict[str, Dict[str, Any]] = {}
    for c in list(df.columns)[:max_cols]:
        s = df[c]
        info: Dict[str, Any] = {
            "dtype": str(s.dtype),
            "missing_pct": float(s.isna().mean() * 100),
            "n_unique": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            s2 = s.dropna()
            if len(s2) > 0:
                info.update(
                    {
                        "min": float(s2.min()),
                        "max": float(s2.max()),
                        "mean": float(s2.mean()),
                    }
                )
        profile[c] = info
    return Profile(column_profile=profile)


def profile_to_text(profile: Profile) -> str:
    """
    Optional: a concise text summary for the LLM.
    """
    lines = []
    for col, info in profile.column_profile.items():
        base = f"- {col} | dtype={info.get('dtype')} | missing%={info.get('missing_pct'):.1f} | unique={info.get('n_unique')}"
        if "min" in info:
            base += f" | min={info['min']:.2f} max={info['max']:.2f} mean={info['mean']:.2f}"
        lines.append(base)
    return "\n".join(lines)
