from __future__ import annotations

from statistics import fmean


def build_feature_vector(patient: dict, readings: list[dict]) -> dict[str, float]:
    if not readings:
        readings = [{
            "heart_rate": 72.0,
            "hrv_rmssd": 35.0,
            "hrv_sdnn": 55.0,
            "steps": 5000,
            "sleep_duration_minutes": 420.0,
            "systolic_bp_estimate": 120.0,
            "diastolic_bp_estimate": 80.0,
        }]

    avg_hr = fmean(r["heart_rate"] for r in readings)
    avg_hrv = fmean(r["hrv_rmssd"] for r in readings)
    avg_sleep = fmean(r["sleep_duration_minutes"] for r in readings)
    bp_mean = fmean((r["systolic_bp_estimate"] + r["diastolic_bp_estimate"]) / 2 for r in readings)

    features = {
        "age": float(patient.get("age", 45)),
        "bmi": float(patient.get("bmi", 26)),
        "heart_rate": float(avg_hr),
        "hrv_rmssd": float(avg_hrv),
        "sleep_duration_minutes": float(avg_sleep),
        "bp_mean": float(bp_mean),
        "family_history_htn": 1.0 if patient.get("genetic_flags", {}).get("family_history_htn", False) else 0.0,
        "salt_sensitivity_marker": 1.0 if patient.get("genetic_flags", {}).get("salt_sensitivity_marker", False) else 0.0,
        "total_diagnoses": float(len(patient.get("diagnoses", []))),
    }
    return features
