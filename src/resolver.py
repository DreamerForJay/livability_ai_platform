from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class AddressMatch:
    query: str
    region_name: str
    confidence: str
    matched_by: str


ADDRESS_ALIASES = {
    "逢甲夜市": "台中市西屯區",
    "台中國家歌劇院": "台中市西屯區",
    "台中榮總": "台中市西屯區",
    "秋紅谷": "台中市西屯區",
    "中國醫藥大學": "台中市北區",
    "一中街": "台中市北區",
    "台中公園": "台中市中區",
    "台中火車站": "台中市東區",
    "大慶車站": "台中市南區",
    "文心森林公園": "台中市南屯區",
    "北屯好市多": "台中市北屯區",
    "草悟道": "台中市西區",
    "勤美": "台中市西區",
}


def resolve_address(query: str, df: pd.DataFrame) -> AddressMatch | None:
    cleaned = query.strip()
    if not cleaned:
        return None

    region_names = df["region_name"].tolist()

    for region_name in region_names:
        district = region_name.replace("台中市", "")
        if region_name in cleaned or district in cleaned:
            return AddressMatch(cleaned, region_name, "高", "行政區關鍵字")

    for alias, region_name in ADDRESS_ALIASES.items():
        if alias in cleaned:
            return AddressMatch(cleaned, region_name, "中", f"地標別名：{alias}")

    return None


def suggested_queries() -> list[str]:
    return [
        "逢甲夜市",
        "草悟道",
        "台中火車站",
        "文心森林公園",
        "台中市西屯區",
    ]
