"""FaceBox 設定檔"""

import os
from pathlib import Path

# ── 伺服器 ──
HOST = os.getenv("FACEBOX_HOST", "127.0.0.1")
PORT = int(os.getenv("FACEBOX_PORT", "17494"))

# ── SD WebUI 連線 ──
SD_WEBUI_URL = os.getenv("SD_WEBUI_URL", "http://127.0.0.1:7860")

# ── 資料目錄 ──
DATA_DIR = Path(os.getenv(
    "FACEBOX_DATA_DIR",
    Path(__file__).parent.parent / "data"
))
PROFILES_DIR = DATA_DIR / "profiles"
OUTPUTS_DIR = DATA_DIR / "outputs"
LORA_DIR = DATA_DIR / "lora_models"

# 確保目錄存在
for d in [PROFILES_DIR, OUTPUTS_DIR, LORA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── LoRA 訓練預設 ──
LORA_DEFAULTS = {
    "resolution": 512,
    "train_batch_size": 1,
    "max_train_steps": 1500,
    "learning_rate": 1e-4,
    "network_rank": 32,
    "network_alpha": 16,
    "instance_prompt": "photo of sks person",
    "class_prompt": "photo of a person",
}

# ── 生成預設 ──
GENERATION_DEFAULTS = {
    "width": 512,
    "height": 512,
    "steps": 30,
    "cfg_scale": 7.0,
    "sampler_name": "Euler a",
    "checkpoint": "",  # 使用 SD WebUI 當前載入的模型
}
