"""圖片生成 API 路由"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..config import OUTPUTS_DIR
from ..database import get_profile, save_profile, save_generation, get_generation, list_generations
from ..models import GenerateRequest, GenerationRecord
from ..services.sd_client import sd_client
from ..services.lora_trainer import lora_trainer

router = APIRouter()


@router.post("/generate")
async def api_generate(req: GenerateRequest):
    """使用人臉 LoRA 生成圖片。"""
    profile = get_profile(req.profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    if not profile.get("lora_trained"):
        raise HTTPException(
            400,
            "此 Profile 尚未訓練 LoRA 模型。請先使用 /train 訓練。"
        )

    # 建立生成紀錄
    gen = GenerationRecord(
        profile_id=req.profile_id,
        prompt=req.prompt,
        negative_prompt=req.negative_prompt,
        width=req.width,
        height=req.height,
        steps=req.steps,
        cfg_scale=req.cfg_scale,
        seed=req.seed,
        lora_weight=req.lora_weight,
        status="generating",
    )
    save_generation(gen.model_dump())

    try:
        # 取得 LoRA 名稱
        lora_path = Path(profile["lora_path"])
        lora_name = lora_path.stem  # 不含副檔名

        img_bytes, info = await sd_client.txt2img(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            width=req.width,
            height=req.height,
            steps=req.steps,
            cfg_scale=req.cfg_scale,
            seed=req.seed,
            lora_name=lora_name,
            lora_weight=req.lora_weight,
            trigger_word=profile.get("trigger_word", "sks"),
        )

        # 儲存輸出圖片
        output_dir = OUTPUTS_DIR / gen.id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.png"
        output_path.write_bytes(img_bytes)

        # 更新紀錄
        gen_dict = gen.model_dump()
        gen_dict["status"] = "completed"
        gen_dict["output_path"] = str(output_path)
        save_generation(gen_dict)

        # 更新 profile 生成次數
        profile["generation_count"] = profile.get("generation_count", 0) + 1
        profile["updated_at"] = datetime.now(timezone.utc).isoformat()
        save_profile(profile)

        return {
            "id": gen.id,
            "status": "completed",
            "output_path": str(output_path),
            "prompt": req.prompt,
        }

    except Exception as e:
        gen_dict = gen.model_dump()
        gen_dict["status"] = "failed"
        gen_dict["error"] = str(e)
        save_generation(gen_dict)
        raise HTTPException(500, f"生成失敗：{e}")


@router.post("/generate/img2img")
async def api_img2img(
    profile_id: str,
    init_image_path: str,
    prompt: str,
    negative_prompt: str = "blurry, bad quality, distorted face, ugly",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    cfg_scale: float = 7.0,
    denoising_strength: float = 0.5,
    seed: int = -1,
    lora_weight: float = 0.8,
):
    """圖生圖 — 基於參考圖片和 LoRA 生成變體。"""
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    if not profile.get("lora_trained"):
        raise HTTPException(400, "此 Profile 尚未訓練 LoRA 模型。")

    init_path = Path(init_image_path)
    if not init_path.exists():
        raise HTTPException(400, f"找不到圖片：{init_image_path}")

    gen = GenerationRecord(
        profile_id=profile_id,
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        cfg_scale=cfg_scale,
        seed=seed,
        lora_weight=lora_weight,
        status="generating",
    )
    save_generation(gen.model_dump())

    try:
        lora_path = Path(profile["lora_path"])
        lora_name = lora_path.stem

        img_bytes, info = await sd_client.img2img(
            init_image_path=init_image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            denoising_strength=denoising_strength,
            seed=seed,
            lora_name=lora_name,
            lora_weight=lora_weight,
            trigger_word=profile.get("trigger_word", "sks"),
        )

        output_dir = OUTPUTS_DIR / gen.id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.png"
        output_path.write_bytes(img_bytes)

        gen_dict = gen.model_dump()
        gen_dict["status"] = "completed"
        gen_dict["output_path"] = str(output_path)
        save_generation(gen_dict)

        profile["generation_count"] = profile.get("generation_count", 0) + 1
        save_profile(profile)

        return {
            "id": gen.id,
            "status": "completed",
            "output_path": str(output_path),
        }

    except Exception as e:
        gen_dict = gen.model_dump()
        gen_dict["status"] = "failed"
        gen_dict["error"] = str(e)
        save_generation(gen_dict)
        raise HTTPException(500, f"生成失敗：{e}")


@router.get("/output/{generation_id}")
async def api_get_output(generation_id: str):
    """取得生成的圖片。"""
    gen = get_generation(generation_id)
    if not gen:
        raise HTTPException(404, "Generation not found")
    if gen.get("status") != "completed" or not gen.get("output_path"):
        raise HTTPException(400, "圖片尚未生成完成")

    output_path = Path(gen["output_path"])
    if not output_path.exists():
        raise HTTPException(404, "圖片檔案遺失")

    return FileResponse(output_path, media_type="image/png")


@router.get("/history")
async def api_history(profile_id: str = None, limit: int = 20):
    return list_generations(profile_id=profile_id, limit=limit)


@router.get("/history/{generation_id}")
async def api_get_generation(generation_id: str):
    gen = get_generation(generation_id)
    if not gen:
        raise HTTPException(404, "Generation not found")
    return gen
