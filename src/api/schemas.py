from __future__ import annotations

from pydantic import BaseModel, Field


class WeightsPayload(BaseModel):
    air_quality_score: float = Field(default=0.25, ge=0.0)
    facility_score: float = Field(default=0.25, ge=0.0)
    transport_score: float = Field(default=0.20, ge=0.0)
    public_service_score: float = Field(default=0.15, ge=0.0)
    risk_score: float = Field(default=0.15, ge=0.0)


class AskPayload(BaseModel):
    question: str
    weights: WeightsPayload | None = None


class ResolvePayload(BaseModel):
    query: str
    weights: WeightsPayload | None = None


class RegionResponse(BaseModel):
    region_id: str
    region_name: str
    air_quality_score: float
    facility_score: float
    transport_score: float
    public_service_score: float
    risk_score: float
    latitude: float
    longitude: float
    population: int
    livability_score: float
    summary_text: str
    badges: list[str]
    recommendations: list[str]


class ResolveResponse(BaseModel):
    query: str
    region_name: str
    confidence: str
    matched_by: str
    region: RegionResponse


class RankingResponse(BaseModel):
    items: list[RegionResponse]
    weights: dict[str, float]


class AskResponse(BaseModel):
    question: str
    answer: str
    recommended_region: str | None = None


class DemoStep(BaseModel):
    title: str
    instruction: str


class DemoFlowResponse(BaseModel):
    steps: list[DemoStep]
