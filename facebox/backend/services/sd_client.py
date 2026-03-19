"""Stable Diffusion WebUI API 客戶端"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Optional

import httpx

from ..config import SD_WEBUI_URL

TIMEOUT = httpx.Timeout(600.0, connect=10.0)


class SDClient:
    """封裝與 SD WebUI (A1111) API 的互動。"""

    def __init__(self, base_url: str = SD_WEBUI_URL):
        self.base_url = base_url.rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=TIMEOUT)

    async def health_check(self) -> dict:
        """檢查 SD WebUI 是否運行中。"""
        async with self._client() as c:
            r = await c.get("/sdapi/v1/memory")
            r.raise_for_status()
            return r.json()

    async def get_models(self) -> list[dict]:
        """取得可用的 checkpoint 模型列表。"""
        async with self._client() as c:
            r = await c.get("/sdapi/v1/sd-models")
            r.raise_for_status()
            return r.json()

    async def get_loras(self) -> list[dict]:
        """取得可用的 LoRA 模型列表。"""
        async with self._client() as c:
            r = await c.get("/sdapi/v1/loras")
            r.raise_for_status()
            return r.json()

    async def refresh_loras(self) -> None:
        """重新載入 LoRA 列表。"""
        async with self._client() as c:
            await c.post("/sdapi/v1/refresh-loras")

    async def get_samplers(self) -> list[dict]:
        """取得可用的取樣器列表。"""
        async with self._client() as c:
            r = await c.get("/sdapi/v1/samplers")
            r.raise_for_status()
            return r.json()

    async def txt2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = -1,
        sampler_name: str = "Euler a",
        lora_name: Optional[str] = None,
        lora_weight: float = 0.8,
        trigger_word: str = "sks",
    ) -> tuple[bytes, dict]:
        """文字生成圖片。

        Returns:
            (image_bytes, info_dict)
        """
        # 如果有 LoRA，將其注入 prompt
        full_prompt = prompt
        if lora_name:
            lora_tag = f"<lora:{lora_name}:{lora_weight}>"
            # 確保 trigger word 在 prompt 中
            if trigger_word and trigger_word not in full_prompt:
                full_prompt = f"{trigger_word} {full_prompt}"
            full_prompt = f"{full_prompt} {lora_tag}"

        payload = {
            "prompt": full_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler_name": sampler_name,
        }

        async with self._client() as c:
            r = await c.post("/sdapi/v1/txt2img", json=payload)
            r.raise_for_status()
            data = r.json()

        # 解碼第一張圖片
        img_b64 = data["images"][0]
        img_bytes = base64.b64decode(img_b64)
        info = data.get("info", "{}")

        return img_bytes, {"info": info, "parameters": data.get("parameters", {})}

    async def img2img(
        self,
        init_image_path: str,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 30,
        cfg_scale: float = 7.0,
        denoising_strength: float = 0.5,
        seed: int = -1,
        sampler_name: str = "Euler a",
        lora_name: Optional[str] = None,
        lora_weight: float = 0.8,
        trigger_word: str = "sks",
    ) -> tuple[bytes, dict]:
        """圖生圖。"""
        img_path = Path(init_image_path)
        img_b64 = base64.b64encode(img_path.read_bytes()).decode()

        full_prompt = prompt
        if lora_name:
            lora_tag = f"<lora:{lora_name}:{lora_weight}>"
            if trigger_word and trigger_word not in full_prompt:
                full_prompt = f"{trigger_word} {full_prompt}"
            full_prompt = f"{full_prompt} {lora_tag}"

        payload = {
            "init_images": [img_b64],
            "prompt": full_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "denoising_strength": denoising_strength,
            "seed": seed,
            "sampler_name": sampler_name,
        }

        async with self._client() as c:
            r = await c.post("/sdapi/v1/img2img", json=payload)
            r.raise_for_status()
            data = r.json()

        img_bytes = base64.b64decode(data["images"][0])
        info = data.get("info", "{}")
        return img_bytes, {"info": info, "parameters": data.get("parameters", {})}

    async def get_progress(self) -> dict:
        """取得目前生成進度。"""
        async with self._client() as c:
            r = await c.get("/sdapi/v1/progress")
            r.raise_for_status()
            return r.json()


# 全域實例
sd_client = SDClient()
