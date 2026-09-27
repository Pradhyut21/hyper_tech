import { act } from 'react';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import DashboardPage from './page';

afterEach(() => {
  vi.restoreAllMocks();
  document.body.innerHTML = '';
});

describe('dashboard', () => {
  it('renders the roster returned by the API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(
        async () =>
          new Response(
            JSON.stringify({
              total_patients: 1,
              risk_counts: { low: 0, moderate: 1, high: 0, critical: 0 },
              patients: [
                {
                  patient_id: 'live-001',
                  age: 57,
                  sex: 'female',
                  region: 'Pune',
                  bmi: 28.1,
                  current_risk_score: 0.58,
                  risk_tier: 'moderate',
                },
              ],
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } },
          ),
      ),
    );
    const container = document.createElement('div');
    document.body.append(container);
    const root = createRoot(container);
    await act(async () => {
      root.render(<DashboardPage />);
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
    expect(document.body.textContent).toContain('live-001');
    expect(document.body.textContent).toContain('Pune');
    root.unmount();
  });
});
