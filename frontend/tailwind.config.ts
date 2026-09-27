import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#f3f5f7',
        panel: '#ffffff',
        ink: '#102a43',
        muted: '#5b6b7f',
        'risk-low': '#1f9d74',
        'risk-moderate': '#d97706',
        'risk-high': '#ef4444',
        'risk-critical': '#7f1d1d',
      },
    },
  },
  plugins: [],
};

export default config;
