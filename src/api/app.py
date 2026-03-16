from __future__ import annotations

from fastapi import FastAPI, HTTPException

from src.config import API_DOCS_ENABLED
from src.config import DEFAULT_WEIGHTS
from src.services import get_region, list_regions, metadata, resolve_query
from src.summary import answer_question
from src.api.schemas import (
    AskPayload,
    AskResponse,
    DemoFlowResponse,
    RankingResponse,
    RegionResponse,
    ResolvePayload,
    ResolveResponse,
    WeightsPayload,
)


app = FastAPI(
    title="Taiwan Livability AI Platform API",
    description="提供區域排名、地址解析、AI 問答與展示流程的後端 API。",
    version="1.0.0",
    docs_url="/docs" if API_DOCS_ENABLED else None,
    redoc_url="/redoc" if API_DOCS_ENABLED else None,
    openapi_url="/openapi.json" if API_DOCS_ENABLED else None,
)


def weights_to_dict(payload: WeightsPayload | None) -> dict[str, float]:
    return payload.model_dump() if payload else DEFAULT_WEIGHTS.copy()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata")
def get_metadata() -> dict[str, object]:
    return metadata()


@app.get("/regions", response_model=RankingResponse)
def regions() -> RankingResponse:
    weights = DEFAULT_WEIGHTS.copy()
    return RankingResponse(items=[RegionResponse(**item) for item in list_regions(weights)], weights=weights)


@app.post("/score", response_model=RankingResponse)
def score(payload: WeightsPayload) -> RankingResponse:
    weights = weights_to_dict(payload)
    return RankingResponse(items=[RegionResponse(**item) for item in list_regions(weights)], weights=weights)


@app.get("/regions/{identifier}", response_model=RegionResponse)
def region_detail(identifier: str) -> RegionResponse:
    region = get_region(identifier)
    if not region:
        raise HTTPException(status_code=404, detail="找不到指定區域。")
    return RegionResponse(**region)


@app.post("/resolve", response_model=ResolveResponse)
def resolve(payload: ResolvePayload) -> ResolveResponse:
    matched = resolve_query(payload.query, weights_to_dict(payload.weights))
    if not matched:
        raise HTTPException(status_code=404, detail="目前無法解析該地址或地標。")
    return ResolveResponse(**matched)


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskPayload) -> AskResponse:
    weights = weights_to_dict(payload.weights)
    ranked_items = list_regions(weights)
    import pandas as pd

    ranked_df = pd.DataFrame(ranked_items)
    answer = answer_question(payload.question, ranked_df)
    recommended_region = ranked_df.iloc[0]["region_name"] if not ranked_df.empty else None
    return AskResponse(question=payload.question, answer=answer, recommended_region=recommended_region)


@app.get("/demo-flow", response_model=DemoFlowResponse)
def demo_flow() -> DemoFlowResponse:
    return DemoFlowResponse(
        steps=[
            {
                "title": "問題切入",
                "instruction": "先說明城市資料分散、選址與居住評估困難，帶出平台需求。",
            },
            {
                "title": "地址查詢",
                "instruction": "輸入逢甲夜市或草悟道，展示系統如何定位到對應區域。",
            },
            {
                "title": "區域判讀",
                "instruction": "展示宜居分數、風險標籤、適合族群與 AI 摘要。",
            },
            {
                "title": "多區比較",
                "instruction": "比較西屯區、西區與北屯區，說明不同使用情境下的排序差異。",
            },
            {
                "title": "延伸價值",
                "instruction": "說明未來可串接真實 geocoding、開放資料與正式 AI 模型。",
            },
        ]
    )
