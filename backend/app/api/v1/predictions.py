from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status

from app.db.store import store
from app.schemas.common import PredictionResult
from app.services.llm_summary_service import synthesize_summary

router = APIRouter(prefix="/patients", tags=["predictions"])


@router.post("/{patient_id}/predict", response_model=PredictionResult)
async def predict(patient_id: str, request: Request):
    if patient_id not in store.patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "patient_not_found", "message": "Patient not found.", "details": []}})

    patient = store.get_patient(patient_id)
    readings = patient.wearable_readings[-10:]
    prediction = request.app.state.model_service.predict(patient.__dict__, readings)
    prediction["patient_id"] = patient_id
    prediction["timestamp"] = datetime.now(timezone.utc).isoformat()
    patient.predictions.append({**prediction})
    prediction["summary"] = synthesize_summary(prediction)
    return {
        "patient_id": patient_id,
        "risk_score": float(prediction["risk_score"]),
        "risk_tier": prediction["risk_tier"],
        "predicted_event": prediction["predicted_event"],
        "confidence_interval": prediction["confidence_interval"],
        "top_features": prediction["top_features"],
        "summary": prediction["summary"],
        "timestamp": prediction["timestamp"],
    }
