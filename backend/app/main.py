from fastapi import FastAPI

from app.api.health import router as health_router


app = FastAPI(
    title="MarketSignal AI",
    description="AI-powered market intelligence and trading education platform",
    version="0.1.0"
)

app.include_router(health_router)