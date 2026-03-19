"""Profile 相關 API 路由"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from ..config import PROFILES_DIR
from ..database import (
    list_profiles,
    get_profile,
    save_profile,
    delete_profile,
    list_samples,
    save_sample,
    delete_sample,
)
from ..models import FaceProfile, FaceSample, CreateProfileRequest

router = APIRouter()


# ── Profile CRUD ──


@router.get("/profiles")
async def api_list_profiles():
    return list_profiles()


@router.post("/profiles")
async def api_create_profile(req: CreateProfileRequest):
    profile = FaceProfile(
        name=req.name,
        description=req.description,
        trigger_word=req.trigger_word,
    )
    return save_profile(profile.model_dump())


@router.get("/profiles/{profile_id}")
async def api_get_profile(profile_id: str):
    p = get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")
    return p


@router.delete("/profiles/{profile_id}")
async def api_delete_profile(profile_id: str):
    # 刪除資料目錄
    profile_dir = PROFILES_DIR / profile_id
    if profile_dir.exists():
        shutil.rmtree(profile_dir)
    if not delete_profile(profile_id):
        raise HTTPException(404, "Profile not found")
    return {"ok": True}


# ── Samples (參考照片) ──


@router.get("/profiles/{profile_id}/samples")
async def api_list_samples(profile_id: str):
    p = get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")
    return list_samples(profile_id)


@router.post("/profiles/{profile_id}/samples")
async def api_upload_sample(
    profile_id: str,
    file: UploadFile = File(...),
    caption: str = Form(""),
):
    p = get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")

    # 儲存檔案
    samples_dir = PROFILES_DIR / profile_id / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # 保留原始副檔名
    ext = Path(file.filename).suffix or ".jpg"
    sample = FaceSample(
        profile_id=profile_id,
        filename="",
        caption=caption,
    )
    filename = f"{sample.id}{ext}"
    sample.filename = filename

    dest = samples_dir / filename
    content = await file.read()
    dest.write_bytes(content)

    return save_sample(sample.model_dump())


@router.post("/profiles/{profile_id}/samples/batch")
async def api_upload_samples_from_paths(
    profile_id: str,
    paths: list[str],
):
    """批次從本地路徑上傳參考照片。"""
    p = get_profile(profile_id)
    if not p:
        raise HTTPException(404, "Profile not found")

    samples_dir = PROFILES_DIR / profile_id / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for path_str in paths:
        src = Path(path_str)
        if not src.exists():
            results.append({"path": path_str, "error": "File not found"})
            continue

        ext = src.suffix or ".jpg"
        sample = FaceSample(
            profile_id=profile_id,
            filename="",
            caption=src.stem,
        )
        filename = f"{sample.id}{ext}"
        sample.filename = filename
        dest = samples_dir / filename
        shutil.copy2(src, dest)
        saved = save_sample(sample.model_dump())
        results.append({"path": path_str, "sample": saved})

    return {"uploaded": len([r for r in results if "sample" in r]), "results": results}


@router.delete("/profiles/{profile_id}/samples/{sample_id}")
async def api_delete_sample(profile_id: str, sample_id: str):
    samples = list_samples(profile_id)
    sample = next((s for s in samples if s["id"] == sample_id), None)
    if not sample:
        raise HTTPException(404, "Sample not found")

    # 刪除檔案
    fpath = PROFILES_DIR / profile_id / "samples" / sample["filename"]
    if fpath.exists():
        fpath.unlink()

    delete_sample(sample_id)
    return {"ok": True}
