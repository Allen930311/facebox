# 專案上下文 (Agent Context)：FaceBox

> **最後更新時間**：2026-03-18 17:38
> **自動生成**：由 `prepare_context.py` 產生，供 AI Agent 快速掌握專案全局

---

## 🎯 1. 專案目標 (Project Goal)
* **核心目的**：_（請手動補充，或建立 README.md）_

## 🛠️ 2. 技術棧與環境 (Tech Stack & Environment)
* _（未偵測到 package.json / pyproject.toml / requirements.txt）_

## 📂 3. 核心目錄結構 (Core Structure)
_(💡 AI 讀取守則：請依據此結構尋找對應檔案，勿盲目猜測路徑)_
```text
FaceBox/
├── AGENT_CONTEXT.md
├── diary
│   └── 2026
│       └── 03
├── facebox
│   ├── README.md
│   ├── backend
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   ├── routes
│   │   └── services
│   └── data
│       ├── lora_models
│       ├── outputs
│       └── profiles
└── facebox-mcp
    ├── server.py
    └── start-backend.ps1
```

## 🏛️ 4. 架構與設計約定 (Architecture & Conventions)
* _（尚無 `.auto-skill-local.md`，專案踩坑經驗將在開發過程中自動累積）_

## 🚦 5. 目前進度與待辦 (Current Status & TODO)
_(自動提取自最近日記 2026-03-18)_

### 🚧 待辦事項
- [ ] 安裝 Stable Diffusion WebUI (A1111)，以 `--api` 參數啟動在 port 7860。
- [ ] 安裝 kohya-ss/sd-scripts 用於 LoRA 訓練。
- [ ] 啟動 FaceBox 後端，測試 `/health` 端點與 SD WebUI 連線。
- [ ] 上傳 10-20 張參考照片，測試完整的臉部克隆 → LoRA 訓練 → 圖片生成流程。
- [ ] 整合 Voicebox + FaceBox，實現「聲音 + 臉部」數位分身。

