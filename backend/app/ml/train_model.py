from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def generate_synthetic_dataset(rows: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    records = []
    for _ in range(rows):
        age = int(rng.integers(25, 80))
        bmi = float(rng.normal(27, 5))
        heart_rate = float(rng.normal(72, 8))
        hrv_rmssd = float(rng.normal(35, 12))
        sleep = float(rng.normal(420, 70))
        bp_mean = float(rng.normal(92, 18))
        family_history = int(rng.random() < 0.4)
        salt_sensitivity = int(rng.random() < 0.3)
        risk = int((heart_rate > 75) + (bmi > 30) + (bp_mean > 95) + family_history + salt_sensitivity >= 2)
        records.append({
            "age": age,
            "bmi": bmi,
            "heart_rate": heart_rate,
            "hrv_rmssd": hrv_rmssd,
            "sleep_duration_minutes": sleep,
            "bp_mean": bp_mean,
            "family_history_htn": family_history,
            "salt_sensitivity_marker": salt_sensitivity,
            "total_diagnoses": int(rng.integers(0, 5)),
            "label": risk,
        })
    return pd.DataFrame(records)


def train_and_save(output_dir: str = "app/ml/artifacts") -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    df = generate_synthetic_dataset()
    # Split by subject-level grouping is important to prevent leakage across repeated rows; for this synthetic demo, the generated data is already subject-consistent by row block.
    X = df.drop(columns=["label"])
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, output_dict=True)

    artifact = output_path / "risk_model.joblib"
    joblib.dump(model, artifact)
    metadata = {
        "accuracy": float(accuracy),
        "classification_report": report,
        "label_definition": "synthetic proxy label generated from transparent cardiovascular risk heuristics",
        "data_status": "synthetic-only; no UCI records are bundled or used for fitting",
        "feature_names": list(X.columns),
    }
    (output_path / "training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return str(artifact)


if __name__ == "__main__":
    train_and_save()
