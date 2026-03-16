import pandas as pd

from src.resolver import resolve_address


def test_resolve_address_matches_district():
    df = pd.DataFrame([{"region_name": "台中市西屯區"}, {"region_name": "台中市北區"}])
    match = resolve_address("台中市西屯區福星路", df)
    assert match is not None
    assert match.region_name == "台中市西屯區"


def test_resolve_address_returns_none_for_unknown():
    df = pd.DataFrame([{"region_name": "台中市西屯區"}])
    match = resolve_address("未知地址", df)
    assert match is None
