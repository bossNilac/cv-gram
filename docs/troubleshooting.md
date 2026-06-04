# Troubleshooting

## Frontend Cannot Reach Backend

Check that the backend is running on the expected port:

```powershell
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If running the frontend separately, confirm `VITE_API_BASE` points to the backend or that the frontend code is using the expected default backend URL.

## Email Verification or Password Reset Links Do Not Arrive

Check SMTP configuration:

- `MAIL_HOST`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_FROM`

Also confirm the backend can reach the SMTP provider and that the recipient address is valid.

## Upload Is Rejected

Supported file extensions are `PDF`, `DOC`, and `DOCX`. Rejections can happen when the file is too large, corrupted, unreadable, empty after text extraction, unsupported, or classified as not being a CV.

Check `CV_MAX_MB` if legitimate files are rejected for size.

## AI Scoring Fails

Confirm model configuration:

- `OPENAI_API_KEY`
- `OPENAI_ADV_API_KEY`
- `PRIMARY_MODEL`
- `ESCALATION_MODEL`
- `ADV_MODEL`

Also check backend logs for service errors, invalid JSON responses, or validation failures.

## Async Result Is Missing

Advanced scoring tasks are tracked in memory. Results are lost if the backend restarts before the task finishes or before the frontend retrieves the result.

## Search Returns Few or No Results

Search depends on stored profile rows. Generate or save profile data first, then seed additional test users if needed:

```powershell
psql -d your_database_name -f backend/db/seed_search_test_users.sql
```

## Integrated App Serves Old Frontend

Rebuild and copy the frontend bundle:

```powershell
.\.venv\Scripts\python run_fullstack.py --host 127.0.0.1 --port 8000 --reload
```

Avoid `--skip-build` when frontend files changed.
