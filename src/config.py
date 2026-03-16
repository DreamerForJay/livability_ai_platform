import os
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


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


GEOCODING_PROVIDER = get_env("GEOCODING_PROVIDER", "local")
GEOCODING_USER_AGENT = get_env(
    "GEOCODING_USER_AGENT",
    "livability-ai-platform/1.0 (contact: your-email@example.com)",
)
API_DOCS_ENABLED = get_bool_env("API_DOCS_ENABLED", True)
