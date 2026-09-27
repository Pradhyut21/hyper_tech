from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.db.store import store
from app.schemas.common import PatientCreateRequest, WearableReadingsRequest

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("")
async def create_patient(payload: PatientCreateRequest):
    patient = store.create_patient(payload.model_dump())
    return {"patient_id": patient.patient_id, "status": "created"}


@router.post("/{patient_id}/wearable-stream")
async def ingest_wearable_stream(patient_id: str, payload: WearableReadingsRequest):
    if patient_id not in store.patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "patient_not_found", "message": "Patient not found.", "details": []}})
    readings = [reading.model_dump() for reading in payload.readings]
    store.add_wearable_readings(patient_id, readings)
    return {"patient_id": patient_id, "ingested_count": len(readings)}


@router.get("/{patient_id}/twin-state")
async def twin_state(patient_id: str, request: Request):
    if patient_id not in store.patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "patient_not_found", "message": "Patient not found.", "details": []}})
    patient = store.get_patient(patient_id)
    recent = patient.wearable_readings[-5:]
    from app.services.fusion_engine import build_feature_vector
    prediction = request.app.state.model_service.predict(patient.__dict__, recent)

    feature_vector = build_feature_vector(patient.__dict__, recent)
    return {
        "patient_id": patient_id,
        "age": patient.age,
        "sex": patient.sex,
        "bmi": patient.bmi,
        "region": patient.region,
        "average_heart_rate": sum(r["heart_rate"] for r in recent) / max(len(recent), 1),
        "average_hrv_rmssd": sum(r["hrv_rmssd"] for r in recent) / max(len(recent), 1),
        "average_steps": int(sum(r["steps"] for r in recent) / max(len(recent), 1)),
        "average_sleep_minutes": sum(r["sleep_duration_minutes"] for r in recent) / max(len(recent), 1),
        "current_risk_score": prediction["risk_score"],
        "risk_tier": prediction["risk_tier"],
        "feature_vector": feature_vector,
    }


@router.get("/{patient_id}/history")
async def history(patient_id: str):
    if patient_id not in store.patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": {"code": "patient_not_found", "message": "Patient not found.", "details": []}})
    patient = store.get_patient(patient_id)
    return {"patient_id": patient_id, "predictions": patient.predictions, "readings": patient.wearable_readings}
