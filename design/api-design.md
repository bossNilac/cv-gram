# API Design

This document describes the currently implemented API surface inferred from the backend routers and frontend API client.

## Base Structure

- Auth routes are exposed under `/auth`
- CV parsing and scoring routes are exposed under `/parser`
- Profile and search routes are exposed under `/profiles`
- Authentication is cookie-based through a `session` HTTP-only cookie
- Most protected routes require an active authenticated session

## Authentication API

### `POST /auth/register`
- Purpose: create a new account
- Auth required: no
- Request body:
```json
{
  "email": "name@example.com",
  "password": "string-with-min-8-chars"
}
```
- Success:
```json
{
  "email": "name@example.com"
}
```
- Notes:
- Creates an inactive user
- Sends email verification link

### `POST /auth/login`
- Purpose: authenticate a verified user and create a session
- Auth required: no
- Request body:
```json
{
  "email": "name@example.com",
  "password": "password"
}
```
- Success: `200 OK` with `session` cookie set
- Error cases:
- `401 Invalid credentials`

### `POST /auth/logout`
- Purpose: revoke current session
- Auth required: yes
- Success: `200 OK`, cookie deleted

### `POST /auth/me`
- Purpose: return current authenticated user account data
- Auth required: yes
- Success:
```json
{
  "email": "name@example.com",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### `POST /auth/password/forgot`
- Purpose: start password reset flow
- Auth required: no
- Request body:
```json
{
  "email": "name@example.com"
}
```
- Success: `200 OK`
- Notes:
- Returns success even if the email does not exist

### `POST /auth/password/reset`
- Purpose: complete password reset using reset token
- Auth required: no
- Request body:
```json
{
  "token": "reset-token",
  "new_password": "new-password"
}
```
- Success: `200 OK`
- Notes:
- Marks reset token as used
- Revokes all active sessions for the user

### `POST /auth/logout_all`
- Purpose: revoke all active sessions for current user
- Auth required: yes
- Success: `200 OK`, current session cookie deleted

### `DELETE /auth/sessions/{id}`
- Purpose: revoke one active session
- Auth required: yes
- Success: `200 OK`
- Notes:
- If revoking the current session, the cookie is deleted

### `GET /auth/sessions`
- Purpose: list active unrevoked, unexpired sessions
- Auth required: yes
- Success:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "created_at": "datetime",
    "expires_at": "datetime",
    "revoked_at": null,
    "ip": "string",
    "agent": "string"
  }
]
```

### `POST /auth/verify-mail`
- Purpose: verify email using token
- Auth required: no
- Request body:
```json
{
  "token": "verification-token"
}
```
- Success: `200 OK`

## Parser API

### `GET /parser/health`
- Purpose: basic parser service health and configuration visibility
- Auth required: no

### `GET /parser/adv/health`
- Purpose: advanced parser service health
- Auth required: no

### `POST /parser/resume/score`
- Purpose: score a CV without persisting the result
- Auth required: yes
- Content type: `multipart/form-data`
- Form fields:
- `file`: PDF, DOC, or DOCX
- Success:
```json
{
  "score": 78.4,
  "parsed": {
    "name": "Candidate Name",
    "email": "name@example.com",
    "skills": [],
    "overall_score": 78.4,
    "components": {
      "education": 70,
      "experience": 82,
      "skills": 80,
      "ai_signal": 76,
      "projects": 65
    },
    "weights": {},
    "confidence": 0.76,
    "explanation": {
      "highlights": [],
      "top_archetype_matches": [],
      "notes": {
        "strengths": [],
        "weaknesses": []
      }
    }
  }
}
```
- Error cases:
- `400` no file
- `413` file too large
- `415` unsupported type
- `422` unreadable, empty, corrupted, or not a CV
- `500` missing OpenAI config

### `PUT /parser/resume/score`
- Purpose: score a CV and persist score data into the user's profile record
- Auth required: yes
- Content type: `multipart/form-data`
- Behavior:
- Updates or creates score fields on the user's profile row

### `POST /parser/resume/adv/score_async`
- Purpose: start advanced asynchronous review
- Auth required: yes
- Content type: `multipart/form-data`
- Success:
```json
{
  "proc_id": "task-id",
  "status": "queued"
}
```

### `GET /parser/resume/task_status/{task_id}`
- Purpose: poll async task status
- Auth required: yes
- Success:
```json
{
  "proc_id": "task-id",
  "status": "queued|running|done|failed",
  "stage": "string",
  "progress": 35,
  "created_at": 0,
  "started_at": 0,
  "finished_at": 0,
  "adv": true,
  "filename": "resume.pdf"
}
```

### `GET /parser/resume/result/{task_id}`
- Purpose: fetch final async review result
- Auth required: yes
- Success: same response shape as synchronous scoring
- Error:
- `404` if result not ready

### `POST /parser/resume/cv`
- Purpose: generate and store structured profile JSON from CV
- Auth required: yes
- Content type: `multipart/form-data`
- Success:
```json
{
  "profile": {
    "basics": {},
    "experience": [],
    "education": [],
    "projects": [],
    "skills": []
  }
}
```

## Profiles API

### `GET /profiles/resume-scores`
- Purpose: get current user's stored CV scores
- Auth required: yes

### `GET /profiles/resume-scores/{user_id}`
- Purpose: get another user's stored CV scores
- Auth required: yes

### `GET /profiles/me`
- Purpose: get current user's stored profile record
- Auth required: yes

### `GET /profiles/user/{user_id}`
- Purpose: get another user's stored profile record
- Auth required: yes

### `GET /profiles/search/`
- Purpose: search stored profiles
- Auth required: yes
- Query parameters:
- `q_name`
- `q_location`
- `q_experience`
- `q_education`
- `limit`
- `offset`
- `overall_min`, `overall_max`
- `projects_min`, `projects_max`
- `experience_min`, `experience_max`
- `education_min`, `education_max`
- `skills_min`, `skills_max`
- Success:
```json
[
  {
    "user_id": "uuid",
    "overall_score": 82,
    "projects_score": 76,
    "experience_score": 84,
    "education_score": 70,
    "skills_score": 88,
    "profile_json": {},
    "rank": 0.94
  }
]
```

## Cross-Cutting Rules

- Authenticated endpoints depend on a valid non-expired, non-revoked session cookie
- Passwords have a minimum length of 8 characters
- Score values are bounded between 0 and 100
- Sensitive or expensive endpoints are rate limited
- File processing happens in memory
