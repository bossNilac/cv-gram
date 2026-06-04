# Architecture

CV_GRAM is a full-stack CV review, profile generation, and profile search application.

```text
Vue 3 frontend
  -> FastAPI backend
  -> authentication/session services
  -> CV upload and text extraction
  -> AI scoring/profile generation
  -> PostgreSQL profile and account storage
  -> authenticated search and profile views
```

## Main Runtime Areas

- `frontend/CV_GRAM/`: Vue 3 application built with Vite.
- `backend/main.py`: FastAPI application factory, router registration, CORS, and static frontend serving.
- `backend/routers/auth_routers/auth_router.py`: registration, login, logout, email verification, password reset, and session management.
- `backend/routers/v1/parser.py`: CV upload, validation, parsing, scoring, async scoring, and profile generation.
- `backend/routers/v1/resume_score.py`: stored profile lookup, score lookup, and profile search.
- `backend/models/`: SQLAlchemy model definitions and DTOs.
- `backend/db/`: database connection helpers and seed data.
- `backend/services/`: reusable backend services such as rate limiting and email delivery.
- `run_fullstack.py`: builds the frontend, copies the bundle into the backend, and starts the app on one origin.

## Request Flow

Public browser routes are served by the Vue app. During local frontend development, API requests target the FastAPI backend. In integrated mode, `run_fullstack.py` builds the Vue bundle into `backend/static/frontend`, then FastAPI serves both API routes and frontend routes from the same host and port.

Authenticated API requests use a session cookie. Backend dependencies validate that the session exists, has not expired, has not been revoked, and belongs to an active user.

## CV Processing Flow

1. The user uploads a `PDF`, `DOC`, or `DOCX` file.
2. The backend validates file type and size.
3. Text is extracted in memory.
4. Empty, unreadable, corrupted, unsupported, oversized, or non-CV files are rejected.
5. Extracted text is sent to the configured model flow.
6. Model output is validated and normalized.
7. Score data or structured profile JSON is optionally persisted.
8. The frontend renders scores, explanations, profile sections, or async task status.

## Persistence

PostgreSQL stores users, sessions, verification tokens, reset tokens, CV score fields, and structured profile JSON. Search uses stored profile data and database-side search behavior.

## Boundaries

The current project does not include:

- Public anonymous profile publishing.
- Manual profile editing independent of CV upload.
- Admin or recruiter team workspaces.
- Social features such as messaging or endorsements.
- Durable background workers for async scoring.
