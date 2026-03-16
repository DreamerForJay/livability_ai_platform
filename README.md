# 臺灣宜居地智慧分析平台：基於環境資料與AI分析的城市宜居度評估系統

**團隊名稱：** `Livability AI Team`  
**英文名稱：** `Taiwan Livability AI Platform`

本專案為「智慧創新大賞」參賽作品，目標是建立一套結合環境資料、生活機能資料、地理資訊分析與 AI 摘要能力的城市宜居度評估系統。平台讓使用者能以地圖、指標分數與自然語言問答三種方式，快速理解不同區域的宜居程度、風險暴露與生活便利性，作為租屋、購屋、設點與區域比較的決策輔助工具。

## 線上展示

- Streamlit Demo: https://livabilityai.streamlit.app/

## 一、專案背景

一般民眾在評估一個區域是否適合居住、通勤、就學或商業設點時，常常需要同時查看空氣品質、交通便利性、公共設施、生活機能與潛在風險。但實際上，這些資料分散於不同平台，格式不一致，也不容易用一般人能理解的方式整合解讀。

本專案希望解決的核心問題是：

**如何把分散的城市環境資料轉化為可查詢、可比較、可解釋的宜居決策系統。**

## 二、專案目標

- 建立可視覺化的城市宜居度分析平台
- 整合多項環境與生活機能指標，形成區域綜合評分
- 提供互動式地圖，快速比較不同區域
- 提供 AI 問答與摘要，降低非專業使用者理解門檻
- 建立可延伸至更多城市與更多資料源的技術基礎

## 三、核心功能

### 1. 區域宜居度評分

系統整合多項評估指標，對各行政區進行標準化與加權計算，產生綜合宜居分數。

目前示範指標包含：

- 空氣品質
- 生活機能
- 交通便利
- 公共服務資源
- 風險暴露反向分數

### 2. 互動式地圖分析

使用者可透過地圖查看不同區域分布，快速辨識高分區域與相對弱勢區域，提升資料理解效率。

### 2.5 地址與地標查詢

使用者可直接輸入行政區、地標或常見地址關鍵字，例如逢甲夜市、草悟道、台中火車站與台中市西屯區，系統會自動對應至分析區域並回傳宜居評估結果。

### 3. 區域比較

平台支援多區域比較，協助使用者從多維度檢視差異，適合用於租屋、購屋、家庭生活規劃或商業設點決策。

### 4. AI 問答與摘要

系統支援自然語言輸入，例如：

- 哪裡最適合學生租屋？
- 哪區風險較低？
- 哪些區域生活機能完整但風險相對較小？

系統可根據現有資料回傳摘要與建議，讓資料不只可看，也可被理解。

## 四、系統架構

本專案採模組化設計，便於後續擴充：

- `data/`：示範資料與未來正式資料集
- `src/data_loader.py`：資料載入與欄位轉換
- `src/scoring.py`：宜居度評分公式與加權邏輯
- `src/summary.py`：AI 摘要與問答邏輯
- `src/ui.py`：Streamlit 視覺化與互動介面
- `tests/`：核心邏輯測試

## 五、技術實作

### 開發技術

- Python
- Streamlit
- Pandas
- Plotly
- FastAPI

### 設計原則

- 先完成可解釋的規則式評分，再逐步導入更進階的 AI 分析
- 先聚焦競賽可展示的 MVP，再擴展成完整平台
- 讓資料分析結果可視化、可驗證、可說明

## 六、目前完成內容

目前已完成第一版 MVP：

- 專案規格書
- 專案程式骨架
- FastAPI 後端 API
- 區域示範資料集
- 宜居度評分模組
- AI 摘要與問答雛形
- Streamlit 展示介面
- 基本測試與執行驗證

## 七、介面展示內容

目前系統畫面包含：

- 區域綜合分數總覽
- 地址 / 地標查詢
- 區域地圖分布
- 區域排行表
- 單區分析摘要
- 多區域比較圖
- AI 問答區塊
- 排序結果匯出功能

## 八、系統啟動方式

### 1. 啟動前端展示介面

```bash
python -m streamlit run app.py
```

### 2. 啟動 FastAPI 後端

```bash
python -m uvicorn src.api.app:app --reload
```

啟動後可使用：

- API 文件：`http://127.0.0.1:8000/docs`
- API 首頁檢查：`http://127.0.0.1:8000/health`

## 九、如何安裝專案

在專案目錄中執行：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 十、目前提供的 API

- `GET /health`：健康檢查
- `GET /metadata`：資料狀態與來源規劃
- `GET /regions`：取得預設權重下的區域排行
- `GET /regions/{identifier}`：取得單一區域詳細資訊
- `POST /score`：依自訂權重重新計算排行
- `POST /resolve`：解析地址 / 地標到對應區域
- `POST /ask`：AI 問答
- `GET /demo-flow`：評審展示建議流程

## 十一、真實 geocoding 與開放資料接入指引

目前專案已先建立可擴充骨架，但預設仍使用示範資料與本地地址映射。若要升級為正式版本，建議依下列順序進行：

### 1. 串接真實 geocoding

- 檔案位置：`src/geocoding.py`
- 目前已預留 provider 機制
- 預設為 `local`
- 後續可改為：
  - `nominatim`
  - TGOS API
  - Google Geocoding API

免費優先建議：

- 開發與競賽展示階段：優先使用 `Nominatim`
- 正式上線或高流量：改用商業 geocoding 或自建服務

目前專案已針對 `Nominatim` 補上：

- 快取機制
- 單機節流
- 自訂 User-Agent

這是為了符合其公開服務的使用限制。

建議流程：

1. 取得 geocoding 服務帳號或 API Key
2. 將 provider 與授權資訊寫入環境變數
3. 以地址取得經緯度
4. 再將經緯度對應至行政區或最近分析單元

### 2. 串接正式開放資料

建議優先資料類型：

- 空氣品質資料
- 公共設施與生活機能 POI
- 交通節點資料
- 行政區界資料
- 災害風險或潛勢資料

建議實作方式：

1. 在 `data/raw/` 放原始資料
2. 新增 `src/data_pipeline/` 做清理與欄位統一
3. 輸出正式版 `data/processed/*.csv`
4. 再由 `src/data_loader.py` 讀取正式資料

### 3. API 與前端整合

目前 Streamlit 仍直接呼叫本地模組。下一階段可改為：

- Streamlit 改呼叫 FastAPI
- 或額外建立 React 前端呼叫 FastAPI

這樣就能形成真正的前後端分離架構。

## 十二、安全配置說明

目前專案已採以下原則避免敏感資訊外露：

- 不將 API Key、Token 或密碼寫死在前端頁面或 Git 版控中
- 使用 `.env` 或 `.streamlit/secrets.toml` 保存私密設定
- `.gitignore` 已排除 `.env` 與真實 `secrets.toml`
- FastAPI 文件可透過 `API_DOCS_ENABLED=false` 在正式環境關閉
- 前端不應直接呼叫需要金鑰的第三方服務，應由後端代為請求

重要說明：

- 對於 Web 專案，敏感金鑰的正確做法是「只放在伺服器端」，而不是放到瀏覽器端再加密。
- 如果金鑰送到前端，使用者仍可在瀏覽器開發者工具中看到，因此那不算真正安全。
- 若部署在 Streamlit Cloud，請將敏感設定放入其 Secrets 管理；若部署在雲端主機，請使用環境變數或平台 Secret Manager。

## 十三、專案結構

```text
.
├─ app.py
├─ api.py
├─ TESTING.md
├─ requirements.txt
├─ README.md
├─ SPEC-KIT.md
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ data/
│  └─ processed/
│     └─ regions_demo.csv
├─ src/
│  ├─ __init__.py
│  ├─ services.py
│  ├─ geocoding.py
│  ├─ config.py
│  ├─ data_loader.py
│  ├─ scoring.py
│  ├─ summary.py
│  ├─ resolver.py
│  ├─ ui.py
│  └─ api/
│     ├─ __init__.py
│     ├─ app.py
│     └─ schemas.py
└─ tests/
   ├─ conftest.py
   ├─ test_api.py
   ├─ test_resolver.py
   └─ test_scoring.py
```

## 十四、測試與 GitHub 驗證

本專案已提供：

- 本地測試文件：`TESTING.md`
- GitHub Actions 自動化測試：`.github/workflows/ci.yml`

本地執行：

```bash
python -m pytest tests -q
```

推上 GitHub 後，當你對 `main` push 或發出 PR，GitHub Actions 會自動執行測試。

## 十五、競賽價值

本作品的價值不只是做出地圖或聊天機器人，而是把城市資料轉化為具備決策意義的應用系統。它能幫助使用者從多個面向綜合判讀一個區域的宜居程度，並透過 AI 將資料結果轉譯成易懂建議。

此平台具備以下延伸潛力：

- 租屋與購屋決策輔助
- 商業設點評估
- 區域治理與資源規劃
- 城市數據服務平台

## 十六、後續發展方向

後續將持續擴充以下能力：

- 串接真實開放資料來源
- 擴大分析範圍至更多縣市
- 加入更完整的 GIS 圖層
- 導入正式 LLM API 與檢索機制
- 讓 Streamlit 或新前端直接串接 FastAPI
- 強化前端互動設計與展示品質
- 製作完整 Demo 影片與競賽簡報

## 十七、競賽資訊

本專案為「智慧創新大賞」參賽作品。

- 團隊名稱：`Livability AI Team`
- 參賽作品名稱：`臺灣宜居地智慧分析平台：基於環境資料與AI分析的城市宜居度評估系統`

## 十八、備註

目前版本為競賽展示用 MVP。資料集與分析結果將在後續版本中持續以正式公開資料進行替換與優化。
