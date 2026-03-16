from __future__ import annotations

import pandas as pd


def classify_level(score: float) -> str:
    if score >= 85:
        return "非常適合"
    if score >= 78:
        return "適合"
    if score >= 70:
        return "可考慮"
    return "需審慎評估"


def generate_region_summary(row: pd.Series) -> str:
    level = classify_level(float(row["livability_score"]))
    strengths = []
    warnings = []

    if row["facility_score"] >= 85:
        strengths.append("生活機能完整")
    if row["transport_score"] >= 85:
        strengths.append("交通可近性高")
    if row["public_service_score"] >= 85:
        strengths.append("公共服務資源充足")
    if row["air_quality_score"] >= 80:
        strengths.append("環境品質相對穩定")

    if row["risk_score"] >= 40:
        warnings.append("風險暴露偏高")
    if row["air_quality_score"] < 72:
        warnings.append("空氣品質需持續觀察")
    if row["facility_score"] < 75:
        warnings.append("生活機能相對有限")

    strength_text = "、".join(strengths[:3]) if strengths else "整體表現均衡"
    warning_text = "、".join(warnings[:2]) if warnings else "目前沒有明顯短板"

    return (
        f"{row['region_name']} 的綜合宜居分數為 {row['livability_score']}，屬於「{level}」等級。"
        f"主要優勢為 {strength_text}；需注意 {warning_text}。"
        "若目標族群為學生租屋、一般家庭或中小型店面設點，這個區域具備不錯的展示價值。"
    )


def answer_question(question: str, ranked_df: pd.DataFrame) -> str:
    top = ranked_df.iloc[0]
    bottom = ranked_df.iloc[-1]
    question = question.strip()

    if not question:
        return "請輸入問題，例如：哪裡適合學生租屋？"

    if "最佳" in question or "最適合" in question or "推薦" in question:
        return (
            f"目前最推薦的區域是 {top['region_name']}，綜合分數 {top['livability_score']}。"
            f"它在生活機能、交通與公共服務表現較完整，適合拿來做主要示範案例。"
        )

    if "風險" in question or "安全" in question:
        safest = ranked_df.sort_values("risk_score").iloc[0]
        return (
            f"若優先考慮低風險，{safest['region_name']} 目前最有優勢，風險分數為 {safest['risk_score']}。"
            "建議搭配空氣品質與交通條件一起判讀，不要只看單一指標。"
        )

    return (
        f"依目前資料，整體表現最好的是 {top['region_name']}，最低的是 {bottom['region_name']}。"
        "如果你要 Demo，建議比較前兩名與後兩名，最容易把差異說清楚。"
    )
