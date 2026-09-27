from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import dashboard, patients, predictions
from app.core.config import settings
from app.core.security import ApiKeyDep
from app.db.store import store
from app.services.prediction_service import PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.seed_demo_patients()
    app.state.model_service = PredictionService(settings.model_path)
    for patient in store.patients.values():
        if not patient.predictions:
            prediction = app.state.model_service.predict(patient.__dict__, patient.wearable_readings)
            prediction["timestamp"] = datetime.now(timezone.utc).isoformat()
            patient.predictions.append(prediction)
    yield


app = FastAPI(title="Digital Twin Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    payload = exc.detail if isinstance(exc.detail, dict) else {"error": {"code": "http_error", "message": str(exc.detail), "details": None}}
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/health/ready")
async def ready() -> dict:
    try:
        _ = app.state.model_service
        return {"status": "ready", "db": "demo-in-memory", "model": "loaded"}
    except AttributeError as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": {"code": "model_load_failed", "message": str(exc), "details": []}})


app.include_router(patients.router, prefix=settings.api_v1_prefix, dependencies=[ApiKeyDep])
app.include_router(predictions.router, prefix=settings.api_v1_prefix, dependencies=[ApiKeyDep])
app.include_router(dashboard.router, prefix=settings.api_v1_prefix, dependencies=[ApiKeyDep])
