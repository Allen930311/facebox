"""LoRA 訓練服務 — 使用 kohya-ss/sd-scripts 進行臉部 LoRA 訓練"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from ..config import LORA_DIR, LORA_DEFAULTS, PROFILES_DIR


class LoraTrainer:
    """管理 LoRA 訓練任務。"""

    def __init__(self):
        self._training_tasks: dict[str, dict] = {}

    def get_training_status(self, profile_id: str) -> Optional[dict]:
        return self._training_tasks.get(profile_id)

    async def train(
        self,
        profile_id: str,
        profile_name: str,
        trigger_word: str = "sks",
        max_train_steps: int = 1500,
        learning_rate: float = 1e-4,
        resolution: int = 512,
        network_rank: int = 32,
        network_alpha: int = 16,
        base_model: str = "",
    ) -> dict:
        """啟動 LoRA 訓練。

        訓練圖片來源: PROFILES_DIR / profile_id / samples/
        輸出 LoRA 至: LORA_DIR / {profile_name}.safetensors
        """
        samples_dir = PROFILES_DIR / profile_id / "samples"
        if not samples_dir.exists() or not list(samples_dir.glob("*")):
            return {"error": "沒有找到訓練圖片，請先上傳參考照片。"}

        output_name = f"facebox_{profile_name}_{profile_id}"
        output_dir = LORA_DIR

        # 訓練設定
        config = {
            "profile_id": profile_id,
            "trigger_word": trigger_word,
            "samples_dir": str(samples_dir),
            "output_dir": str(output_dir),
            "output_name": output_name,
            "max_train_steps": max_train_steps,
            "learning_rate": learning_rate,
            "resolution": resolution,
            "network_rank": network_rank,
            "network_alpha": network_alpha,
            "base_model": base_model,
        }

        self._training_tasks[profile_id] = {
            "status": "preparing",
            "config": config,
            "progress": 0,
        }

        # 準備訓練資料目錄結構 (kohya 格式)
        train_data_dir = PROFILES_DIR / profile_id / "train_data"
        instance_dir = train_data_dir / f"1_{trigger_word} person"
        instance_dir.mkdir(parents=True, exist_ok=True)

        # 複製/連結訓練圖片到 kohya 格式目錄
        import shutil
        for img in samples_dir.iterdir():
            if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
                dest = instance_dir / img.name
                if not dest.exists():
                    shutil.copy2(img, dest)

        # 寫入訓練配置檔
        config_path = PROFILES_DIR / profile_id / "train_config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))

        self._training_tasks[profile_id]["status"] = "ready"
        self._training_tasks[profile_id]["config_path"] = str(config_path)
        self._training_tasks[profile_id]["train_data_dir"] = str(train_data_dir)
        self._training_tasks[profile_id]["expected_output"] = str(
            output_dir / f"{output_name}.safetensors"
        )

        return {
            "status": "ready",
            "message": (
                f"訓練資料已準備完成。\n"
                f"訓練圖片: {sum(1 for _ in instance_dir.iterdir())} 張\n"
                f"輸出名稱: {output_name}\n"
                f"配置檔: {config_path}\n\n"
                f"請使用 kohya_ss GUI 或命令列工具執行訓練：\n"
                f"  訓練資料目錄: {train_data_dir}\n"
                f"  輸出目錄: {output_dir}\n"
                f"  輸出名稱: {output_name}\n"
                f"  Trigger word: {trigger_word}\n"
                f"  步數: {max_train_steps}\n"
                f"  學習率: {learning_rate}\n"
                f"  Rank: {network_rank}\n"
                f"  Alpha: {network_alpha}"
            ),
            "config": config,
        }

    def check_lora_exists(self, profile_id: str, profile_name: str) -> Optional[Path]:
        """檢查某個 profile 的 LoRA 是否已訓練完成。"""
        pattern = f"facebox_{profile_name}_{profile_id}"
        for f in LORA_DIR.iterdir():
            if f.stem.startswith(pattern) and f.suffix == ".safetensors":
                return f
        return None

    def list_trained_loras(self) -> list[dict]:
        """列出所有已訓練的 LoRA 模型。"""
        loras = []
        for f in LORA_DIR.iterdir():
            if f.suffix == ".safetensors":
                size_mb = f.stat().st_size / (1024 * 1024)
                loras.append({
                    "name": f.stem,
                    "path": str(f),
                    "size_mb": round(size_mb, 1),
                })
        return loras


# 全域實例
lora_trainer = LoraTrainer()
