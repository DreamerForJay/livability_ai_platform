from __future__ import annotations

import pandas as pd

from src.config import DEFAULT_WEIGHTS


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {key: value / total for key, value in weights.items()}


def calculate_livability_score(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    selected = normalize_weights(weights or DEFAULT_WEIGHTS.copy())
    scored = df.copy()
    scored["livability_score"] = (
        scored["air_quality_score"] * selected["air_quality_score"]
        + scored["facility_score"] * selected["facility_score"]
        + scored["transport_score"] * selected["transport_score"]
        + scored["public_service_score"] * selected["public_service_score"]
        + (100 - scored["risk_score"]) * selected["risk_score"]
    ).round(2)
    return scored.sort_values("livability_score", ascending=False).reset_index(drop=True)


def build_breakdown(row: pd.Series, weights: dict[str, float]) -> dict[str, float]:
    selected = normalize_weights(weights)
    return {
        "空氣品質": round(row["air_quality_score"] * selected["air_quality_score"], 2),
        "生活機能": round(row["facility_score"] * selected["facility_score"], 2),
        "交通便利": round(row["transport_score"] * selected["transport_score"], 2),
        "公共服務": round(row["public_service_score"] * selected["public_service_score"], 2),
        "風險反向": round((100 - row["risk_score"]) * selected["risk_score"], 2),
    }
