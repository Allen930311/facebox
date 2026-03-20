# 專案上下文 (Agent Context)：FaceBox

> **最後更新時間**：2026-03-20 14:31
> **自動生成**：由 `prepare_context.py` 產生，供 AI Agent 快速掌握專案全局

---

## 🎯 1. 專案目標 (Project Goal)
* **核心目的**：[繁體中文](#繁體中文) | [English](#english)
* _完整說明見 [README.md](README.md)_

## 🛠️ 2. 技術棧與環境 (Tech Stack & Environment)
* _（未偵測到 package.json / pyproject.toml / requirements.txt）_

## 📂 3. 核心目錄結構 (Core Structure)
_(💡 AI 讀取守則：請依據此結構尋找對應檔案，勿盲目猜測路徑)_
```text
FaceBox/
├── AGENT_CONTEXT.md
├── README.md
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
├── facebox-mcp
│   ├── server.py
│   └── start-backend.ps1
└── notebooks
    └── sd_webui_colab.ipynb
```

## 🏛️ 4. 架構與設計約定 (Architecture & Conventions)
* _（尚無 `.auto-skill-local.md`，專案踩坑經驗將在開發過程中自動累積）_

## 🚦 5. 目前進度與待辦 (Current Status & TODO)
_(自動提取自最近日記 2026-03-20)_

### 🚧 待辦事項
- [x] 以調降後的參數重新執行 LoRA 訓練。
- [ ] 訓練成功後下載 LoRA 模型，整合至本地 FaceBox MCP 生成流程。
- [ ] 評估是否需要針對 A100/L4 GPU 建立差異化設定檔。
- [ ] 持續維護 GitHub 上的 README 文件，同步 Colab 筆記本的變更。

