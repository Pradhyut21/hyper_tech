from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.services.fusion_engine import build_feature_vector
from app.services.risk_scoring import explainability_ranking, tier_from_score


class PredictionService:
    def __init__(self, model_path: str) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        candidate = Path(model_path)
        if not candidate.is_absolute():
            candidate = backend_root / candidate
        self.model_path = candidate
        self.model: Any = None
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            from app.ml.train_model import train_and_save

            artifact_dir = self.model_path.parent
            train_and_save(str(artifact_dir))
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}")
        self.model = joblib.load(self.model_path)

    def predict(self, patient: dict, readings: list[dict]) -> dict:
        feature_vector = build_feature_vector(patient, readings)
        feature_names = list(feature_vector.keys())
        row = pd.DataFrame([[feature_vector[name] for name in feature_names]], columns=feature_names)
        raw_score = float(self.model.predict_proba(row)[0][1])
        risk_tier = tier_from_score(raw_score)
        staged_scores = [float(probability[0][1]) for probability in self.model.staged_predict_proba(row)]
        lower, upper = np.quantile(staged_scores, [0.1, 0.9]).tolist()
        confidence_interval = {
            "lower": round(min(float(lower), raw_score), 4),
            "upper": round(max(float(upper), raw_score), 4),
        }
        feature_importance = {name: float(self.model.feature_importances_[idx]) for idx, name in enumerate(feature_names)}
        return {
            "risk_score": raw_score,
            "risk_tier": risk_tier,
            "predicted_event": "elevated hypertensive risk within next 24–48h",
            "confidence_interval": confidence_interval,
            "top_features": explainability_ranking(feature_importance),
            "feature_vector": feature_vector,
            "uncertainty_method": "10th-90th percentile across gradient boosting stages",
            "summary": "Patient shows elevated blood-pressure risk driven by combined cardiovascular strain and clinical factors.",
        }

    def load_model(self):
        return self.model
