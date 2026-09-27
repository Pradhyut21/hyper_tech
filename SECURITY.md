# Security Overview

This proof-of-concept handles synthetic health data only and is designed to demonstrate a production-minded security posture without making claims that exceed the project scope.

## Implemented controls

- Secrets are read from environment variables, never committed.
- The repository includes a .env.example and a gitignored .env file pattern.
- A pre-commit secret scan is configured via .pre-commit-config.yaml and the same scan is expected in CI.
- Backend API routes are protected by an auth requirement in the FastAPI app layer.
- CORS is restricted to explicit origins.
- Prediction and ingestion routes have rate limits.
- Security headers are enabled in the frontend and backend configuration.
- Synthetic-data handling and deletion policy are documented.

The CI secret scan runs in `.github/workflows/security.yml`; local pre-commit hooks provide the faster developer feedback loop.

## Non-implemented or intentionally limited

- This is not a production clinical system and should not be treated as a regulated healthcare deployment.
- Real patient data is not used anywhere, and the repo explicitly excludes medical-grade compliance claims.

## Synthetic-data disclaimer

No real patient records were used at any stage. The project relies on public synthetic or reference sources, including the UCI Cuff-Less Blood Pressure Estimation dataset and a synthetic EHR generator pattern designed for demo purposes.
