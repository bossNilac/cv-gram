# Non-Functional Requirements

This section captures quality attributes and operational constraints that follow from the current implementation.

## Security

- Passwords must never be stored in plaintext.
- Session tokens, verification tokens, and password reset tokens must be stored as hashes, not raw values.
- Protected routes must reject requests without a valid active session.
- Session cookies should remain HTTP-only.
- Password reset must revoke all live sessions.
- Expired and revoked sessions must be rejected by the backend.

## Performance

- Standard page actions such as login, dashboard load, profile load, and session listing should feel interactive under normal local or hosted conditions.
- Synchronous CV review should complete fast enough for single-user interactive use, subject to file size and OpenAI latency.
- Advanced scoring should run asynchronously so the UI does not block while heavier analysis runs.
- Search should return the first page of results fast enough for iterative recruiter-style filtering.

## Reliability

- The application should fail with explicit errors for invalid input, expired tokens, unsupported files, unreadable files, and non-CV uploads.
- Email verification and password reset links should remain valid only within configured token lifetimes.
- If OpenAI or email delivery is unavailable, the backend should surface clear failure responses rather than silently succeeding.
- Stored profile and score data should remain available independently of the temporary frontend state.

## Scalability

- The system should support multiple concurrent authenticated users with isolated sessions and profile records.
- Search should be backed by the database rather than frontend filtering.
- Expensive AI processing should be rate limited and structured so it can later be moved to dedicated workers if needed.

## Usability

- The application should provide clear feedback for loading, success, and error states on all major screens.
- Auth flows should be understandable without manual support.
- Search results should expose enough information for quick scanning and comparison.
- CV review output should provide explanatory text, not only numeric scores.

## Maintainability

- Frontend routes and backend routers should remain separated by domain concerns.
- Request and response payloads should use explicit models where practical.
- The design should remain understandable enough that additional auth methods, richer search, or manual profile editing can be added later without major rewrites.

## Compatibility

- The frontend should work in modern browsers that support Vue 3 and standard cookie handling.
- The application should support local development with Vite and Uvicorn.
- The backend should work with PostgreSQL and the current Python package stack.

## Constraints

- Supported upload formats are limited to `PDF`, `DOC`, and `DOCX`.
- File extraction is text-based and may fail for scanned CVs requiring OCR.
- AI behavior depends on configured OpenAI models and keys.
- Email flows depend on SMTP configuration.
