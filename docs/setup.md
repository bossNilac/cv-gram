# Setup

This project has a FastAPI backend and a Vue 3 frontend.

## Requirements

- Python 3.11 or newer
- Node.js compatible with the frontend `package.json` engines field
- PostgreSQL
- SMTP credentials for email flows
- OpenAI API credentials for CV scoring and profile generation

## Backend

Install backend dependencies in your virtual environment:

```powershell
.\.venv\Scripts\python -m pip install -r backend\requirements.txt
```

Run the API:

```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend/CV_GRAM
npm install
npm run dev
```

The frontend uses `VITE_API_BASE` when provided. Otherwise it is expected to talk to the local backend.

## Integrated Full Stack

```powershell
.\.venv\Scripts\python run_fullstack.py --host 127.0.0.1 --port 8000 --reload
```

This command builds the frontend, copies the production bundle into `backend/static/frontend`, and serves the API plus frontend from one origin.

Use `--skip-build` when you only want to restart the backend using the already copied frontend bundle:

```powershell
.\.venv\Scripts\python run_fullstack.py --host 127.0.0.1 --port 8000 --reload --skip-build
```

## Configuration

Common environment variables:

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_FROM`
- `APP_BASE_URL`
- `FRONTEND_BASE_URL`
- `SUPPORT_EMAIL`
- `OPENAI_API_KEY`
- `OPENAI_ADV_API_KEY`
- `PRIMARY_MODEL`
- `ESCALATION_MODEL`
- `ADV_MODEL`
- `AUTO_ESCALATE`
- `MIN_CONFIDENCE`
- `CV_MAX_MB`

## Database

The SQL initialization file is:

```text
design/database.sql
```

Search test data is available at:

```text
backend/db/seed_search_test_users.sql
```
