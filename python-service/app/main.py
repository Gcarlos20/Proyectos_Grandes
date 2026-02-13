from typing import Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    java_service_url: str = "http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ScoreRequest(BaseModel):
    user_id: int = Field(gt=0)
    transactions_last_30d: int = Field(ge=0)
    avg_ticket: float = Field(ge=0)
    chargeback_count: int = Field(ge=0)


class ScoreResponse(BaseModel):
    user_id: int
    risk_score: float
    segment: str
    java_service_status: Optional[str] = None


settings = Settings()
app = FastAPI(title="enterprise-python-service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "python-service", "env": settings.app_env}


@app.post("/api/v1/analytics/score", response_model=ScoreResponse)
async def score(payload: ScoreRequest) -> ScoreResponse:
    base = 50.0
    base += min(payload.transactions_last_30d * 0.3, 20)
    base += min(payload.avg_ticket * 0.05, 20)
    base -= min(payload.chargeback_count * 15, 45)

    risk_score = max(0.0, min(100.0, round(base, 2)))
    if risk_score >= 75:
        segment = "low-risk"
    elif risk_score >= 45:
        segment = "medium-risk"
    else:
        segment = "high-risk"

    java_status = None
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            response = await client.get(f"{settings.java_service_url}/api/v1/health")
            if response.status_code == 200:
                java_status = response.json().get("status", "unknown")
            else:
                java_status = "unreachable"
    except Exception:
        java_status = "unreachable"

    return ScoreResponse(
        user_id=payload.user_id,
        risk_score=risk_score,
        segment=segment,
        java_service_status=java_status,
    )
