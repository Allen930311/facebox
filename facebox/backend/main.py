"""FaceBox 後端入口 — FastAPI 伺服器"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import HOST, PORT
from .routes.profiles import router as profiles_router
from .routes.generate import router as generate_router
from .routes.train import router as train_router
from .services.sd_client import sd_client

app = FastAPI(
    title="FaceBox",
    description="個人臉部克隆工具 — Stable Diffusion + LoRA",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles_router)
app.include_router(generate_router)
app.include_router(train_router)


@app.get("/health")
async def health():
    """健康檢查 — 同時回報 SD WebUI 連線狀態。"""
    sd_ok = False
    sd_info = None
    try:
        sd_info = await sd_client.health_check()
        sd_ok = True
    except Exception as e:
        sd_info = str(e)

    return {
        "status": "ok",
        "service": "FaceBox",
        "port": PORT,
        "sd_webui": {
            "connected": sd_ok,
            "info": sd_info,
        },
    }


@app.get("/sd/models")
async def sd_models():
    """列出 SD WebUI 可用的 checkpoint 模型。"""
    try:
        return await sd_client.get_models()
    except Exception as e:
        return {"error": str(e)}


@app.get("/sd/loras")
async def sd_loras():
    """列出 SD WebUI 可用的 LoRA。"""
    try:
        return await sd_client.get_loras()
    except Exception as e:
        return {"error": str(e)}


@app.get("/sd/samplers")
async def sd_samplers():
    """列出可用的取樣器。"""
    try:
        return await sd_client.get_samplers()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
