from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "regions_demo.csv"

DEFAULT_WEIGHTS = {
    "air_quality_score": 0.25,
    "facility_score": 0.25,
    "transport_score": 0.20,
    "public_service_score": 0.15,
    "risk_score": 0.15,
}
