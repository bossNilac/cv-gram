# README Proposal

This is a proposed direction for the root `README.md`. The current root README has not been changed.

## Recommended README Shape

```text
# CV_GRAM

Short one-paragraph product summary.

Badges, only if useful.

## Preview
Screenshots grouped by workflow.

## Features
Concise bullets for account/auth, CV scoring, profile generation, search, and sessions.

## How It Works
Short explanation of frontend -> backend -> AI processing -> PostgreSQL.

## Stack
Frontend, backend, database, AI, email.

## Local Development
Link to docs/setup.md and include the three most common commands.

## Project Structure
Link to backend, frontend, docs, run_fullstack.py.

## Documentation
Links to docs/architecture.md, docs/api.md, docs/data-model.md, docs/ai-processing.md, docs/troubleshooting.md, SECURITY.md, CONTRIBUTING.md.

## Security and Privacy Notes
Short notes only, with a link to SECURITY.md.
```

## Proposed GitHub Description

Full-stack CV review and profile search app built with Vue, FastAPI, PostgreSQL, and AI-assisted resume scoring.

## Proposed Short README Intro

CV_GRAM is a full-stack CV review and profile search platform. It lets authenticated users upload CVs, receive AI-assisted scoring, generate structured profile data, and search saved profiles using score and text signals.

The project is built as a practical coding portfolio application: Vue on the frontend, FastAPI on the backend, PostgreSQL for persistence, SMTP for account emails, and OpenAI-backed processing for CV review and profile extraction.

## Notes Before Rewriting

- Keep the root README shorter than the current version.
- Move detailed API, data, setup, and AI behavior into `docs/`.
- Keep screenshots in the README because they make the project easier to evaluate quickly.
- Decide whether to move `screenshots/` into `docs/screenshots/`; doing that also requires updating image links.
