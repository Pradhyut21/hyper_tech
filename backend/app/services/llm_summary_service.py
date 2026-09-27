from __future__ import annotations


def synthesize_summary(prediction: dict) -> str:
    drivers = ", ".join(str(item["feature"]).replace("_", " ") for item in prediction.get("top_features", [])[:3])
    driver_text = drivers or "the available fused signals"
    return (
        f"AI-generated summary — verify against clinical judgment. The patient is in the {prediction['risk_tier']} risk tier "
        f"with a modeled risk score of {prediction['risk_score']:.2f}. The leading model features are {driver_text}. "
        "Monitor for worsening blood-pressure indicators over the next 24–48 hours."
    )
