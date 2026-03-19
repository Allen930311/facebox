"""
FaceBox MCP Server — 個人臉部克隆工具
將本地 FaceBox (Stable Diffusion + LoRA) 引擎暴露為 Claude Code 可調用的 MCP 工具。

啟動方式: python server.py
前置條件: FaceBox 後端需先啟動 (python -m backend.main)
          SD WebUI (A1111) 需先啟動 (port 7860)
"""

import asyncio
import json
import os
import sys
import base64
from pathlib import Path
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ── 設定 ─────────────────────────────────────────────
FACEBOX_BASE_URL = os.getenv("FACEBOX_URL", "http://127.0.0.1:17494")
FACEBOX_PROJECT = Path(os.getenv(
    "FACEBOX_PROJECT",
    r"c:\Users\Allen\OneDrive\Desktop\FaceBox\facebox"
))
TIMEOUT = httpx.Timeout(600.0, connect=10.0)

mcp = FastMCP(
    "facebox",
    instructions=(
        "FaceBox 個人臉部克隆工具 — 使用 Stable Diffusion + LoRA 進行臉部克隆與圖片生成。"
        "可用來克隆人臉、訓練 LoRA、生成各種風格的人像照片。"
        "使用前請確保 FaceBox 後端 (port 17494) 和 SD WebUI (port 7860) 已啟動。"
    ),
)


# ── 工具函式 ─────────────────────────────────────────


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=FACEBOX_BASE_URL, timeout=TIMEOUT)


# ─── 健康檢查 ───


@mcp.tool()
async def facebox_status() -> str:
    """檢查 FaceBox 後端與 SD WebUI 是否正在運行。"""
    try:
        async with _client() as c:
            r = await c.get("/health")
            r.raise_for_status()
            data = r.json()
            sd = data.get("sd_webui", {})
            sd_status = "✅ 已連線" if sd.get("connected") else "❌ 未連線"
            return (
                f"FaceBox 後端: ✅ 運行中 (port {data.get('port', 17494)})\n"
                f"SD WebUI: {sd_status}\n\n"
                + json.dumps(data, ensure_ascii=False, indent=2)
            )
    except httpx.ConnectError:
        return (
            "❌ FaceBox 後端未啟動。\n"
            f"請先在 {FACEBOX_PROJECT} 目錄執行：\n"
            "  python -m backend.main\n\n"
            "同時確保 SD WebUI (A1111) 已啟動在 port 7860。"
        )
    except Exception as e:
        return f"❌ 連線錯誤：{e}"


# ─── Face Profile 管理 ───


@mcp.tool()
async def facebox_list_profiles() -> str:
    """列出所有已建立的臉部 Profile（人臉角色），包含名稱、樣本數、LoRA 狀態。"""
    async with _client() as c:
        r = await c.get("/profiles")
        r.raise_for_status()
        profiles = r.json()
        if not profiles:
            return "目前沒有任何 Face Profile。使用 facebox_create_profile 建立一個。"
        lines = []
        for p in profiles:
            lora_icon = "✅" if p.get("lora_trained") else "⏳"
            lines.append(
                f"• **{p['name']}** (id: `{p['id']}`)\n"
                f"  Trigger: {p.get('trigger_word', 'sks')} | "
                f"  樣本: {p.get('sample_count', 0)} 張 | "
                f"  LoRA: {lora_icon} | "
                f"  生成: {p.get('generation_count', 0)} 次"
            )
        return "\n".join(lines)


@mcp.tool()
async def facebox_create_profile(
    name: str,
    description: str = "",
    trigger_word: str = "sks",
) -> str:
    """建立新的臉部 Profile（人臉角色）。

    Args:
        name: 人臉名稱（如 "Allen"、"Model A"）
        description: 描述此人臉的特色
        trigger_word: LoRA 觸發詞（預設 sks，訓練時會用到）
    """
    async with _client() as c:
        r = await c.post("/profiles", json={
            "name": name,
            "description": description,
            "trigger_word": trigger_word,
        })
        r.raise_for_status()
        p = r.json()
        return (
            f"✅ Face Profile 已建立！\n"
            f"名稱: {p['name']}\n"
            f"ID: `{p['id']}`\n"
            f"Trigger word: {p.get('trigger_word', 'sks')}\n\n"
            f"下一步：使用 facebox_add_samples 上傳 10-20 張參考照片。"
        )


@mcp.tool()
async def facebox_get_profile(profile_id: str) -> str:
    """取得特定 Face Profile 的詳細資訊。

    Args:
        profile_id: Profile ID
    """
    async with _client() as c:
        r = await c.get(f"/profiles/{profile_id}")
        r.raise_for_status()
        p = r.json()

        r2 = await c.get(f"/profiles/{profile_id}/samples")
        r2.raise_for_status()
        samples = r2.json()

        lora_status = "✅ 已訓練" if p.get("lora_trained") else "⏳ 未訓練"
        lines = [
            f"**{p['name']}** (id: `{p['id']}`)",
            f"描述: {p.get('description') or '無'}",
            f"Trigger word: {p.get('trigger_word', 'sks')}",
            f"樣本數: {p.get('sample_count', 0)} 張",
            f"LoRA 狀態: {lora_status}",
            f"生成次數: {p.get('generation_count', 0)}",
        ]
        if p.get("lora_path"):
            lines.append(f"LoRA 路徑: {p['lora_path']}")
        if samples:
            lines.append("\n**參考照片：**")
            for s in samples:
                lines.append(f"  • `{s['id']}` — {s.get('caption', s['filename'])}")
        return "\n".join(lines)


@mcp.tool()
async def facebox_delete_profile(profile_id: str) -> str:
    """刪除 Face Profile 及其所有樣本和訓練資料。

    Args:
        profile_id: Profile ID
    """
    async with _client() as c:
        r = await c.delete(f"/profiles/{profile_id}")
        r.raise_for_status()
        return f"✅ Profile `{profile_id}` 已刪除。"


# ─── 參考照片管理 ───


@mcp.tool()
async def facebox_add_samples(
    profile_id: str,
    photo_paths: str,
) -> str:
    """批次上傳參考照片至 Profile（用於 LoRA 訓練）。

    建議上傳 10-20 張高品質照片，包含不同角度、表情、光線。

    Args:
        profile_id: Profile ID
        photo_paths: 照片路徑列表，以換行或逗號分隔
            例如: "C:/photos/face1.jpg, C:/photos/face2.jpg"
            或: "C:/photos/face1.jpg\\nC:/photos/face2.jpg"
    """
    # 解析路徑
    paths = []
    for line in photo_paths.replace(",", "\n").split("\n"):
        p = line.strip()
        if p:
            paths.append(p)

    if not paths:
        return "❌ 未提供任何照片路徑。"

    async with _client() as c:
        r = await c.post(
            f"/profiles/{profile_id}/samples/batch",
            json=paths,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        r.raise_for_status()
        data = r.json()
        uploaded = data.get("uploaded", 0)
        results = data.get("results", [])
        errors = [r for r in results if "error" in r]

        msg = f"✅ 成功上傳 {uploaded} 張照片！"
        if errors:
            msg += f"\n⚠️ {len(errors)} 張失敗："
            for e in errors:
                msg += f"\n  • {e['path']}: {e['error']}"

        msg += f"\n\n下一步：累積足夠照片後 (建議 10-20 張)，使用 facebox_train_lora 開始訓練。"
        return msg


# ─── LoRA 訓練 ───


@mcp.tool()
async def facebox_train_lora(
    profile_id: str,
    max_train_steps: int = 1500,
    learning_rate: float = 1e-4,
    resolution: int = 512,
    network_rank: int = 32,
    network_alpha: int = 16,
) -> str:
    """準備 LoRA 訓練資料。會產生 kohya-ss 格式的訓練配置。

    Args:
        profile_id: Profile ID
        max_train_steps: 最大訓練步數（預設 1500）
        learning_rate: 學習率（預設 1e-4）
        resolution: 訓練解析度（預設 512）
        network_rank: LoRA Rank（預設 32）
        network_alpha: LoRA Alpha（預設 16）
    """
    async with _client() as c:
        r = await c.post("/train", json={
            "profile_id": profile_id,
            "max_train_steps": max_train_steps,
            "learning_rate": learning_rate,
            "resolution": resolution,
            "network_rank": network_rank,
            "network_alpha": network_alpha,
        })
        r.raise_for_status()
        data = r.json()
        return data.get("message", json.dumps(data, ensure_ascii=False, indent=2))


@mcp.tool()
async def facebox_mark_training_complete(
    profile_id: str,
    lora_path: str = "",
) -> str:
    """標記 LoRA 訓練完成。訓練完成後，呼叫此工具告訴 FaceBox LoRA 在哪裡。

    Args:
        profile_id: Profile ID
        lora_path: LoRA safetensors 檔案路徑（若為空則自動搜尋）
    """
    async with _client() as c:
        r = await c.post(
            f"/train/{profile_id}/mark-complete",
            params={"lora_path": lora_path} if lora_path else {},
        )
        r.raise_for_status()
        data = r.json()
        return data.get("message", json.dumps(data, ensure_ascii=False, indent=2))


@mcp.tool()
async def facebox_list_loras() -> str:
    """列出所有已訓練的 LoRA 模型。"""
    async with _client() as c:
        r = await c.get("/loras")
        r.raise_for_status()
        loras = r.json()
        if not loras:
            return "目前沒有任何已訓練的 LoRA 模型。"
        lines = []
        for l in loras:
            lines.append(
                f"• **{l['name']}** — {l.get('size_mb', '?')} MB\n"
                f"  路徑: {l['path']}"
            )
        return "\n".join(lines)


# ─── 圖片生成 ───


@mcp.tool()
async def facebox_generate(
    profile_id: str,
    prompt: str,
    negative_prompt: str = "blurry, bad quality, distorted face, ugly",
    width: int = 512,
    height: int = 512,
    steps: int = 30,
    cfg_scale: float = 7.0,
    seed: int = -1,
    lora_weight: float = 0.8,
    output_path: Optional[str] = None,
) -> str:
    """使用已訓練的臉部 LoRA 生成人像圖片。

    Args:
        profile_id: 人臉 Profile ID
        prompt: 生成提示詞（例如 "photo of sks person in a suit, professional headshot"）
        negative_prompt: 反向提示詞
        width: 圖片寬度
        height: 圖片高度
        steps: 生成步數
        cfg_scale: CFG 引導強度
        seed: 隨機種子（-1 為隨機）
        lora_weight: LoRA 權重（0.0-1.0）
        output_path: 可選，將圖片額外複製到此路徑
    """
    async with _client() as c:
        r = await c.post("/generate", json={
            "profile_id": profile_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "lora_weight": lora_weight,
        })
        r.raise_for_status()
        data = r.json()
        gen_id = data["id"]

        # 如果指定了 output_path，下載圖片
        if output_path and data.get("status") == "completed":
            r2 = await c.get(f"/output/{gen_id}")
            r2.raise_for_status()
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(r2.content)

        result = (
            f"✅ 圖片生成完成！\n"
            f"Generation ID: `{gen_id}`\n"
            f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"原始路徑: {data.get('output_path', '未知')}"
        )
        if output_path:
            result += f"\n複製至: {output_path}"
        result += f"\n\n使用 facebox_download_image 可下載圖片。"
        return result


@mcp.tool()
async def facebox_download_image(
    generation_id: str,
    output_path: str,
) -> str:
    """下載已生成的圖片至指定路徑。

    Args:
        generation_id: Generation ID
        output_path: 輸出路徑（含檔名，如 C:/output/face.png）
    """
    async with _client() as c:
        r = await c.get(f"/output/{generation_id}")
        r.raise_for_status()
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        size_kb = len(r.content) / 1024
        return f"✅ 圖片已下載至：{out}（{size_kb:.0f} KB）"


# ─── 歷史紀錄 ───


@mcp.tool()
async def facebox_history(
    profile_id: Optional[str] = None,
    limit: int = 10,
) -> str:
    """查看圖片生成歷史紀錄。

    Args:
        profile_id: 篩選特定 Profile 的紀錄
        limit: 回傳筆數上限（預設 10）
    """
    params = {"limit": limit}
    if profile_id:
        params["profile_id"] = profile_id

    async with _client() as c:
        r = await c.get("/history", params=params)
        r.raise_for_status()
        items = r.json()
        if not items:
            return "沒有找到任何生成紀錄。"

        lines = []
        for g in items[:limit]:
            prompt_preview = (g.get("prompt", "")[:60] + "...") if len(g.get("prompt", "")) > 60 else g.get("prompt", "")
            lines.append(
                f"• `{g['id']}` [{g.get('status', '?')}]\n"
                f"  Profile: {g.get('profile_id', '?')}\n"
                f"  \"{prompt_preview}\""
            )
        return "\n\n".join(lines)


# ─── SD WebUI 資訊 ───


@mcp.tool()
async def facebox_list_models() -> str:
    """列出 SD WebUI 可用的 checkpoint 模型。"""
    async with _client() as c:
        r = await c.get("/sd/models")
        r.raise_for_status()
        models = r.json()
        if isinstance(models, dict) and "error" in models:
            return f"❌ {models['error']}"
        if not models:
            return "沒有找到任何模型。請確認 SD WebUI 已啟動。"
        lines = []
        for m in models:
            lines.append(f"• **{m.get('model_name', m.get('title', '?'))}**")
        return "\n".join(lines)


@mcp.tool()
async def facebox_list_samplers() -> str:
    """列出 SD WebUI 可用的取樣器。"""
    async with _client() as c:
        r = await c.get("/sd/samplers")
        r.raise_for_status()
        samplers = r.json()
        if isinstance(samplers, dict) and "error" in samplers:
            return f"❌ {samplers['error']}"
        lines = [f"• {s.get('name', '?')}" for s in samplers]
        return "\n".join(lines)


# ─── 一鍵克隆 ───


@mcp.tool()
async def facebox_clone_face(
    name: str,
    photo_paths: str,
    description: str = "",
    trigger_word: str = "sks",
) -> str:
    """一鍵開始臉部克隆：建立 Profile + 上傳參考照片 + 準備 LoRA 訓練配置。

    Args:
        name: 人臉名稱（如 "Allen"）
        photo_paths: 參考照片路徑，以換行或逗號分隔（建議 10-20 張）
        description: 人臉描述
        trigger_word: LoRA 觸發詞（預設 sks）
    """
    steps_log = []

    async with _client() as c:
        # Step 1: 建立 Profile
        r1 = await c.post("/profiles", json={
            "name": name,
            "description": description,
            "trigger_word": trigger_word,
        })
        r1.raise_for_status()
        profile = r1.json()
        pid = profile["id"]
        steps_log.append(f"✅ Profile 已建立 — ID: `{pid}`")

        # Step 2: 上傳照片
        paths = []
        for line in photo_paths.replace(",", "\n").split("\n"):
            p = line.strip()
            if p:
                paths.append(p)

        if paths:
            r2 = await c.post(
                f"/profiles/{pid}/samples/batch",
                json=paths,
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
            r2.raise_for_status()
            upload_data = r2.json()
            uploaded = upload_data.get("uploaded", 0)
            steps_log.append(f"✅ 已上傳 {uploaded} 張參考照片")
        else:
            steps_log.append("⚠️ 未提供照片路徑，請稍後手動上傳")

        # Step 3: 準備訓練
        if paths and len(paths) >= 5:
            r3 = await c.post("/train", json={"profile_id": pid})
            r3.raise_for_status()
            train_data = r3.json()
            steps_log.append("✅ LoRA 訓練資料已準備完成")
        else:
            steps_log.append(f"⚠️ 照片數量不足（建議至少 10 張），請繼續上傳後再訓練")

    return (
        f"🎭 臉部克隆流程已啟動！\n\n"
        f"**Profile:** {name}\n"
        f"**ID:** `{pid}`\n"
        f"**Trigger word:** {trigger_word}\n\n"
        + "\n".join(steps_log)
        + "\n\n**後續步驟：**\n"
        f"1. 使用 kohya-ss 訓練 LoRA\n"
        f"2. 訓練完成後呼叫 facebox_mark_training_complete\n"
        f"3. 使用 facebox_generate 生成圖片"
    )


# ─── 入口 ───


if __name__ == "__main__":
    mcp.run(transport="stdio")
