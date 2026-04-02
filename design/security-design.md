# Security Design

This document summarizes the security-relevant design choices visible in the implementation.

## Authentication Model

- Authentication is session-based, not JWT-based in current user-facing flows.
- On successful login, the backend creates a raw session token, stores only its SHA-256 hash, and sends the raw token back in an HTTP-only cookie.
- Authenticated routes validate:
- session token exists
- token hash matches a stored session
- session is not revoked
- session is not expired
- owning user exists and is active

## Password Security

- Passwords are hashed with Argon2.
- Password length is validated with a minimum of 8 characters.
- Password verification uses Argon2 hash verification.

## Token Security

- Email verification and password reset tokens are generated randomly.
- Only token hashes are stored in the database.
- Tokens have expiry timestamps.
- Tokens are single-use through `used_at`.

## Session Security

- Sessions store metadata such as IP and user agent for user visibility.
- Users can revoke one session or all sessions.
- Password reset revokes all active sessions for the affected user.
- Current-session revocation clears the browser cookie.

## Abuse Controls

- Registration, login, password reset, verification, and CV parsing endpoints are rate limited.
- Heavier CV-processing endpoints have stricter limits than general account actions.

## File Handling Security

- Uploads are processed in memory.
- File type is checked by extension and optionally by MIME sniffing.
- Unsupported, corrupted, oversized, or unreadable uploads are rejected.
- Non-CV documents are rejected by the AI classification stage.

## External Dependency Risks

- OpenAI availability and model behavior directly affect CV scoring and profile generation.
- SMTP availability affects registration and password recovery completion.
- Search relies on database-side logic not fully documented in code comments.

## Current Security Gaps / Improvement Targets

- Session cookie `secure` is currently disabled in code and should be enabled in production behind HTTPS.
- CSRF protections are not explicitly visible and should be reviewed for cookie-authenticated POST routes.
- There is no MFA, OAuth, or SSO support.
- There is no explicit audit log beyond session records.
- There is no visible role-based authorization model beyond authenticated user access.
