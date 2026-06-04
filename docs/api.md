# API

The FastAPI backend exposes three main route groups.

## Route Groups

- `/auth`: account, email verification, password reset, login/logout, and sessions.
- `/parser`: CV upload, scoring, async scoring, task status, result retrieval, and profile generation.
- `/profiles`: stored score lookup, profile lookup, and profile search.

Authentication is based on an HTTP-only `session` cookie. Protected routes require an active session for a verified user.

## Authentication

| Method | Route | Purpose | Auth |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Create an inactive account and send verification email | No |
| `POST` | `/auth/login` | Create a session for a verified user | No |
| `POST` | `/auth/logout` | Revoke the current session | Yes |
| `POST` | `/auth/logout_all` | Revoke all active sessions | Yes |
| `POST` | `/auth/me` | Return current account data | Yes |
| `GET` | `/auth/sessions` | List active sessions | Yes |
| `DELETE` | `/auth/sessions/{id}` | Revoke one session | Yes |
| `POST` | `/auth/verify-mail` | Verify an email token | No |
| `POST` | `/auth/password/forgot` | Request a password reset email | No |
| `POST` | `/auth/password/reset` | Complete password reset | No |

## Parser

| Method | Route | Purpose | Auth |
| --- | --- | --- | --- |
| `GET` | `/parser/health` | Basic parser health | No |
| `GET` | `/parser/adv/health` | Advanced parser health | No |
| `POST` | `/parser/resume/score` | Score a CV without persistence | Yes |
| `PUT` | `/parser/resume/score` | Score a CV and persist score fields | Yes |
| `POST` | `/parser/resume/adv/score_async` | Start advanced async scoring | Yes |
| `GET` | `/parser/resume/task_status/{task_id}` | Poll async task state | Yes |
| `GET` | `/parser/resume/result/{task_id}` | Fetch completed async result | Yes |
| `POST` | `/parser/resume/cv` | Generate and store structured profile JSON | Yes |

CV upload endpoints use `multipart/form-data` with a `file` field.

## Profiles

| Method | Route | Purpose | Auth |
| --- | --- | --- | --- |
| `GET` | `/profiles/resume-scores` | Get current user's stored scores | Yes |
| `GET` | `/profiles/resume-scores/{user_id}` | Get another user's stored scores | Yes |
| `GET` | `/profiles/me` | Get current user's stored profile | Yes |
| `GET` | `/profiles/user/{user_id}` | Get another user's stored profile | Yes |
| `GET` | `/profiles/search/` | Search stored profiles | Yes |

Search accepts text filters such as name, location, experience, and education, plus score bounds for overall, projects, experience, education, and skills.

## Error Cases

Common upload errors include:

- `400`: no file provided.
- `413`: file too large.
- `415`: unsupported file type.
- `422`: unreadable, empty, corrupted, or not a CV.
- `500`: missing or failing model/service configuration.
