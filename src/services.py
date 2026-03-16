from __future__ import annotations

import pandas as pd

from src.config import DEFAULT_WEIGHTS
from src.data_loader import load_regions
from src.resolver import resolve_address
from src.scoring import calculate_livability_score, normalize_weights
from src.summary import generate_region_summary, persona_recommendations, score_badges


def load_ranked_regions(weights: dict[str, float] | None = None) -> pd.DataFrame:
    selected = normalize_weights(weights or DEFAULT_WEIGHTS.copy())
    return calculate_livability_score(load_regions(), selected)


def serialize_region(row: pd.Series) -> dict[str, object]:
    population = int(float(row["population"])) if pd.notna(row["population"]) else 0
    return {
        "region_id": str(row["region_id"]),
        "region_name": str(row["region_name"]),
        "air_quality_score": float(row["air_quality_score"]),
        "facility_score": float(row["facility_score"]),
        "transport_score": float(row["transport_score"]),
        "public_service_score": float(row["public_service_score"]),
        "risk_score": float(row["risk_score"]),
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "population": population,
        "livability_score": float(row["livability_score"]),
        "summary_text": generate_region_summary(row),
        "badges": score_badges(row),
        "recommendations": persona_recommendations(row),
    }


def list_regions(weights: dict[str, float] | None = None) -> list[dict[str, object]]:
    ranked = load_ranked_regions(weights)
    return [serialize_region(row) for _, row in ranked.iterrows()]


def get_region(identifier: str, weights: dict[str, float] | None = None) -> dict[str, object] | None:
    ranked = load_ranked_regions(weights)
    matched = ranked[(ranked["region_id"] == identifier) | (ranked["region_name"] == identifier)]
    if matched.empty:
        return None
    return serialize_region(matched.iloc[0])


def resolve_query(query: str, weights: dict[str, float] | None = None) -> dict[str, object] | None:
    ranked = load_ranked_regions(weights)
    match = resolve_address(query, ranked)
    if not match:
        return None
    matched = ranked[ranked["region_name"] == match.region_name]
    if matched.empty:
        return None
    return {
        "query": match.query,
        "region_name": match.region_name,
        "confidence": match.confidence,
        "matched_by": match.matched_by,
        "region": serialize_region(matched.iloc[0]),
    }


def metadata() -> dict[str, object]:
    return {
        "city": "台中市",
        "data_status": "demo",
        "current_sources": [
            "示範資料集",
            "本地規則式地址/地標對應",
        ],
        "next_sources": [
            "內政部 TGOS 或其他 geocoding 服務",
            "環境部空氣品質資料",
            "政府開放資料平台 POI / 公共設施資料",
            "災害風險或潛勢資料",
        ],
    }
