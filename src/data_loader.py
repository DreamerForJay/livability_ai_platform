import pandas as pd

from src.config import DATA_PATH


def load_regions() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    numeric_columns = [
        "air_quality_score",
        "facility_score",
        "transport_score",
        "public_service_score",
        "risk_score",
        "latitude",
        "longitude",
        "population",
    ]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    return df
