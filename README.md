# FaceBox

FaceBox 個人臉部克隆工具 — 使用 Stable Diffusion + LoRA 進行臉部克隆與圖片生成。可用來克隆人臉、訓練 LoRA、生成各種風格的人像照片。

## 核心組件

- **facebox-mcp**: 提供臉部克隆功能的 Model Context Protocol (MCP) 伺服器，讓 AI Agent 能夠直接使用臉部克隆工具。
- **notebooks**: 包含 Google Colab 筆記本，用於部署 SD WebUI、訓練 LoRA 並運行 FaceBox 服務。
- **facebox**: 核心邏輯與前端介面。

## 快速開始

### 前置要求

1. **SD WebUI**: 確保 SD WebUI (預設埠號 7860) 已啟動，且開啟了 `--api` 選項。
2. **FaceBox Backend**: 啟動 FaceBox 後端服務 (預設埠號 17494)。

### 使用方式

你可以透過 `facebox-mcp` 將此工具整合到各類 AI 助理中，或直接使用筆記本中的腳本進行批次生成。

## 注意事項

- 本地環境下請確保 GPU 驅動程式與 CUDA 環境已正確配置。
- 訓練 LoRA 建議至少使用 10-20 張高品質人臉照片。

---
Produced by Antigravity AI assistant.
