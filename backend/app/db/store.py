from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class PatientRecord:
    patient_id: str
    age: int
    sex: str
    bmi: float
    region: str
    diagnoses: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    labs: dict[str, float] = field(default_factory=dict)
    genetic_flags: dict[str, bool] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    wearable_readings: list[dict[str, Any]] = field(default_factory=list)
    predictions: list[dict[str, Any]] = field(default_factory=list)


class DemoStore:
    def __init__(self) -> None:
        self.patients: dict[str, PatientRecord] = {}

    def seed_demo_patients(self) -> None:
        if self.patients:
            return
        seed = [
            ("p-001", 52, "female", 29.4, "Bengaluru", 74, 35, 420, 122, 2),
            ("p-002", 41, "male", 24.8, "Hyderabad", 68, 48, 455, 116, 0),
            ("p-003", 63, "male", 31.2, "Delhi", 82, 26, 360, 136, 3),
            ("p-004", 71, "female", 33.8, "Chennai", 91, 19, 315, 148, 4),
        ]
        for patient_id, age, sex, bmi, region, heart_rate, hrv, sleep, bp, diagnoses in seed:
            self.create_patient({
                "patient_id": patient_id,
                "age": age,
                "sex": sex,
                "bmi": bmi,
                "region": region,
                "diagnoses": ["I10"] * diagnoses,
                "genetic_flags": {"family_history_htn": patient_id in {"p-003", "p-004"}},
            })
            self.add_wearable_readings(patient_id, [{
                "timestamp": datetime.now(timezone.utc),
                "heart_rate": heart_rate,
                "hrv_rmssd": hrv,
                "hrv_sdnn": hrv + 18,
                "steps": 4200,
                "sleep_duration_minutes": sleep,
                "systolic_bp_estimate": bp,
                "diastolic_bp_estimate": 82,
            }])

    def create_patient(self, payload: dict[str, Any]) -> PatientRecord:
        patient_id = payload["patient_id"]
        patient = PatientRecord(
            patient_id=patient_id,
            age=payload["age"],
            sex=payload["sex"],
            bmi=payload["bmi"],
            region=payload["region"],
            diagnoses=payload.get("diagnoses", []),
            medications=payload.get("medications", []),
            labs=payload.get("labs", {}),
            genetic_flags=payload.get("genetic_flags", {}),
        )
        self.patients[patient_id] = patient
        return patient

    def add_wearable_readings(self, patient_id: str, readings: list[dict[str, Any]]) -> None:
        patient = self.patients[patient_id]
        patient.wearable_readings.extend(readings)

    def add_prediction(self, patient_id: str, payload: dict[str, Any]) -> None:
        patient = self.patients[patient_id]
        payload = dict(payload)
        payload["timestamp"] = payload.get("timestamp", datetime.now(timezone.utc).isoformat())
        patient.predictions.append(payload)

    def get_patient(self, patient_id: str) -> PatientRecord:
        if patient_id not in self.patients:
            raise KeyError(patient_id)
        return self.patients[patient_id]

    def summary(self) -> dict[str, Any]:
        total = len(self.patients)
        risk_counts = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        for patient in self.patients.values():
            if not patient.predictions:
                continue
            latest = patient.predictions[-1]
            risk_counts.setdefault(latest["risk_tier"], 0)
            risk_counts[latest["risk_tier"]] += 1
        return {"total_patients": total, "risk_counts": risk_counts}

    def roster(self) -> list[dict[str, Any]]:
        return [
            {
                "patient_id": patient.patient_id,
                "age": patient.age,
                "sex": patient.sex,
                "region": patient.region,
                "bmi": patient.bmi,
                "current_risk_score": float(patient.predictions[-1]["risk_score"]) if patient.predictions else 0.0,
                "risk_tier": patient.predictions[-1]["risk_tier"] if patient.predictions else "low",
            }
            for patient in self.patients.values()
        ]


store = DemoStore()
