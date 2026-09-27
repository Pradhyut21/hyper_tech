'use client';

import { useParams } from 'next/navigation';
import React from 'react';
import { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  getHistory,
  getPatient,
  getPrediction,
  PatientHistory,
  PatientSummary,
  PredictionResponse,
  RiskTier,
} from '@/lib/api';

function RiskBadge({ tier }: { tier: RiskTier }) {
  const palettes: Record<RiskTier, string> = {
    low: 'bg-risk-low text-white',
    moderate: 'bg-risk-moderate text-white',
    high: 'bg-risk-high text-white',
    critical: 'bg-risk-critical text-white',
  };
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${palettes[tier]}`}>
      {tier}
    </span>
  );
}

export default function PatientPage() {
  const params = useParams<{ id: string }>();
  const patientId = params.id;
  const [patient, setPatient] = useState<PatientSummary | null>(null);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [history, setHistory] = useState<PatientHistory | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getPatient(patientId), getPrediction(patientId), getHistory(patientId)])
      .then(([patientState, latestPrediction, patientHistory]) => {
        setPatient(patientState);
        setPrediction(latestPrediction);
        setHistory(patientHistory);
      })
      .catch(() =>
        setError('Unable to load this patient from the API. Check the backend and API key.'),
      );
  }, [patientId]);

  if (error)
    return (
      <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
        <p className="mx-auto max-w-3xl rounded-lg border border-red-200 bg-red-50 p-5 text-red-800">
          {error}
        </p>
      </main>
    );
  if (!patient || !prediction || !history)
    return (
      <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
        <p className="mx-auto max-w-3xl rounded-lg bg-white p-5 text-slate-500">
          Loading live patient digital twin...
        </p>
      </main>
    );

  const series = history.readings.map((reading) => ({
    time: new Date(reading.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    }),
    hr: reading.heart_rate,
    bp: reading.systolic_bp_estimate,
  }));
  const scores = history.predictions.map((item) => ({
    time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    score: item.risk_score,
  }));
  const features = prediction.top_features.map((item) => ({
    feature: String(item.feature),
    importance: Number(item.importance),
  }));

  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="card p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">
                Patient digital twin
              </p>
              <h1 className="text-3xl font-bold">{patient.patient_id}</h1>
            </div>
            <div className="flex items-center gap-3">
              <RiskBadge tier={prediction.risk_tier} />
              <span className="text-lg font-semibold">{prediction.risk_score.toFixed(2)}</span>
            </div>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-4">
            {[
              ['Age', patient.age],
              ['Sex', patient.sex],
              ['BMI', patient.bmi],
              ['Region', patient.region],
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">{label}</p>
                <p className="text-xl font-semibold">{value}</p>
              </div>
            ))}
          </div>
        </header>

        <section className="grid gap-6 xl:grid-cols-[2fr_1fr]">
          <div className="card p-5">
            <h2 className="mb-4 text-lg font-semibold">Wearable signal overview</h2>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={series}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="hr" stroke="#0f172a" strokeWidth={2} />
                  <Line type="monotone" dataKey="bp" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="card p-5">
            <h2 className="mb-4 text-lg font-semibold">Model summary</h2>
            <p className="rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-700">
              {prediction.summary}
            </p>
            <div className="mt-5 rounded-xl bg-slate-900 p-4 text-white">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Risk interval</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-3xl font-bold">{prediction.risk_score.toFixed(2)}</span>
                <RiskBadge tier={prediction.risk_tier} />
              </div>
              <p className="mt-3 text-xs text-slate-300">
                {prediction.confidence_interval.lower.toFixed(2)}–
                {prediction.confidence_interval.upper.toFixed(2)} · {prediction.uncertainty_method}
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
          <div className="card p-5">
            <h2 className="mb-4 text-lg font-semibold">Model feature importance</h2>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={features} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="feature" width={150} />
                  <Tooltip />
                  <Bar dataKey="importance" fill="#102a43" radius={[0, 8, 8, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="card p-5">
            <h2 className="mb-4 text-lg font-semibold">Prediction history</h2>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={scores}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#1f9d74" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
