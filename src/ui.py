from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import DEFAULT_WEIGHTS
from src.data_loader import load_regions
from src.resolver import resolve_address, suggested_queries
from src.scoring import build_breakdown, calculate_livability_score
from src.summary import (
    answer_question,
    compare_regions,
    generate_region_summary,
    persona_recommendations,
    score_badges,
)


METRIC_LABELS = {
    "air_quality_score": "空氣品質",
    "facility_score": "生活機能",
    "transport_score": "交通便利",
    "public_service_score": "公共服務",
    "risk_score": "風險暴露",
    "livability_score": "綜合宜居分數",
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(159, 196, 255, 0.25), transparent 32%),
                radial-gradient(circle at bottom right, rgba(183, 231, 198, 0.30), transparent 28%),
                linear-gradient(180deg, #f5f8fc 0%, #f7fbf6 100%);
        }
        .hero {
            padding: 1.6rem 1.8rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #16324f 0%, #2f6690 54%, #3a7d78 100%);
            color: #ffffff;
            box-shadow: 0 20px 40px rgba(19, 39, 58, 0.18);
            margin-bottom: 1.2rem;
        }
        .hero h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.2rem;
            line-height: 1.15;
        }
        .hero p {
            margin: 0;
            font-size: 1rem;
            line-height: 1.65;
            opacity: 0.95;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0 0.1rem 0;
        }
        .pill {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.16);
            font-size: 0.9rem;
        }
        .card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(38, 70, 83, 0.08);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 25px rgba(59, 92, 122, 0.08);
        }
        .section-title {
            margin-top: 0.2rem;
            margin-bottom: 0.6rem;
            font-size: 1.1rem;
            font-weight: 700;
            color: #16324f;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            margin: 0 0.45rem 0.45rem 0;
            border-radius: 999px;
            background: #e9f4ee;
            color: #165b47;
            font-size: 0.88rem;
            font-weight: 600;
        }
        .hint {
            color: #486581;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict[str, float]:
    st.sidebar.header("分析權重設定")
    st.sidebar.caption("你可以切換不同使用情境，模擬不同族群的決策偏好。")
    preset = st.sidebar.selectbox("情境模式", ["均衡模式", "學生租屋", "家庭居住", "商業設點"])

    presets = {
        "均衡模式": DEFAULT_WEIGHTS,
        "學生租屋": {
            "air_quality_score": 0.15,
            "facility_score": 0.30,
            "transport_score": 0.30,
            "public_service_score": 0.10,
            "risk_score": 0.15,
        },
        "家庭居住": {
            "air_quality_score": 0.25,
            "facility_score": 0.20,
            "transport_score": 0.15,
            "public_service_score": 0.20,
            "risk_score": 0.20,
        },
        "商業設點": {
            "air_quality_score": 0.10,
            "facility_score": 0.35,
            "transport_score": 0.30,
            "public_service_score": 0.10,
            "risk_score": 0.15,
        },
    }
    defaults = presets[preset]

    air = st.sidebar.slider("空氣品質", 0.0, 1.0, float(defaults["air_quality_score"]), 0.05)
    facility = st.sidebar.slider("生活機能", 0.0, 1.0, float(defaults["facility_score"]), 0.05)
    transport = st.sidebar.slider("交通便利", 0.0, 1.0, float(defaults["transport_score"]), 0.05)
    public_service = st.sidebar.slider("公共服務", 0.0, 1.0, float(defaults["public_service_score"]), 0.05)
    risk = st.sidebar.slider("風險反向", 0.0, 1.0, float(defaults["risk_score"]), 0.05)

    return {
        "air_quality_score": air,
        "facility_score": facility,
        "transport_score": transport,
        "public_service_score": public_service,
        "risk_score": risk,
    }


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>臺灣宜居地智慧分析平台</h1>
            <p>
                以環境資料、生活機能、交通便利、公共服務與風險指標建立可解釋的城市宜居度評估系統。
                使用者可透過地址、地標、行政區與自然語言查詢，快速得到選址與居住決策建議。
            </p>
            <div class="pill-row">
                <span class="pill">地圖分析</span>
                <span class="pill">地址查詢</span>
                <span class="pill">AI 問答</span>
                <span class="pill">區域比較</span>
                <span class="pill">可解釋評分</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(ranked_df: pd.DataFrame) -> None:
    top_region = ranked_df.iloc[0]
    safest_region = ranked_df.sort_values("risk_score").iloc[0]
    avg_score = round(float(ranked_df["livability_score"].mean()), 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("最佳區域", top_region["region_name"])
    col2.metric("最高分", top_region["livability_score"])
    col3.metric("最低風險區", safest_region["region_name"])
    col4.metric("平均分數", avg_score)


def render_map(df: pd.DataFrame, focus_region: str | None = None) -> None:
    plot_df = df.copy()
    plot_df["marker_size"] = plot_df["population"] / 12000
    plot_df["focus"] = plot_df["region_name"].eq(focus_region) if focus_region else False

    fig = px.scatter_map(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="livability_score",
        size="marker_size",
        hover_name="region_name",
        hover_data={
            "livability_score": True,
            "air_quality_score": True,
            "facility_score": True,
            "transport_score": True,
            "public_service_score": True,
            "risk_score": True,
            "population": True,
            "marker_size": False,
            "latitude": False,
            "longitude": False,
            "focus": False,
        },
        color_continuous_scale="Tealgrn",
        zoom=10,
        height=520,
    )

    if focus_region:
        focus_df = plot_df[plot_df["region_name"] == focus_region]
        fig.add_trace(
            go.Scattermap(
                lat=focus_df["latitude"],
                lon=focus_df["longitude"],
                mode="markers+text",
                text=focus_df["region_name"],
                textposition="top right",
                marker=go.scattermap.Marker(size=22, color="#d1495b"),
                name="查詢位置",
            )
        )

    fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_address_search(ranked_df: pd.DataFrame) -> str | None:
    st.markdown('<div class="section-title">地址 / 地標查詢</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hint">可輸入行政區、地標或常見地址關鍵字，例如：逢甲夜市、草悟道、台中火車站、台中市西屯區。</div>',
        unsafe_allow_html=True,
    )
    query = st.text_input("輸入地址或地標", value="逢甲夜市")
    cols = st.columns([1.2, 0.8])
    with cols[1]:
        st.caption("建議查詢")
        for item in suggested_queries():
            st.write(f"- {item}")

    match = resolve_address(query, ranked_df)
    if not match:
        st.warning("目前無法精準比對該地址，請先輸入台中市行政區或頁面提供的示範地標。")
        return None

    selected_row = ranked_df[ranked_df["region_name"] == match.region_name].iloc[0]
    st.success(
        f"已將「{match.query}」定位到 {match.region_name}，信心等級：{match.confidence}，判定方式：{match.matched_by}。"
    )

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("對應區域", selected_row["region_name"])
        st.metric("綜合宜居分數", selected_row["livability_score"])
        st.write(generate_region_summary(selected_row))
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**適用情境建議**")
        for item in persona_recommendations(selected_row):
            st.write(f"- {item}")
        st.markdown("**判讀標籤**")
        badges = "".join([f'<span class="badge">{badge}</span>' for badge in score_badges(selected_row)])
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    return selected_row["region_name"]


def render_breakdown(selected_row: pd.Series, weights: dict[str, float]) -> None:
    breakdown = build_breakdown(selected_row, weights)
    bar = go.Figure(
        data=[
            go.Bar(
                x=list(breakdown.keys()),
                y=list(breakdown.values()),
                marker_color=["#0b6e4f", "#3a7d44", "#73a580", "#a6c48a", "#2f4858"],
            )
        ]
    )
    bar.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="加權貢獻")
    st.plotly_chart(bar, use_container_width=True)


def render_rankings(ranked_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">區域排行與判讀</div>', unsafe_allow_html=True)
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
    ].rename(columns=METRIC_LABELS)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_ai_panel(ranked_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">AI 決策問答</div>', unsafe_allow_html=True)
    quick_questions = ["哪裡最適合學生租屋？", "哪區風險最低？", "推薦適合家庭居住的區域"]
    selected_quick = st.selectbox("快速情境", quick_questions)
    question = st.text_input("或自行輸入問題", value=selected_quick)
    st.markdown(f'<div class="card">{answer_question(question, ranked_df)}</div>', unsafe_allow_html=True)


def render_region_analysis(ranked_df: pd.DataFrame, weights: dict[str, float], default_region: str | None) -> None:
    st.markdown('<div class="section-title">單區深入分析</div>', unsafe_allow_html=True)
    options = ranked_df["region_name"].tolist()
    default_index = options.index(default_region) if default_region in options else 0
    region_name = st.selectbox("選擇要深入分析的區域", options, index=default_index)
    selected_row = ranked_df[ranked_df["region_name"] == region_name].iloc[0]

    left, right = st.columns([0.95, 1.05])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("綜合宜居分數", selected_row["livability_score"])
        st.write(generate_region_summary(selected_row))
        st.markdown("**適合對象**")
        for item in persona_recommendations(selected_row):
            st.write(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        render_breakdown(selected_row, weights)


def render_compare(ranked_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">多區域比較</div>', unsafe_allow_html=True)
    options = ranked_df["region_name"].tolist()
    selected = st.multiselect("選擇 2 至 3 個區域比較", options=options, default=options[:2], max_selections=3)
    compare_df = ranked_df[ranked_df["region_name"].isin(selected)].copy()
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
    melted["metric"] = melted["metric"].map(METRIC_LABELS)
    fig = px.line_polar(
        melted,
        r="score",
        theta="metric",
        color="region_name",
        line_close=True,
        color_discrete_sequence=["#1d4e89", "#2a9d8f", "#e76f51"],
    )
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<div class="card">{compare_regions(compare_df)}</div>', unsafe_allow_html=True)


def render_export(ranked_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">匯出與可信度說明</div>', unsafe_allow_html=True)
    st.write("資料來源目前為展示用示範資料，下一階段將以正式公開資料取代。分析結果屬決策輔助，不作唯一依據。")
    st.download_button(
        label="下載目前排序 CSV",
        data=ranked_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="livability_ranking.csv",
        mime="text/csv",
    )


def run_app() -> None:
    st.set_page_config(page_title="Taiwan Livability AI Platform", page_icon="🏙️", layout="wide")
    inject_styles()
    render_hero()

    weights = render_sidebar()
    ranked_df = calculate_livability_score(load_regions(), weights)
    render_metrics(ranked_df)

    queried_region = render_address_search(ranked_df)

    st.markdown('<div class="section-title">區域地圖總覽</div>', unsafe_allow_html=True)
    render_map(ranked_df, queried_region)

    left, right = st.columns([1.2, 0.8])
    with left:
        render_rankings(ranked_df)
    with right:
        render_ai_panel(ranked_df)

    render_region_analysis(ranked_df, weights, queried_region)
    render_compare(ranked_df)
    render_export(ranked_df)
