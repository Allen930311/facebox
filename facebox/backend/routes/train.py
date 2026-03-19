"""LoRA 訓練 API 路由"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..config import LORA_DIR
from ..database import get_profile, save_profile
from ..models import TrainLoraRequest
from ..services.lora_trainer import lora_trainer

router = APIRouter()


@router.post("/train")
async def api_train_lora(req: TrainLoraRequest):
    """準備 LoRA 訓練資料並產生訓練配置。"""
    profile = get_profile(req.profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    result = await lora_trainer.train(
        profile_id=req.profile_id,
        profile_name=profile["name"],
        trigger_word=profile.get("trigger_word", "sks"),
        max_train_steps=req.max_train_steps,
        learning_rate=req.learning_rate,
        resolution=req.resolution,
        network_rank=req.network_rank,
        network_alpha=req.network_alpha,
    )

    if "error" in result:
        raise HTTPException(400, result["error"])

    return result


@router.post("/train/{profile_id}/mark-complete")
async def api_mark_training_complete(profile_id: str, lora_path: str = ""):
    """手動標記訓練完成，並指定 LoRA 檔案路徑。"""
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    # 自動搜尋或使用指定路徑
    if lora_path:
        lp = Path(lora_path)
    else:
        lp = lora_trainer.check_lora_exists(profile_id, profile["name"])

    if not lp or not lp.exists():
        raise HTTPException(
            400,
            f"找不到 LoRA 檔案。請確認訓練已完成，或手動指定 lora_path。"
            f"\n搜尋目錄：{LORA_DIR}"
        )

    profile["lora_trained"] = True
    profile["lora_path"] = str(lp)
    profile["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_profile(profile)

    return {
        "ok": True,
        "message": f"LoRA 已標記完成！路徑：{lp}",
        "profile": profile,
    }


@router.get("/train/status/{profile_id}")
async def api_training_status(profile_id: str):
    """查詢訓練狀態。"""
    status = lora_trainer.get_training_status(profile_id)
    if not status:
        return {"status": "no_training", "message": "沒有進行中的訓練任務。"}
    return status


@router.get("/loras")
async def api_list_loras():
    """列出所有已訓練的 LoRA 模型。"""
    return lora_trainer.list_trained_loras()
