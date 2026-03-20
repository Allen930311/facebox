# 🎭 FaceBox — Personal Face Cloning & Image Generation

[繁體中文](#繁體中文) | [English](#english)

---

## 繁體中文

FaceBox 是一個結合 **Stable Diffusion** 與 **LoRA** 技術的個人臉部克隆工具。透過這套工具，您可以輕鬆克隆人臉、訓練專屬 LoRA 模型，並生成各種風格的高品質人像照片。

### 🌟 核心特色
- **臉部克隆 (Face Cloning)**：只需 10-20 張照片即可訓練出極度傳神的個人臉部模型。
- **雲端算力 (Colab Integration)**：內建 Google Colab 支援，即便本地沒有高端 GPU 也能進行 LoRA 訓練與高速生圖。
- **MCP 整合 (Model Context Protocol)**：提供 `facebox-mcp` 伺服器，讓 AI Agent (如 Claude/Antigravity) 直接調用臉部生成能力。

### 🏗️ 系統架構
```text
┌─────────────────────────────┐      Cloudflare Tunnel       ┌─────────────────────┐
│  Google Colab (T4 GPU)      │◄────────────────────────────►│  本地 FaceBox       │
│  SD WebUI (:7860 --api)     │  (https://xxx.trycloudflare.com)│  Backend (:17494)   │
│  + 訓練框架 (kohya-ss)       │                              │  + MCP Server       │
└─────────────────────────────┘                              └─────────────────────┘
```

### 📂 目錄說明
- `facebox/`: 核心後端邏輯與數據管理。
- `facebox-mcp/`: MCP 伺服器實作，串接 AI Agent。
- `notebooks/`: 
    - `sd_webui_colab_public.ipynb`: **開源版**。適合大眾使用，預設路徑為通用名稱。

### 🚀 快速開始
1. **部署 GPU 環境**：
   - 開啟 `notebooks/` 下的 Colab 筆記本。
   - 依序執行 Cell 並獲取 `Cloudflare Tunnel URL`。
2. **啟動本地服務**：
   - 設定環境變數：`set SD_WEBUI_URL=https://your-tunnel-url.trycloudflare.com`
   - 執行 `facebox-mcp` 或啟動 `facebox/backend/main.py`。
3. **開始生成**：
   - 透過 AI 助理下令：「幫我生成一張 [sks person] 穿著西裝的照片」。

---

## English

FaceBox is a personal face cloning and image generation tool powered by **Stable Diffusion** and **LoRA**. It allows you to clone faces, train custom LoRA models, and generate high-quality portraits in various styles.

### 🌟 Features
- **Face Cloning**: Achieve professional results with just 10-20 reference photos.
- **Colab GPU Integration**: Leverage Google Colab's T4 GPU for training and generation without needing local hardware.
- **MCP Support**: Use the `facebox-mcp` server to connect FaceBox directly to AI agents.

### 🏗️ Architecture
```text
┌─────────────────────────────┐      Cloudflare Tunnel       ┌─────────────────────┐
│  Google Colab (T4 GPU)      │◄────────────────────────────►│  Local FaceBox      │
│  SD WebUI (:7860 --api)     │  (https://xxx.trycloudflare.com)│  Backend (:17494)   │
│  + Kohya-ss (Training)      │                              │  + MCP Server       │
└─────────────────────────────┘                              └─────────────────────┘
```

### 📂 Project Structure
- `facebox/`: Core backend logic and data storage.
- `facebox-mcp/`: MCP server implementation for AI agent integration.
- `notebooks/`:
    - `sd_webui_colab_public.ipynb`: **Public Edition**. Generic paths for open use.

### 🚀 Quick Start
1. **Deploy GPU Environment**:
   - Open a notebook in the `notebooks/` directory.
   - Run the cells to receive your `Cloudflare Tunnel URL`.
2. **Launch Local Service**:
   - Set the environment variable: `set SD_WEBUI_URL=https://your-tunnel-url.trycloudflare.com`
   - Start the `facebox-mcp` server or the backend via `facebox/backend/main.py`.
3. **Start Generating**:
   - Ask your AI assistant: "Generate a photo of [sks person] in a suit."

---
Developed & Maintained by Antigravity AI.
