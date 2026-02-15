from __future__ import annotations

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

ChartType = Literal["bar", "line", "scatter", "box", "hist", "heatmap"]
AggType = Literal["mean", "sum", "count", "median", "none"]
SortType = Optional[Literal["asc", "desc"]]


class FilterSpec(BaseModel):
    col: str
    op: Literal["==", "!=", ">", "<", "in"]
    value: Union[str, int, float, List[Union[str, int, float]]]


class FormattingSpec(BaseModel):
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    sort: SortType = None
    top_k: int = Field(default=20, ge=1, le=200)


class Proposal(BaseModel):
    id: int
    title: str
    chart_type: ChartType
    x: str
    y: Optional[str] = None
    color: Optional[str] = None
    aggregation: AggType = "none"
    filters: List[FilterSpec] = Field(default_factory=list)
    reasoning: str
    formatting: FormattingSpec = Field(default_factory=FormattingSpec)


class ProposalsResponse(BaseModel):
    proposals: List[Proposal]
