# 臺灣宜居地智慧分析平台：基於環境資料與AI分析的城市宜居度評估系統

`Livability AI Team`

English project name: `Taiwan Livability AI Platform`

學生組競賽 MVP，提供城市區域宜居性評分、區域比較與自然語言摘要展示。

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 專案結構

```text
.
├─ app.py
├─ requirements.txt
├─ README.md
├─ SPEC-KIT.md
├─ data/
│  └─ processed/
│     └─ regions_demo.csv
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ data_loader.py
│  ├─ scoring.py
│  └─ summary.py
└─ tests/
   └─ test_scoring.py
```

## 目前內容

- 內建示範資料
- 宜居性評分公式
- 區域排行
- 區域比較圖
- 規則式 AI 摘要

## 接下來你要補的

1. 用真實城市開放資料取代 `data/processed/regions_demo.csv`
2. 若要接 LLM，把 `src/summary.py` 改成 API 呼叫
3. 若要做 API 化，再加 `FastAPI`
