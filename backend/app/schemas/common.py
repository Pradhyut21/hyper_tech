from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    message: str
    details: list[str] | dict[str, str] | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    error: ErrorEnvelope


class PatientCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str = Field(..., min_length=1)
    age: int = Field(..., ge=18, le=90)
    sex: Literal["male", "female", "other"]
    bmi: float = Field(..., gt=10, lt=60)
    region: str = Field(..., min_length=2)
    diagnoses: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    labs: dict[str, float] = Field(default_factory=dict)
    genetic_flags: dict[str, bool] = Field(default_factory=dict)


class WearableReading(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: datetime
    heart_rate: float = Field(..., ge=30, le=200)
    hrv_rmssd: float = Field(..., ge=0, le=250)
    hrv_sdnn: float = Field(..., ge=0, le=300)
    steps: int = Field(..., ge=0, le=50000)
    sleep_duration_minutes: float = Field(..., ge=0, le=1000)
    systolic_bp_estimate: float = Field(..., ge=50, le=220)
    diastolic_bp_estimate: float = Field(..., ge=30, le=150)


class WearableReadingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    readings: list[WearableReading] = Field(..., min_length=1)


class TwinState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str
    age: int
    sex: str
    bmi: float
    region: str
    average_heart_rate: float
    average_hrv_rmssd: float
    average_steps: int
    average_sleep_minutes: float
    current_risk_score: float
    risk_tier: str
    feature_vector: dict[str, float]


class PredictionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_tier: str
    predicted_event: str
    confidence_interval: dict[str, float]
    top_features: list[dict[str, float | str]]
    summary: str
    timestamp: datetime
    feature_vector: dict[str, float] | None = None
    uncertainty_method: str | None = None


class PatientHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str
    predictions: list[PredictionResult]
    readings: list[WearableReading]


class PatientSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: str
    age: int
    sex: str
    region: str
    bmi: float
    current_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_tier: str


class DashboardSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_patients: int
    risk_counts: dict[str, int]
    patients: list[PatientSummary]
