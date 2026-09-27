# CI overview

## backend-ci.yml
- Trigger: PRs and pushes touching the backend folder.
- Runs static checks, mypy, and the backend test suite with coverage.

## frontend-ci.yml
- Trigger: PRs and pushes touching the frontend folder.
- Runs Prettier, ESLint, TypeScript compilation, tests and Next build.

## model-validation.yml
- Trigger: PRs editing the ML training code or model pipeline.
- Re-trains the model and fails if validation accuracy drops below the threshold.

## deploy.yml
- Trigger: only merges to main.
- Contains explicit backend and frontend deployment placeholders for production wiring.

If any workflow fails, inspect the exact failing step in GitHub Actions, fix the issue locally, and re-run the matching command.
