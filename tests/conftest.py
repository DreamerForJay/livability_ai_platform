import pandas as pd
import pytest


@pytest.fixture
def sample_regions():
    return pd.DataFrame(
        [
            {
                "region_id": "A",
                "region_name": "A區",
                "air_quality_score": 90,
                "facility_score": 90,
                "transport_score": 90,
                "public_service_score": 90,
                "risk_score": 10,
            },
            {
                "region_id": "B",
                "region_name": "B區",
                "air_quality_score": 70,
                "facility_score": 70,
                "transport_score": 70,
                "public_service_score": 70,
                "risk_score": 50,
            },
        ]
    )
