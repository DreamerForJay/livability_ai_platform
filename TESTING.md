# 測試文件

本文件說明本專案目前的測試範圍、執行方式與 GitHub 自動化驗證流程。

## 1. 測試目標

目前測試聚焦於競賽 MVP 的核心可用性，確保：

- 區域宜居度評分邏輯正確
- 地址 / 地標解析行為穩定
- FastAPI 後端可正常回應
- 專案在 GitHub 上可自動執行測試

## 2. 測試範圍

目前已涵蓋下列測試：

- `tests/test_scoring.py`
  - 驗證權重正規化
  - 驗證宜居分數計算邏輯

- `tests/test_resolver.py`
  - 驗證行政區關鍵字解析
  - 驗證未知地址時的回應

- `tests/test_api.py`
  - 驗證 `/health`
  - 驗證 `/regions`
  - 驗證 `/resolve`

## 3. 本地執行方式

先安裝依賴：

```bash
pip install -r requirements.txt pytest
```

執行全部測試：

```bash
python -m pytest tests -q
```

如果要看更詳細輸出：

```bash
python -m pytest tests -v
```

## 4. 預期結果

目前正常情況下，應看到類似結果：

```text
7 passed
```

## 5. GitHub Actions 自動測試

本專案已提供 GitHub Actions workflow：

- 路徑：`.github/workflows/ci.yml`

觸發時機：

- push 到 `main`
- pull request 到 `main`

流程內容：

1. 建立 Python 環境
2. 安裝依賴與 `pytest`
3. 執行 `python -m pytest tests -q`

## 6. 目前未涵蓋項目

以下尚未納入自動測試：

- Streamlit 視覺畫面測試
- 真實 geocoding API 整合測試
- 正式開放資料 ETL 測試
- 效能壓力測試
- 安全性掃描

## 7. 下一步測試建議

若專案進一步擴充，建議補上：

- geocoding provider mock 測試
- 真實資料欄位驗證測試
- API 錯誤處理測試
- 前端互動 smoke test
- secret / env 設定檢查
