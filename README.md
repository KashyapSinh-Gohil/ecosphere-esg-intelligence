# EcoSphere ESG Intelligence

An open-source ESG operations platform built for the Odoo Hackathon. EcoSphere connects carbon accounting, employee participation, governance controls, gamification, reporting, and live operational telemetry in one responsive application.

![License](https://img.shields.io/badge/license-MIT-58dfa0)
![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-19-61DAFB)

## What it demonstrates

- Environmental dashboards, Scope 1/2/3 tracking, emission factors, goals, forecasts, and a policy what-if simulator
- CSR activities, employee participation, proof review, diversity, training, and engagement workflows
- ESG policies, acknowledgements, audits, compliance issues, ownership, and overdue detection
- Challenges, XP, points, badges, reward redemption, stock protection, and leaderboards
- Configurable ESG scoring, notifications, custom CSV reports, responsive navigation, and live telemetry
- Persistent local API workflows with automatic score recalculation and tested carbon calculators

## Architecture

```text
React + Vite UI
      |
FastAPI REST + WebSocket API
      |
SQLAlchemy domain models
      |
SQLite locally / replaceable DATABASE_URL in hosted environments
```

The FastAPI application serves the optimized frontend in unified-server mode. Vercel uses `api/index.py` for serverless REST operations and serves the Vite build from its CDN. Hosted telemetry gracefully uses a client-side live simulator because serverless functions do not keep persistent WebSocket processes.

## Quick start

Requirements: Node.js 20+ and Python 3.12+.

```bash
git clone https://github.com/KashyapSinh-Gohil/ecosphere-esg-intelligence.git
cd ecosphere-esg-intelligence

python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

cd frontend
npm ci
npm run build
cd ..

PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000). No sign-in is required for the hackathon demo.

For frontend development:

```bash
cd frontend
npm run dev
```

## Tests

```bash
python -m pytest -q
cd frontend && npm run lint && npm run build
```

The repository includes API tests and deterministic Scope 1, Scope 2, Scope 3, and BRSR/GRI calculator tests.

## Configuration and security

Copy `.env.example` to `.env` for local overrides. Real `.env` files, databases, credentials, build output, and internal design artifacts are excluded from Git and deployment uploads.

- Never commit API keys, tokens, passwords, or production databases.
- Set secrets through the hosting provider's encrypted environment-variable UI.
- Replace SQLite with a managed PostgreSQL `DATABASE_URL` for durable multi-instance production persistence.
- Authentication is intentionally omitted from this public hackathon demo; do not expose sensitive organizational data without adding identity and authorization.

## Project structure

```text
api/          Vercel ASGI entry point
backend/      FastAPI application, models, services, and API tests
calculators/  Carbon and reporting calculators
frontend/     React/Vite application
tests/        Calculator tests
```

## Contributing

Issues and pull requests are welcome. Please run the Python tests, frontend lint, and production build before submitting changes. Keep contributions focused, documented, and free of secrets or generated databases.

## License

Released under the [MIT License](LICENSE).
