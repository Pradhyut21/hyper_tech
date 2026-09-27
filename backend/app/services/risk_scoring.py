from __future__ import annotations


def tier_from_score(score: float) -> str:
    if score < 0.35:
        return "low"
    if score < 0.6:
        return "moderate"
    if score < 0.8:
        return "high"
    return "critical"


def explainability_ranking(feature_importance: dict[str, float]) -> list[dict[str, float | str]]:
    ranked = sorted(feature_importance.items(), key=lambda item: abs(float(item[1])), reverse=True)[:5]
    return [{"feature": name, "importance": float(value)} for name, value in ranked]
