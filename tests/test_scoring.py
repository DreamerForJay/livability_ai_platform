from src.scoring import calculate_livability_score, normalize_weights


def test_normalize_weights_returns_unit_sum():
    weights = normalize_weights({"air_quality_score": 1, "facility_score": 1, "transport_score": 1, "public_service_score": 1, "risk_score": 1})
    assert round(sum(weights.values()), 6) == 1.0


def test_calculate_livability_score_uses_reverse_risk(sample_regions):
    scored = calculate_livability_score(sample_regions)
    assert "livability_score" in scored.columns
    assert scored.iloc[0]["region_name"] == "A區"
