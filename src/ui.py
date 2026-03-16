from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import DEFAULT_WEIGHTS
from src.data_loader import load_regions
from src.scoring import build_breakdown, calculate_livability_score
from src.summary import answer_question, generate_region_summary


def render_sidebar() -> dict[str, float]:
    st.sidebar.header("權重設定")
    air = st.sidebar.slider("空氣品質", 0.0, 1.0, float(DEFAULT_WEIGHTS["air_quality_score"]), 0.05)
    facility = st.sidebar.slider("生活機能", 0.0, 1.0, float(DEFAULT_WEIGHTS["facility_score"]), 0.05)
    transport = st.sidebar.slider("交通便利", 0.0, 1.0, float(DEFAULT_WEIGHTS["transport_score"]), 0.05)
    public_service = st.sidebar.slider(
        "公共服務",
        0.0,
        1.0,
        float(DEFAULT_WEIGHTS["public_service_score"]),
        0.05,
    )
    risk = st.sidebar.slider("風險反向", 0.0, 1.0, float(DEFAULT_WEIGHTS["risk_score"]), 0.05)

    return {
        "air_quality_score": air,
        "facility_score": facility,
        "transport_score": transport,
        "public_service_score": public_service,
        "risk_score": risk,
    }


def render_map(df: pd.DataFrame) -> None:
    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        color="livability_score",
        size="population",
        hover_name="region_name",
        hover_data={
            "livability_score": True,
            "air_quality_score": True,
            "facility_score": True,
            "transport_score": True,
            "public_service_score": True,
            "risk_score": True,
            "latitude": False,
            "longitude": False,
            "population": True,
        },
        color_continuous_scale="YlGnBu",
        zoom=10,
        height=500,
    )
    fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)


def render_breakdown(selected_row: pd.Series, weights: dict[str, float]) -> None:
    breakdown = build_breakdown(selected_row, weights)
    bar = go.Figure(
        data=[
            go.Bar(
                x=list(breakdown.keys()),
                y=list(breakdown.values()),
                marker_color=["#2e8b57", "#4f9d69", "#78b27b", "#a3c18a", "#588157"],
            )
        ]
    )
    bar.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="加權貢獻")
    st.plotly_chart(bar, use_container_width=True)


def render_compare(df: pd.DataFrame) -> None:
    options = df["region_name"].tolist()
    selected = st.multiselect("選擇 2 至 3 個區域比較", options=options, default=options[:2], max_selections=3)
    compare_df = df[df["region_name"].isin(selected)].copy()
    if compare_df.empty:
        st.info("請至少選擇一個區域。")
        return

    melted = compare_df.melt(
        id_vars=["region_name"],
        value_vars=[
            "air_quality_score",
            "facility_score",
            "transport_score",
            "public_service_score",
            "risk_score",
            "livability_score",
        ],
        var_name="metric",
        value_name="score",
    )
    fig = px.line_polar(melted, r="score", theta="metric", color="region_name", line_close=True)
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def run_app() -> None:
    st.set_page_config(page_title="Taiwan Livability AI Platform", layout="wide")
    st.title("臺灣宜居地智慧分析平台")
    st.caption("基於環境資料與 AI 分析的城市宜居度評估系統")

    weights = render_sidebar()
    raw_df = load_regions()
    ranked_df = calculate_livability_score(raw_df, weights)

    top_region = ranked_df.iloc[0]
    avg_score = round(float(ranked_df["livability_score"].mean()), 2)

    a, b, c = st.columns(3)
    a.metric("最佳區域", top_region["region_name"])
    b.metric("最高分", top_region["livability_score"])
    c.metric("平均分數", avg_score)

    st.subheader("區域地圖")
    render_map(ranked_df)

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("區域排行")
        display_df = ranked_df[
            [
                "region_name",
                "livability_score",
                "air_quality_score",
                "facility_score",
                "transport_score",
                "public_service_score",
                "risk_score",
            ]
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("AI 問答")
        st.caption("範例：哪裡最適合學生租屋？ 哪區風險最低？")
        question = st.text_input("輸入問題", value="哪裡最適合學生租屋？")
        st.write(answer_question(question, ranked_df))

    st.subheader("單區分析")
    region_name = st.selectbox("選擇區域", ranked_df["region_name"].tolist())
    selected_row = ranked_df[ranked_df["region_name"] == region_name].iloc[0]

    x, y = st.columns([0.9, 1.1])
    with x:
        st.metric("綜合宜居分數", selected_row["livability_score"])
        st.write(generate_region_summary(selected_row))
    with y:
        render_breakdown(selected_row, weights)

    st.subheader("區域比較")
    render_compare(ranked_df)

    st.subheader("匯出結果")
    st.download_button(
        label="下載目前排序 CSV",
        data=ranked_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="livability_ranking.csv",
        mime="text/csv",
    )
