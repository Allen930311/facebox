---
name: facebox
description: "FaceBox 臉部克隆與人像生成技能 — 封裝 FaceBox MCP 工具，提供完整的臉部克隆工作流：建立 Profile、上傳參考照片、在 Colab GPU 訓練 LoRA、用 SD WebUI 生成各種風格人像。觸發範例：「幫我克隆一張臉」「生成一張專業頭像」「列出我的人臉 Profile」「訓練 LoRA」「用 XXX 的臉生成照片」"
---

# FaceBox — 臉部克隆與人像生成

本技能封裝 FaceBox MCP 工具，提供從臉部克隆到圖片生成的完整工作流。

## 架構概覽

```
Colab (T4 GPU)                         本地
┌─────────────────────┐  Cloudflare  ┌──────────────────┐
│ SD WebUI :7860 --api│◄────────────►│ FaceBox :17494   │
│ kohya-ss (LoRA)     │   Tunnel     │ MCP Server       │
└─────────────────────┘              └──────────────────┘
```

- **FaceBox 後端**: FastAPI (port 17494)，管理 Profile、呼叫 SD WebUI API
- **SD WebUI**: A1111 (port 7860)，可在本地或 Colab GPU 執行
- **MCP Server**: 將 FaceBox API 暴露為 Claude Code 可調用的工具

## 前置檢查

每次操作前先呼叫 `facebox_status` 確認：
1. FaceBox 後端已啟動 (port 17494)
2. SD WebUI 已連線 (port 7860)

若未啟動：
```bash
# 啟動 FaceBox 後端（在專案根目錄下執行）
cd facebox
pip install -r backend/requirements.txt
python -m backend.main

# 若使用 Colab GPU，先設定 Tunnel URL
# Windows:  set SD_WEBUI_URL=https://xxx.trycloudflare.com
# Linux:    export SD_WEBUI_URL=https://xxx.trycloudflare.com
```

## MCP 設定

在 Claude Code `settings.json` 或 `.mcp.json` 中加入：

```json
{
  "mcpServers": {
    "facebox": {
      "command": "python",
      "args": ["<PROJECT_ROOT>/facebox-mcp/server.py"]
    }
  }
}
```

將 `<PROJECT_ROOT>` 替換為實際專案路徑。

## 核心工作流

### 流程 A：一鍵克隆（最快）

當用戶說「幫我克隆一張臉」「建立新的人臉角色」：

1. 確認必要資訊：
   - **名稱**（如 "Allen"）
   - **照片路徑**（10-20 張，含不同角度、表情、光線）
   - **觸發詞**（預設 `sks`）
2. 呼叫 `facebox_clone_face(name, photo_paths, description, trigger_word)`
   - 自動完成：建立 Profile → 上傳照片 → 準備訓練配置
3. 引導用戶執行 LoRA 訓練（見流程 C）
4. 訓練完成後呼叫 `facebox_mark_training_complete(profile_id)`

### 流程 B：生成人像圖片

當用戶說「用 XXX 生成照片」「生成專業頭像」：

1. `facebox_list_profiles` 找到目標 Profile
2. 確認該 Profile 已訓練 LoRA（`lora_trained: true`）
3. 組合 prompt，呼叫：
   ```
   facebox_generate(
     profile_id=<id>,
     prompt="photo of sks person ...",
     negative_prompt="blurry, bad quality, distorted face, ugly",
     lora_weight=0.8
   )
   ```
4. 可用 `facebox_download_image` 下載到指定路徑

### 流程 C：LoRA 訓練

FaceBox 準備訓練資料後，實際訓練需在 GPU 環境執行：

**方法 1：Colab GPU（推薦，免費）**
- 使用 `notebooks/sd_webui_colab.ipynb`
- Cell 1-6 啟動 SD WebUI + Cloudflare Tunnel
- Cell 7-9 安裝 kohya-ss + 上傳照片 + 訓練
- Cell 10 部署 LoRA 到 SD WebUI

**方法 2：本地 GPU**
- 需要 kohya-ss/sd-scripts
- `facebox_train_lora(profile_id)` 產生配置後，用 kohya 執行訓練

訓練完成後：`facebox_mark_training_complete(profile_id, lora_path)`

### 流程 D：管理 Profile

| 用戶意圖 | 動作 |
|---|---|
| 「列出我的臉」 | `facebox_list_profiles` |
| 「看 XXX 的詳細資訊」 | `facebox_get_profile(id)` |
| 「刪除 XXX」 | `facebox_delete_profile(id)` |
| 「追加照片」 | `facebox_add_samples(id, paths)` |
| 「生成歷史」 | `facebox_history(profile_id)` |
| 「有哪些模型」 | `facebox_list_models` / `facebox_list_loras` |

## Prompt 撰寫指南

### 基本結構

```
photo of {trigger_word} person, [場景/服裝/風格], [品質詞]
```

### 風格範例

| 風格 | Prompt |
|---|---|
| 專業頭像 | `photo of sks person in a business suit, professional headshot, studio lighting, sharp focus` |
| 休閒生活 | `photo of sks person in casual clothes, outdoor cafe, natural lighting, candid` |
| 藝術風格 | `portrait of sks person, oil painting style, dramatic lighting, renaissance` |
| 證件照 | `photo of sks person, ID photo, white background, frontal, neutral expression` |

### 關鍵參數

| 參數 | 預設 | 建議範圍 | 說明 |
|---|---|---|---|
| `lora_weight` | 0.8 | 0.6-1.0 | 越高越像本人，太高可能失真 |
| `cfg_scale` | 7.0 | 5-12 | 越高越忠於 prompt，太高會過飽和 |
| `steps` | 30 | 20-50 | 越多越精細，但更慢 |
| `seed` | -1 | 任意正整數 | 固定 seed 可復現同一構圖 |
| `width/height` | 512 | 512/768 | SD 1.5 建議不超過 768 |

### Negative Prompt 建議

```
blurry, bad quality, distorted face, ugly, deformed, disfigured, extra limbs, bad anatomy, watermark, text
```

## LoRA 訓練參數指南

| 參數 | 預設 | 說明 |
|---|---|---|
| `max_train_steps` | 1500 | 10-20 張照片用 1500，照片多可加到 2000-3000 |
| `learning_rate` | 1e-4 | 過高易過擬合，過低欠擬合 |
| `resolution` | 512 | Colab T4 建議 384-512 避免 OOM |
| `network_rank` | 32 | 越高細節越多但檔案越大 |
| `network_alpha` | 16 | 通常為 rank 的一半 |

## 照片上傳建議

- **數量**：10-20 張（少於 5 張效果差，多於 30 張需加步數）
- **角度**：正面、左右 45 度、側面各幾張
- **表情**：自然微笑、嚴肅、大笑等
- **光線**：室內、室外、不同光源
- **清晰度**：高解析度、臉部清晰、無遮擋
- **格式**：JPG / PNG / WebP

## 專案目錄結構

```
FaceBox/
├── facebox/                  # 核心專案
│   ├── backend/              # FastAPI 後端 (port 17494)
│   │   ├── main.py           # 入口
│   │   ├── config.py         # 設定（可用環境變數覆蓋）
│   │   ├── models.py         # Pydantic 資料模型
│   │   ├── database/         # JSON 資料庫
│   │   ├── routes/           # API 路由 (profiles, generate, train)
│   │   └── services/         # SD WebUI 客戶端 & LoRA 訓練
│   └── data/                 # 運行時資料（自動建立）
│       ├── profiles/         # 人臉 Profile（照片、訓練配置）
│       ├── outputs/          # 生成的圖片
│       └── lora_models/      # 訓練完成的 LoRA 模型
├── facebox-mcp/              # MCP Server（Claude Code 整合）
│   └── server.py
├── notebooks/
│   └── sd_webui_colab.ipynb  # Colab GPU 訓練 Notebook
└── skill/
    └── SKILL.md              # 本技能檔案
```

## 環境變數

| 變數 | 預設值 | 說明 |
|---|---|---|
| `FACEBOX_HOST` | `127.0.0.1` | 後端監聽地址 |
| `FACEBOX_PORT` | `17494` | 後端 port |
| `SD_WEBUI_URL` | `http://127.0.0.1:7860` | SD WebUI 位址（Colab 時改為 Tunnel URL） |
| `FACEBOX_DATA_DIR` | `facebox/data` | 資料儲存目錄 |

## 注意事項

- Colab 免費版有使用時限，訓練前確認 GPU 分配
- Cloudflare Tunnel URL 每次啟動都會變，需重新設定 `SD_WEBUI_URL`
- LoRA 訓練完成後要呼叫 `facebox_mark_training_complete` 才能用於生成
- 生成時 prompt 中必須包含 trigger word（`sks` 或自訂詞），MCP 會自動注入
- 若使用 Colab，訓練好的 LoRA 需部署到 SD WebUI 的 `models/Lora/` 目錄（或開啟 Drive 持久化自動連結）
