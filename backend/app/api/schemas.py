from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class DisasterAnalyzeRequest(BaseModel):
    area: str = Field(..., min_length=1, max_length=200)


class OfflineRecordRequest(BaseModel):
    record_type: str = Field(..., min_length=1, max_length=100)
    payload: dict


class ReportRequest(BaseModel):
    area: str = Field(..., min_length=1, max_length=200)


class GraphBuildResponse(BaseModel):
    backend: str
    node_count: int
    edge_count: int


class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    graph_backend: str
    vector_backend: str
    version: str
