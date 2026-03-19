# FaceBox — 個人臉部克隆工具

使用 Stable Diffusion + LoRA 進行臉部克隆與圖片生成。

## 架構

```
FaceBox/
├── facebox/                  # 核心專案
│   ├── backend/              # FastAPI 後端 (port 17494)
│   │   ├── main.py           # 入口
│   │   ├── config.py         # 設定
│   │   ├── models.py         # 資料模型
│   │   ├── database/         # JSON 資料庫
│   │   ├── routes/           # API 路由
│   │   └── services/         # SD WebUI 客戶端 & LoRA 訓練
│   └── data/                 # 資料目錄
│       ├── profiles/         # 人臉 Profile (照片、訓練資料)
│       ├── outputs/          # 生成的圖片
│       └── lora_models/      # 訓練完成的 LoRA 模型
├── facebox-mcp/              # MCP Server (Claude Code 整合)
│   └── server.py
└── AGENT_CONTEXT.md
```

## 前置需求

1. **Python 3.10+**
2. **Stable Diffusion WebUI (A1111)** — 在 port 7860 啟動，需加上 `--api` 參數
3. **kohya-ss/sd-scripts** — 用於 LoRA 訓練（可選，訓練時才需要）

## 快速開始

### 1. 啟動 SD WebUI

```bash
cd stable-diffusion-webui
python launch.py --api
```

### 2. 啟動 FaceBox 後端

```powershell
cd FaceBox/facebox
pip install -r backend/requirements.txt
python -m backend.main
```

### 3. 使用流程

1. **建立 Profile** — 給你的臉取個名字
2. **上傳照片** — 10-20 張不同角度的高品質照片
3. **訓練 LoRA** — 使用 kohya-ss 訓練臉部 LoRA
4. **生成圖片** — 用提示詞生成各種風格的人像

## API (port 17494)

| 端點 | 說明 |
|------|------|
| `GET /health` | 健康檢查 |
| `GET /profiles` | 列出 Profile |
| `POST /profiles` | 建立 Profile |
| `POST /profiles/{id}/samples` | 上傳參考照片 |
| `POST /profiles/{id}/samples/batch` | 批次上傳 |
| `POST /train` | 準備 LoRA 訓練 |
| `POST /train/{id}/mark-complete` | 標記訓練完成 |
| `POST /generate` | 生成圖片 |
| `GET /output/{id}` | 下載圖片 |
| `GET /history` | 生成歷史 |

## MCP 整合

在 Claude Code 設定中加入：

```json
{
  "mcpServers": {
    "facebox": {
      "command": "python",
      "args": ["c:/Users/Allen/OneDrive/Desktop/FaceBox/facebox-mcp/server.py"]
    }
  }
}
```
