export type RiskTier = 'low' | 'moderate' | 'high' | 'critical';

export interface PatientSummary {
  patient_id: string;
  age: number;
  sex: string;
  region: string;
  bmi: number;
  current_risk_score: number;
  risk_tier: RiskTier;
}

export interface DashboardPayload {
  total_patients: number;
  risk_counts: Record<string, number>;
  patients: PatientSummary[];
}

export interface PredictionResponse {
  patient_id: string;
  risk_score: number;
  risk_tier: RiskTier;
  predicted_event: string;
  confidence_interval: { lower: number; upper: number };
  top_features: Array<{ feature: string; importance: number }>;
  summary: string;
  timestamp: string;
  feature_vector?: Record<string, number>;
  uncertainty_method?: string;
}

export interface WearableReading {
  timestamp: string;
  heart_rate: number;
  hrv_rmssd: number;
  hrv_sdnn: number;
  steps: number;
  sleep_duration_minutes: number;
  systolic_bp_estimate: number;
  diastolic_bp_estimate: number;
}

export interface PatientHistory {
  patient_id: string;
  predictions: PredictionResponse[];
  readings: WearableReading[];
}

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

function apiHeaders(): Record<string, string> {
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  return apiKey ? { 'X-API-Key': apiKey } : {};
}

export async function getDashboardSummary(): Promise<DashboardPayload> {
  const response = await fetch(`${apiUrl}/api/v1/dashboard/summary`, {
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Dashboard summary failed');
  return response.json();
}

export async function getPatient(patientId: string): Promise<PatientSummary> {
  const response = await fetch(`${apiUrl}/api/v1/patients/${patientId}/twin-state`, {
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Patient fetch failed');
  return response.json();
}

export async function getPrediction(patientId: string): Promise<PredictionResponse> {
  const response = await fetch(`${apiUrl}/api/v1/patients/${patientId}/predict`, {
    method: 'POST',
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Prediction failed');
  return response.json();
}

export async function getHistory(patientId: string): Promise<PatientHistory> {
  const response = await fetch(`${apiUrl}/api/v1/patients/${patientId}/history`, {
    headers: apiHeaders(),
  });
  if (!response.ok) throw new Error('Patient history failed');
  return response.json();
}
