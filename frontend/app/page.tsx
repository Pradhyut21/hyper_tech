'use client';

import Link from 'next/link';
import React from 'react';
import { useEffect, useState } from 'react';
import { DashboardPayload, getDashboardSummary, PatientSummary, RiskTier } from '@/lib/api';

const tiers: RiskTier[] = ['low', 'moderate', 'high', 'critical'];

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

function PatientRow({ patient }: { patient: PatientSummary }) {
  return (
    <Link
      href={`/dashboard/patients/${patient.patient_id}`}
      className="rounded-xl border border-slate-200 p-4 transition hover:border-slate-300 hover:bg-slate-50"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{patient.patient_id}</p>
          <p className="text-lg font-semibold">Patient {patient.patient_id}</p>
          <p className="text-sm text-slate-500">
            {patient.age} years · {patient.region}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <RiskBadge tier={patient.risk_tier} />
          <span className="text-sm font-medium text-slate-600">
            Score {patient.current_risk_score.toFixed(2)}
          </span>
        </div>
      </div>
    </Link>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch(() => setError('Connect the API to load the live synthetic roster.'));
  }, []);

  return (
    <main className="min-h-screen bg-slate-100 p-6 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">
              Hypertension Digital Twin
            </p>
            <h1 className="text-3xl font-bold">Clinician dashboard</h1>
          </div>
          <Link
            href="/dashboard/patients/p-001"
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
          >
            Open patient view
          </Link>
        </header>

        {error && (
          <p className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            {error}
          </p>
        )}
        {!data && !error && (
          <p className="mb-6 rounded-lg bg-white p-4 text-sm text-slate-500">
            Loading live risk board...
          </p>
        )}

        <section className="mb-6 grid gap-4 md:grid-cols-4">
          {tiers.map((tier) => (
            <div key={tier} className="card p-4">
              <p className="text-sm text-slate-500">{tier}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-2xl font-bold">{data?.risk_counts[tier] ?? 0}</span>
                <RiskBadge tier={tier} />
              </div>
            </div>
          ))}
        </section>

        <section className="card p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Live synthetic patient roster</h2>
            <span className="text-sm text-slate-500">
              {data?.total_patients ?? 0} patients · sorted by risk
            </span>
          </div>
          <div className="grid gap-3">
            {[...(data?.patients ?? [])]
              .sort((a, b) => b.current_risk_score - a.current_risk_score)
              .map((patient) => (
                <PatientRow key={patient.patient_id} patient={patient} />
              ))}
          </div>
        </section>
      </div>
    </main>
  );
}
