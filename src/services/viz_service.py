from __future__ import annotations

import pandas as pd
import plotly.express as px

from src.models.viz_spec import Proposal


def apply_filters(df: pd.DataFrame, spec: Proposal) -> pd.DataFrame:
    data = df.copy()
    for f in spec.filters:
        if f.col not in data.columns:
            continue
        if f.op == "==":
            data = data[data[f.col] == f.value]
        elif f.op == "!=":
            data = data[data[f.col] != f.value]
        elif f.op == ">":
            data = data[data[f.col] > f.value]
        elif f.op == "<":
            data = data[data[f.col] < f.value]
        elif f.op == "in":
            vals = f.value if isinstance(f.value, list) else [f.value]
            data = data[data[f.col].isin(vals)]
    return data


def aggregate_if_needed(df: pd.DataFrame, spec: Proposal) -> pd.DataFrame:
    data = df.copy()
    if spec.chart_type in ("bar", "line") and spec.y and spec.aggregation != "none":
        if spec.x not in data.columns or spec.y not in data.columns:
            return data

        if spec.aggregation == "mean":
            data = data.groupby(spec.x, as_index=False)[spec.y].mean()
        elif spec.aggregation == "sum":
            data = data.groupby(spec.x, as_index=False)[spec.y].sum()
        elif spec.aggregation == "median":
            data = data.groupby(spec.x, as_index=False)[spec.y].median()
        elif spec.aggregation == "count":
            data = data.groupby(spec.x, as_index=False)[spec.y].count()

        if spec.formatting.sort in ("asc", "desc"):
            data = data.sort_values(spec.y, ascending=(spec.formatting.sort == "asc"))

        if spec.formatting.top_k and len(data) > spec.formatting.top_k:
            data = data.head(spec.formatting.top_k)

    return data


def build_figure(df: pd.DataFrame, spec: Proposal):
    data = apply_filters(df, spec)
    data = aggregate_if_needed(data, spec)

    x = spec.x
    y = spec.y
    color = spec.color

    labels = {}
    if x:
        labels[x] = spec.formatting.x_label or x
    if y:
        labels[y] = spec.formatting.y_label or y

    if spec.chart_type == "bar":
        fig = px.bar(data, x=x, y=y, color=color, title=spec.title, labels=labels)
    elif spec.chart_type == "line":
        fig = px.line(data, x=x, y=y, color=color, title=spec.title, labels=labels)
    elif spec.chart_type == "scatter":
        fig = px.scatter(data, x=x, y=y, color=color, title=spec.title, labels=labels)
    elif spec.chart_type == "box":
        fig = px.box(data, x=x, y=y, color=color, title=spec.title, labels=labels)
    elif spec.chart_type == "hist":
        fig = px.histogram(data, x=x, color=color, title=spec.title, labels=labels)
    elif spec.chart_type == "heatmap":
        if not x or not y:
            raise ValueError("Heatmap nécessite x et y.")
        pivot = data.pivot_table(index=y, columns=x, aggfunc="size", fill_value=0)
        fig = px.imshow(pivot, title=spec.title)
    else:
        raise ValueError(f"chart_type inconnu: {spec.chart_type}")

    fig.update_layout(margin=dict(l=30, r=30, t=60, b=30))
    return fig
