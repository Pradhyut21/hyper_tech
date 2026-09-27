import json
from pathlib import Path

import joblib
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.store import DemoStore
from app.main import app
from app.ml.train_model import generate_synthetic_dataset, train_and_save
from app.services.fusion_engine import build_feature_vector
from app.services.prediction_service import PredictionService
from app.services.risk_scoring import explainability_ranking, tier_from_score


def test_fusion_builds_feature_vector():
    patient = {"age": 52, "bmi": 29.1, "diagnoses": ["I10"], "genetic_flags": {"family_history_htn": True}}
    readings = [
        {"heart_rate": 72, "hrv_rmssd": 28, "hrv_sdnn": 45, "steps": 4200, "sleep_duration_minutes": 420, "systolic_bp_estimate": 126, "diastolic_bp_estimate": 82},
        {"heart_rate": 78, "hrv_rmssd": 30, "hrv_sdnn": 50, "steps": 5100, "sleep_duration_minutes": 390, "systolic_bp_estimate": 132, "diastolic_bp_estimate": 84},
    ]
    features = build_feature_vector(patient, readings)
    assert "heart_rate" in features
    assert features["age"] == 52.0
    assert features["family_history_htn"] == 1.0


def test_content_features_are_numeric():
    patient = {"age": 50, "bmi": 28.0, "diagnoses": ["I10"], "genetic_flags": {"salt_sensitivity_marker": True}}
    result = build_feature_vector(patient, [{"heart_rate": 70, "hrv_rmssd": 25, "hrv_sdnn": 40, "steps": 6000, "sleep_duration_minutes": 440, "systolic_bp_estimate": 118, "diastolic_bp_estimate": 75}])
    assert all(isinstance(value, float) for value in result.values())


def test_tier_from_score_low():
    assert tier_from_score(0.2) == "low"


def test_tier_from_score_moderate():
    assert tier_from_score(0.45) == "moderate"


def test_tier_from_score_high():
    assert tier_from_score(0.7) == "high"


def test_tier_from_score_critical():
    assert tier_from_score(0.9) == "critical"


def test_explainability_ranking_limits_entries():
    ranked = explainability_ranking({"age": 0.2, "bmi": 0.4, "heart_rate": 0.7, "sleep": 0.5})
    assert len(ranked) <= 5
    assert ranked[0]["feature"] in {"age", "bmi", "heart_rate", "sleep"}


def test_store_can_create_patient():
    store = DemoStore()
    patient = store.create_patient({"patient_id": "p1", "age": 40, "sex": "female", "bmi": 24, "region": "Bengaluru", "diagnoses": ["E11"], "labs": {"glucose": 94.0}})
    assert patient.patient_id == "p1"
    assert patient.age == 40


def test_store_add_prediction_updates_summary():
    store = DemoStore()
    store.create_patient({"patient_id": "p2", "age": 50, "sex": "male", "bmi": 28, "region": "Hyderabad"})
    store.add_prediction("p2", {"risk_tier": "high", "risk_score": 0.75})
    summary = store.summary()
    assert summary["risk_counts"]["high"] == 1


def test_store_summary_counts_all_tiers():
    store = DemoStore()
    store.create_patient({"patient_id": "p3", "age": 60, "sex": "male", "bmi": 30, "region": "Delhi"})
    store.create_patient({"patient_id": "p4", "age": 62, "sex": "female", "bmi": 27, "region": "Chennai"})
    store.add_prediction("p3", {"risk_tier": "moderate", "risk_score": 0.55})
    store.add_prediction("p4", {"risk_tier": "critical", "risk_score": 0.88})
    summary = store.summary()
    assert summary["total_patients"] == 2
    assert summary["risk_counts"]["moderate"] == 1
    assert summary["risk_counts"]["critical"] == 1


def test_generate_synthetic_dataset_shape():
    df = generate_synthetic_dataset(rows=25)
    assert len(df) == 25
    assert "label" in df.columns
    assert "age" in df.columns


def test_generate_synthetic_dataset_label_is_binary():
    df = generate_synthetic_dataset(rows=50)
    assert set(df["label"].unique()) <= {0, 1}


def test_train_and_save_generates_artifact(tmp_path):
    artifact_path = tmp_path / "risk_model.joblib"
    output_dir = str(tmp_path)
    saved = train_and_save(output_dir)
    assert saved == str(artifact_path)
    assert artifact_path.exists()
    metadata_file = tmp_path / "training_metadata.json"
    assert metadata_file.exists()
    text = json.loads(metadata_file.read_text(encoding="utf-8"))
    assert "accuracy" in text


def test_prediction_service_predict_returns_expected_keys():
    service = PredictionService("app/ml/artifacts/risk_model.joblib")
    patient = {"age": 63, "bmi": 31.2, "diagnoses": ["I10"], "genetic_flags": {"family_history_htn": True}}
    readings = [{"heart_rate": 82, "hrv_rmssd": 26, "hrv_sdnn": 46, "steps": 5400, "sleep_duration_minutes": 360, "systolic_bp_estimate": 136, "diastolic_bp_estimate": 89}]
    prediction = service.predict(patient, readings)
    assert set(prediction.keys()) >= {"risk_score", "risk_tier", "predicted_event", "confidence_interval", "top_features", "feature_vector"}


def test_prediction_score_is_bounded():
    service = PredictionService("app/ml/artifacts/risk_model.joblib")
    patient = {"age": 55, "bmi": 28, "diagnoses": [], "genetic_flags": {}}
    readings = [{"heart_rate": 74, "hrv_rmssd": 35, "hrv_sdnn": 50, "steps": 7000, "sleep_duration_minutes": 430, "systolic_bp_estimate": 124, "diastolic_bp_estimate": 82}]
    prediction = service.predict(patient, readings)
    assert 0.0 <= prediction["risk_score"] <= 1.0
    assert prediction["confidence_interval"]["lower"] <= prediction["confidence_interval"]["upper"]


def test_prediction_service_loads_model_object():
    service = PredictionService("app/ml/artifacts/risk_model.joblib")
    assert service.model is not None
    assert hasattr(service.model, "predict_proba")


def test_default_feature_vector_for_empty_readings():
    patient = {"age": 46, "bmi": 24, "diagnoses": [], "genetic_flags": {}}
    result = build_feature_vector(patient, [])
    assert result["heart_rate"] > 0
    assert result["sleep_duration_minutes"] > 0


def test_model_artifact_is_pickle_loadable():
    artifact = joblib.load("app/ml/artifacts/risk_model.joblib")
    assert artifact is not None


def test_training_script_creates_artifact_directory(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir()
    saved = train_and_save(str(output_dir))
    assert Path(saved).exists()


def test_http_dashboard_requires_auth_and_returns_seeded_roster():
    settings.secret_key = "test-key"
    with TestClient(app) as client:
        assert client.get("/api/v1/dashboard/summary").status_code == 401
        response = client.get("/api/v1/dashboard/summary", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_patients"] >= 4
    assert {patient["patient_id"] for patient in payload["patients"]} >= {"p-001", "p-004"}


def test_http_twin_state_is_computed_for_requested_patient():
    settings.secret_key = "test-key"
    with TestClient(app) as client:
        first = client.get("/api/v1/patients/p-001/twin-state", headers={"X-API-Key": "test-key"})
        second = client.get("/api/v1/patients/p-004/twin-state", headers={"X-API-Key": "test-key"})
    assert first.status_code == second.status_code == 200
    assert first.json()["patient_id"] == "p-001"
    assert second.json()["patient_id"] == "p-004"
    assert first.json()["current_risk_score"] != second.json()["current_risk_score"]


def test_http_prediction_uses_cached_model_and_returns_model_metadata():
    settings.secret_key = "test-key"
    with TestClient(app) as client:
        response = client.post("/api/v1/patients/p-003/predict", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["patient_id"] == "p-003"
    assert payload["confidence_interval"]["lower"] <= payload["risk_score"] <= payload["confidence_interval"]["upper"]
    assert payload["top_features"]
