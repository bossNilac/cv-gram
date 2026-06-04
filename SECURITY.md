# Security Policy

CV_GRAM handles account credentials, uploaded CV files, generated profile data, and AI-processing results. Treat all local test data as sensitive unless it is explicitly synthetic.

## Security Model

- Authentication uses HTTP-only session cookies.
- Raw session tokens are hashed before storage.
- Passwords are hashed with Argon2.
- Email verification and password reset tokens are stored as hashes and expire.
- Password reset revokes existing active sessions for the affected account.
- Protected CV, profile, search, and session routes require an active authenticated session.
- Authentication and CV-processing routes are rate limited.

## External Services

The app can depend on:

- PostgreSQL for account, session, score, and profile persistence.
- SMTP for email verification and password reset delivery.
- OpenAI-compatible model access for CV scoring and profile generation.

Do not commit service credentials or real production configuration.

## Reporting Security Issues

Report security issues privately to the repository owner instead of opening a public issue with sensitive details.

When reporting, include:

- A short description of the issue.
- Steps to reproduce.
- Affected route, screen, or data flow.
- Whether the issue requires a specific browser, database state, or environment variable.

Do not post passwords, session cookies, reset tokens, verification tokens, API keys, private CVs, or real profile data publicly.

## Known Improvement Targets

- Review CSRF protection for cookie-authenticated state-changing routes.
- Enable secure cookies in production behind HTTPS.
- Add a production deployment checklist before hosting real user data.
- Consider durable async job storage if advanced scoring is used beyond local development.
