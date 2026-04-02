# CV_GRAM

CV_GRAM is a full-stack CV review, profile storage, and search platform.

It is designed to work as both:
- a helper for reviewing and ranking CVs
- a profile-hosting space where people can turn a CV into a searchable structured presence

The public landing page reflects that directly:
- people can get their CV rated by AI
- people can build a profile similar to LinkedIn
- people can search for others based on CV scores and profile signals

## What The App Includes

The current product covers:
- account creation, login, email verification, forgot password, and reset password
- CV upload and AI-assisted scoring
- storing CV-derived profile data
- profile viewing for the current user or another user
- search across saved profiles using text signals and score thresholds
- session management and account security tools

## Stack

Frontend:
- Vue 3
- Vue Router
- Vite

Backend:
- FastAPI
- SQLAlchemy
- PostgreSQL
- SMTP email delivery

AI / processing:
- OpenAI-backed CV scoring and profile extraction flows

## Project Structure

- [frontend/CV_GRAM](frontend/CV_GRAM): Vue application
- [backend](backend): FastAPI API, DB models, routers, services
- [run_fullstack.py](run_fullstack.py): builds the frontend into the backend and runs the app on one port

## Main Backend Areas

- [backend/main.py](backend/main.py): app entrypoint and frontend static serving
- [backend/routers/auth_routers/auth_router.py](backend/routers/auth_routers/auth_router.py): auth, sessions, verification, reset password
- [backend/routers/v1/parser.py](backend/routers/v1/parser.py): CV parsing, scoring, and profile generation
- [backend/routers/v1/resume_score.py](backend/routers/v1/resume_score.py): profile lookup and search

## Main Frontend Screens

- `/` landing page
- `/login` sign in
- `/register` create account
- `/forgot` request password reset
- `/reset-password` complete password reset
- `/verify-email` confirm email token
- `/dashboard` workspace overview
- `/score` upload and review CVs
- `/profile` view structured profile data
- `/search` search saved profiles
- `/sessions` manage active sessions

## Screenshots

### Login

The login screen provides the main entry point into the authenticated workspace and links directly to registration and password reset flows.

![Login screen](screenshots/Screenshot%202026-04-02%20222337.png)

### Register

The registration screen keeps onboarding minimal: email, password, and a short note explaining that email verification is required before protected features can be used.

![Register screen](screenshots/Screenshot%202026-04-02%20222348.png)

### Password Reset Request

This screen starts the password recovery flow by allowing an existing user to request a reset link by email.

![Password reset request screen](screenshots/Screenshot%202026-04-02%20222357.png)

### Dashboard / Workspace

The workspace dashboard summarizes the account state, the latest saved CV score snapshot, and the broader workflow supported by the application.

![Workspace dashboard](screenshots/Screenshot%202026-04-02%20222407.png)

### CV Review Upload

The CV review screen supports document upload and exposes the main actions: review a CV, save the score, run an advanced review, and generate a profile.

![CV review upload state](screenshots/Screenshot%202026-04-02%20222417.png)

### CV Review Results

After processing, the review screen displays the generated score breakdown together with highlights, strengths, and weaknesses extracted from the uploaded CV.

![CV review results](screenshots/Screenshot%202026-04-02%20222457.png)

### Profile View

The profile page turns CV-derived data into a structured profile with score summary, identity details, skill signals, experience history, and education.

![Profile view](screenshots/Screenshot%202026-04-02%20222512.png)

### Search

The search page combines text filters and score thresholds to surface stored profiles and make comparison easier.

![Search page](screenshots/Screenshot%202026-04-02%20222523.png)

### Sessions / Security

The sessions screen gives users visibility into active device sessions and lets them revoke individual sessions or sign out everywhere.

![Sessions page](screenshots/Screenshot%202026-04-02%20222534.png)

## Local Development

### Frontend only

```powershell
cd frontend/CV_GRAM
npm install
npm run dev
```

By default the frontend talks to `http://localhost:8000` during dev. You can override that with `VITE_API_BASE`.

### Backend only

Install backend dependencies in your virtual environment, then run:

```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Full stack on one port

Use the integrated runner:

```powershell
.\.venv\Scripts\python run_fullstack.py --host 127.0.0.1 --port 8000 --reload
```

This command:
- builds the Vue frontend
- copies the production bundle into the backend
- serves both the frontend and backend from the same origin and port

## Email Links

Verification and password reset emails now derive their public base URL from the incoming backend request. If the app is running on `http://localhost:8000`, the email links point there automatically. If you run it on another port, the links follow that port.

## Database SQL:

This SQL file contains all the necessary commands to initialize it to a new server:

- [design/database.sql](design\database.sql)

## Search Test Data

To seed extra users for profile search testing, use:

```powershell
psql -d your_database_name -f backend/db/seed_search_test_users.sql
```

The seed file is here:
- [backend/db/seed_search_test_users.sql](backend/db/seed_search_test_users.sql)
