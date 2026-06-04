# Contributing

CV_GRAM is currently maintained as a focused full-stack coding project rather than a broad public open-source product. Contributions should keep the codebase easy to run, inspect, and extend.

## Local Setup

Backend:

```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend/CV_GRAM
npm install
npm run dev
```

Integrated full-stack run:

```powershell
.\.venv\Scripts\python run_fullstack.py --host 127.0.0.1 --port 8000 --reload
```

## Code Expectations

- Keep changes small and easy to review.
- Keep backend API logic, database access, and frontend views separated where practical.
- Do not commit generated folders such as `__pycache__`, `node_modules`, Vite `dist`, or copied frontend build assets.
- Do not commit secrets, API keys, SMTP passwords, database credentials, or private CV/profile data.
- Include screenshots for meaningful UI changes.
- Update docs when endpoint behavior, setup steps, or data assumptions change.

## Pull Request Notes

Useful change descriptions include:

- What changed.
- Why the change was needed.
- How it was tested.
- Any security, privacy, or data-model impact.

## Sensitive Test Data

Use synthetic CVs, fake emails, and local-only database records when testing. Remove real candidate names, private emails, reset tokens, session tokens, and API keys from logs or screenshots before sharing them.
