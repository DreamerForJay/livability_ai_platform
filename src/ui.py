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
        :root {
            --bg-main: linear-gradient(180deg, #f5f8fc 0%, #f7fbf6 100%);
            --bg-spot-a: rgba(159, 196, 255, 0.25);
            --bg-spot-b: rgba(183, 231, 198, 0.30);
            --card-bg: rgba(255, 255, 255, 0.84);
            --card-border: rgba(38, 70, 83, 0.10);
            --card-shadow: rgba(59, 92, 122, 0.10);
            --text-main: #14243a;
            --text-muted: #52667a;
            --accent: #16324f;
            --badge-bg: #e9f4ee;
            --badge-text: #165b47;
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-main: linear-gradient(180deg, #09111a 0%, #0d1621 100%);
                --bg-spot-a: rgba(63, 94, 251, 0.18);
                --bg-spot-b: rgba(42, 157, 143, 0.16);
                --card-bg: rgba(11, 24, 37, 0.82);
                --card-border: rgba(159, 196, 255, 0.16);
                --card-shadow: rgba(0, 0, 0, 0.28);
                --text-main: #f5f8fb;
                --text-muted: #c7d5e4;
                --accent: #d9ecff;
                --badge-bg: rgba(56, 101, 86, 0.40);
                --badge-text: #d9f7ea;
            }
        }
        .stApp {
            background:
                radial-gradient(circle at top left, var(--bg-spot-a), transparent 32%),
                radial-gradient(circle at bottom right, var(--bg-spot-b), transparent 28%),
                var(--bg-main);
        }
        .stApp, .stApp p, .stApp label, .stApp li, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3 {
            color: var(--text-main);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }
        .hero {
            padding: 1.8rem 1.9rem;
            border-radius: 28px;
            background: linear-gradient(135deg, #16324f 0%, #2f6690 54%, #3a7d78 100%);
            color: #ffffff;
            box-shadow: 0 24px 48px rgba(19, 39, 58, 0.18);
            margin-bottom: 1.4rem;
        }
        .hero h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2.35rem;
            line-height: 1.15;
            color: #ffffff !important;
        }
        .hero p {
            margin: 0;
            font-size: 1rem;
            line-height: 1.65;
            opacity: 0.95;
            color: #f5f9ff !important;
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
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 25px var(--card-shadow);
            backdrop-filter: blur(16px);
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            margin-bottom: 1.15rem;
        }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 12px 24px var(--card-shadow);
            backdrop-filter: blur(16px);
        }
        .stat-label {
            color: var(--text-muted) !important;
            font-size: 0.85rem;
            margin-bottom: 0.35rem;
        }
        .stat-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-main) !important;
        }
        .panel-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            color: var(--accent) !important;
        }
        .panel-copy {
            color: var(--text-muted) !important;
            line-height: 1.65;
        }
        .section-title {
            margin-top: 0.25rem;
            margin-bottom: 0.2rem;
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--accent);
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            margin: 0 0.45rem 0.45rem 0;
            border-radius: 999px;
            background: var(--badge-bg);
            color: var(--badge-text);
            font-size: 0.88rem;
            font-weight: 600;
        }
        .hint {
            color: var(--text-muted);
            font-size: 0.92rem;
        }
        .section-space {
            margin-top: 1.15rem;
        }
        [data-testid="stMetric"] {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 0.65rem 0.85rem;
            box-shadow: 0 10px 20px var(--card-shadow);
        }
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"] {
            color: var(--text-main) !important;
        }
        [data-testid="stDataFrame"] {
            background: var(--card-bg);
            border-radius: 18px;
            border: 1px solid var(--card-border);
            padding: 0.35rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(50, 70, 94, 0.94) 0%, rgba(63, 88, 110, 0.94) 100%);
        }
        [data-testid="stSidebar"] * {
            color: #f4f8fc !important;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {
            background: var(--card-bg) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--card-border) !important;
        }
        .stSlider [data-baseweb="slider"] {
            padding-top: 0.25rem;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 999px;
            border: 1px solid rgba(47, 102, 144, 0.25);
            background: linear-gradient(135deg, #1d4e89 0%, #2a9d8f 100%);
            color: #ffffff !important;
            padding: 0.55rem 1rem;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.4rem;
        }
        .stTabs [data-baseweb="tab"] {
            background: var(--card-bg);
            border-radius: 999px;
            border: 1px solid var(--card-border);
            color: var(--text-main);
        }
        .hero {
            padding: 1.2rem 1.5rem;
            margin-bottom: 1rem;
        }
        .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin-bottom: 0.7rem;
        }
        .hero-kicker {
            display: inline-block;
            padding: 0.28rem 0.72rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.16);
            border: 1px solid rgba(255, 255, 255, 0.18);
            font-size: 0.82rem;
            letter-spacing: 0.02em;
        }
        .step-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 0.7rem 0 1rem 0;
        }
        .step-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 22px var(--card-shadow);
        }
        .step-index {
            color: var(--text-muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .step-title {
            font-size: 1rem;
            font-weight: 700;
            margin: 0.2rem 0 0.25rem 0;
        }
        .metric-icon {
            font-size: 1.2rem;
            margin-bottom: 0.35rem;
        }
        .stat-subtext {
            color: var(--text-muted) !important;
            font-size: 0.84rem;
            margin-top: 0.3rem;
        }
        .search-shell {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 22px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: 0 12px 24px var(--card-shadow);
            margin-bottom: 1rem;
        }
        .search-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            color: var(--accent) !important;
        }
        .search-copy {
            color: var(--text-muted) !important;
            font-size: 0.92rem;
            margin-bottom: 0.75rem;
        }
        .result-hero {
            background: linear-gradient(135deg, rgba(22, 50, 79, 0.95) 0%, rgba(47, 102, 144, 0.92) 100%);
            border-radius: 24px;
            padding: 1.2rem 1.25rem;
            color: #ffffff;
            box-shadow: 0 18px 36px rgba(19, 39, 58, 0.18);
        }
        .result-label {
            font-size: 0.84rem;
            opacity: 0.84;
            margin-bottom: 0.3rem;
        }
        .result-region {
            font-size: 2.5rem;
            line-height: 1.05;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .result-score {
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }
        .score-track {
            width: 100%;
            height: 10px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.16);
            overflow: hidden;
            margin: 0.5rem 0 0.7rem 0;
        }
        .score-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #8be9c4 0%, #d9f99d 100%);
        }
        .weight-meta {
            color: #e8f0f7 !important;
            font-size: 0.88rem;
            margin-top: 0.5rem;
        }
        @media (max-width: 980px) {
            .stat-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .step-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
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
    total = air + facility + transport + public_service + risk
    normalized_total = min(total, 1.0)

    st.sidebar.caption(f"Total weight: {total:.2f}")
    st.sidebar.progress(normalized_total)
    if abs(total - 1.0) > 0.001:
        st.sidebar.warning("目前權重總和不等於 1，分數會依相對比例計算。")

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
            <div class="hero-meta">
                <span class="hero-kicker">AI 決策儀表板</span>
                <span class="hero-kicker">Taichung Demo Dataset</span>
            </div>
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


def render_steps() -> None:
    st.markdown(
        """
        <div class="step-grid">
            <div class="step-card">
                <div class="step-index">Step 1</div>
                <div class="step-title">搜尋</div>
                <div class="panel-copy">輸入地址、地標或行政區，快速鎖定分析入口。</div>
            </div>
            <div class="step-card">
                <div class="step-index">Step 2</div>
                <div class="step-title">定位</div>
                <div class="panel-copy">將查詢結果映射到對應區域，建立統一分析單元。</div>
            </div>
            <div class="step-card">
                <div class="step-index">Step 3</div>
                <div class="step-title">分析</div>
                <div class="panel-copy">依權重計算宜居分數，對照地圖與指標差異。</div>
            </div>
            <div class="step-card">
                <div class="step-index">Step 4</div>
                <div class="step-title">建議</div>
                <div class="panel-copy">輸出適用族群、風險提示與簡報可用結論。</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(ranked_df: pd.DataFrame) -> None:
    top_region = ranked_df.iloc[0]
    safest_region = ranked_df.sort_values("risk_score").iloc[0]
    avg_score = round(float(ranked_df["livability_score"].mean()), 2)
    highest_facility = ranked_df.sort_values("facility_score", ascending=False).iloc[0]
    st.markdown(
        f"""
        <div class="stat-grid">
            <div class="stat-card">
                <div class="metric-icon">🏆</div>
                <div class="stat-label">最佳區域</div>
                <div class="stat-value">{top_region["region_name"]}</div>
                <div class="stat-subtext">目前綜合宜居分數最高</div>
            </div>
            <div class="stat-card">
                <div class="metric-icon">📈</div>
                <div class="stat-label">最高分</div>
                <div class="stat-value">{top_region["livability_score"]}</div>
                <div class="stat-subtext">作為首頁主展示案例</div>
            </div>
            <div class="stat-card">
                <div class="metric-icon">🛡️</div>
                <div class="stat-label">最低風險區</div>
                <div class="stat-value">{safest_region["region_name"]}</div>
                <div class="stat-subtext">風險暴露相對較低</div>
            </div>
            <div class="stat-card">
                <div class="metric-icon">🏙️</div>
                <div class="stat-label">高機能代表</div>
                <div class="stat-value">{highest_facility["region_name"]}</div>
                <div class="stat-subtext">生活機能指標表現突出</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"目前平均綜合分數為 {avg_score}，此頁以台中市示範資料呈現分析流程。")


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
    st.markdown(
        """
        <div class="search-shell">
            <div class="search-title">搜尋與定位</div>
            <div class="search-copy">可輸入行政區、地標或常見地址關鍵字，例如：逢甲夜市、草悟道、台中火車站、台中市西屯區。</div>
        """,
        unsafe_allow_html=True,
    )
    query = st.text_input("搜尋地址或地標", value="逢甲夜市", placeholder="例如：逢甲夜市、草悟道、台中火車站")
    cols = st.columns([1.2, 0.8])
    with cols[1]:
        st.caption("建議查詢")
        for item in suggested_queries():
            st.write(f"- 🔎 {item}")

    match = resolve_address(query, ranked_df)
    if not match:
        st.warning("目前無法精準比對該地址，請先輸入台中市行政區或頁面提供的示範地標。")
        st.markdown("</div>", unsafe_allow_html=True)
        return None

    selected_row = ranked_df[ranked_df["region_name"] == match.region_name].iloc[0]
    st.success(
        f"已將「{match.query}」定位到 {match.region_name}，信心等級：{match.confidence}，判定方式：{match.matched_by}。"
    )

    st.markdown(
        f"""
        <div class="result-hero">
            <div class="result-label">最終推薦區域</div>
            <div class="result-region">{selected_row["region_name"]}</div>
            <div class="result-score">宜居指數 {selected_row["livability_score"]}</div>
            <div class="score-track">
                <div class="score-fill" style="width: {min(float(selected_row["livability_score"]), 100):.2f}%;"></div>
            </div>
            <div class="weight-meta">這個結果會同步反映左側權重設定與地址映射規則。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">定位結果</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-copy">系統已將輸入內容映射到對應行政區，並產生可解釋的區域判讀。</div>', unsafe_allow_html=True)
        st.metric("對應區域", selected_row["region_name"])
        st.metric("綜合宜居分數", selected_row["livability_score"])
        st.write(generate_region_summary(selected_row))
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">決策建議</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-copy">以下建議可作為租屋、家庭居住或商業設點的簡報話術。</div>', unsafe_allow_html=True)
        st.markdown("**適用情境建議**")
        for item in persona_recommendations(selected_row):
            st.write(f"- {item}")
        st.markdown("**判讀標籤**")
        badges = "".join([f'<span class="badge">{badge}</span>' for badge in score_badges(selected_row)])
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

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
    st.markdown('<div class="hint">左側可調整權重，這個排序會即時反映不同使用情境下的結果變化。</div>', unsafe_allow_html=True)
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
    st.markdown(
        f'<div class="card"><div class="panel-title">AI 分析回應</div><div class="panel-copy">{answer_question(question, ranked_df)}</div></div>',
        unsafe_allow_html=True,
    )


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
    st.markdown('<div class="hint">建議展示 2 到 3 個區域，最容易說清楚不同指標的取捨。</div>', unsafe_allow_html=True)
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
    st.markdown(
        f'<div class="card"><div class="panel-title">比較結論</div><div class="panel-copy">{compare_regions(compare_df)}</div></div>',
        unsafe_allow_html=True,
    )


def render_export(ranked_df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">匯出與可信度說明</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card"><div class="panel-title">資料聲明</div><div class="panel-copy">資料來源目前為展示用示範資料，下一階段將以正式公開資料取代。分析結果屬決策輔助，不作唯一依據。</div></div>',
        unsafe_allow_html=True,
    )
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
    render_steps()

    weights = render_sidebar()
    ranked_df = calculate_livability_score(load_regions(), weights)
    render_metrics(ranked_df)

    queried_region = render_address_search(ranked_df)

    overview_tab, insight_tab, compare_tab = st.tabs(["總覽地圖", "AI 與單區分析", "區域比較與匯出"])

    with overview_tab:
        st.markdown('<div class="section-title">區域地圖總覽</div>', unsafe_allow_html=True)
        render_map(ranked_df, queried_region)
        render_rankings(ranked_df)

    with insight_tab:
        left, right = st.columns([1.1, 0.9])
        with left:
            render_region_analysis(ranked_df, weights, queried_region)
        with right:
            render_ai_panel(ranked_df)

    with compare_tab:
        render_compare(ranked_df)
        render_export(ranked_df)
