# Model Card: Hypertension Risk Digital Twin

## Purpose

This model predicts elevated hypertensive risk over the next 24–48 hours using a fused view of synthetic EHR features and wearable time-series signals.

## Data sources

- Wearable physiology: synthetic signals parameterized around public UCI Cuff-Less Blood Pressure Estimation reference ranges. The UCI records themselves are not bundled or used for fitting.
- Synthetic EHR: a reproducible synthetic patient generator used to model demographics, labs, and historical risk factors.
- No real patient data is used anywhere in this repository.

## Split strategy

Training, validation, and test rows are generated independently for this PoC. This is not a substitute for a subject-level clinical validation split.

## Model choice

A scikit-learn gradient-boosted classifier is used as the baseline for a fast, auditable risk model. This is explainable and fast enough for a hackathon proof-of-concept, with feature importances available for clinician review.

## Metrics

- AUROC: reported on the held-out test cohort.
- Precision, recall, and F1 used for risk-tier classification.
- Calibration is not established. The displayed interval is the 10th–90th percentile spread across gradient-boosting stages and should be read as a model-stability signal, not a clinical confidence interval.

## Limitations

- Synthetic data approximates real-world signal variation.
- The training label is a transparent synthetic proxy heuristic, so the reported accuracy measures rule recovery rather than clinical prediction.
- Physiological markers are not validated on a clinical population.
- The model is a decision-support prototype and not for clinical diagnosis or treatment.

## Non-clinical-use disclaimer

This project is a research and demo artifact for a digital twin prototype. It does not replace clinician judgment or medical advice.
