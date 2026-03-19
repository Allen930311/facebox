"""FaceBox 簡易 JSON 資料庫"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..config import DATA_DIR

DB_PATH = DATA_DIR / "facebox.json"


def _load() -> dict:
    if DB_PATH.exists():
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    return {"profiles": {}, "samples": {}, "generations": {}}


def _save(db: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Profile CRUD ──


def list_profiles() -> list[dict]:
    db = _load()
    return list(db["profiles"].values())


def get_profile(profile_id: str) -> Optional[dict]:
    db = _load()
    return db["profiles"].get(profile_id)


def save_profile(profile: dict) -> dict:
    db = _load()
    db["profiles"][profile["id"]] = profile
    _save(db)
    return profile


def delete_profile(profile_id: str) -> bool:
    db = _load()
    if profile_id not in db["profiles"]:
        return False
    del db["profiles"][profile_id]
    # 刪除相關 samples
    db["samples"] = {
        k: v for k, v in db["samples"].items() if v["profile_id"] != profile_id
    }
    # 刪除相關 generations
    db["generations"] = {
        k: v for k, v in db["generations"].items() if v["profile_id"] != profile_id
    }
    _save(db)
    return True


# ── Sample CRUD ──


def list_samples(profile_id: str) -> list[dict]:
    db = _load()
    return [s for s in db["samples"].values() if s["profile_id"] == profile_id]


def save_sample(sample: dict) -> dict:
    db = _load()
    db["samples"][sample["id"]] = sample
    # 更新 profile 的 sample_count
    pid = sample["profile_id"]
    if pid in db["profiles"]:
        count = sum(1 for s in db["samples"].values() if s["profile_id"] == pid)
        db["profiles"][pid]["sample_count"] = count
    _save(db)
    return sample


def delete_sample(sample_id: str) -> bool:
    db = _load()
    if sample_id not in db["samples"]:
        return False
    sample = db["samples"].pop(sample_id)
    pid = sample["profile_id"]
    if pid in db["profiles"]:
        count = sum(1 for s in db["samples"].values() if s["profile_id"] == pid)
        db["profiles"][pid]["sample_count"] = count
    _save(db)
    return True


# ── Generation CRUD ──


def save_generation(gen: dict) -> dict:
    db = _load()
    db["generations"][gen["id"]] = gen
    _save(db)
    return gen


def get_generation(gen_id: str) -> Optional[dict]:
    db = _load()
    return db["generations"].get(gen_id)


def list_generations(
    profile_id: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    db = _load()
    gens = list(db["generations"].values())
    if profile_id:
        gens = [g for g in gens if g["profile_id"] == profile_id]
    gens.sort(key=lambda g: g.get("created_at", ""), reverse=True)
    return gens[:limit]
