"""FaceBox 資料模型"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


# ── Face Profile ──


class FaceProfile(BaseModel):
    id: str = Field(default_factory=_new_id)
    name: str
    description: str = ""
    trigger_word: str = "sks"
    sample_count: int = 0
    lora_trained: bool = False
    lora_path: Optional[str] = None
    generation_count: int = 0
    created_at: str = Field(default_factory=_utcnow)
    updated_at: str = Field(default_factory=_utcnow)


class FaceSample(BaseModel):
    id: str = Field(default_factory=_new_id)
    profile_id: str
    filename: str
    caption: str = ""
    created_at: str = Field(default_factory=_utcnow)


class GenerationRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    profile_id: str
    prompt: str
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    steps: int = 30
    cfg_scale: float = 7.0
    seed: int = -1
    lora_weight: float = 0.8
    status: str = "pending"  # pending / generating / completed / failed
    output_path: Optional[str] = None
    error: Optional[str] = None
    created_at: str = Field(default_factory=_utcnow)


# ── API Request / Response ──


class CreateProfileRequest(BaseModel):
    name: str
    description: str = ""
    trigger_word: str = "sks"


class GenerateRequest(BaseModel):
    profile_id: str
    prompt: str
    negative_prompt: str = "blurry, bad quality, distorted face, ugly"
    width: int = 512
    height: int = 512
    steps: int = 30
    cfg_scale: float = 7.0
    seed: int = -1
    lora_weight: float = 0.8


class TrainLoraRequest(BaseModel):
    profile_id: str
    max_train_steps: int = 1500
    learning_rate: float = 1e-4
    resolution: int = 512
    network_rank: int = 32
    network_alpha: int = 16
