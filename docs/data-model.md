# Data Model

CV_GRAM persists account, session, token, score, and profile data in PostgreSQL.

## `users`

Stores account identity and lifecycle state.

- `id`: user UUID.
- `email`: account email address.
- `password_hash`: Argon2 password hash.
- `is_active`: email verification state.
- `created_at`: creation timestamp.
- `updated_at`: update timestamp.

## `sessions`

Stores login sessions.

- `id`: session UUID.
- `user_id`: owning user UUID.
- `token_hash`: hash of the raw session token.
- `created_at`: session creation timestamp.
- `expires_at`: expiry timestamp.
- `revoked_at`: revocation timestamp.
- `ip`: client IP captured at session creation.
- `agent`: user agent captured at session creation.

## `email_verification`

Stores email verification tokens.

- `id`: token UUID.
- `user_id`: target user UUID.
- `token_hash`: hash of the raw verification token.
- `created_at`: creation timestamp.
- `expires_at`: expiry timestamp.
- `used_at`: token consumption timestamp.

## `password_reset_tokens`

Stores password reset tokens.

- `id`: token UUID.
- `user_id`: target user UUID.
- `token_hash`: hash of the raw reset token.
- `created_at`: creation timestamp.
- `expires_at`: expiry timestamp.
- `used_at`: token consumption timestamp.

## `profile`

Stores one profile record per user.

- `user_id`: owning user UUID.
- `overall_score`: overall CV score.
- `projects_score`: projects score.
- `experience_score`: experience score.
- `education_score`: education score.
- `skills_score`: skills score.
- `profile_json`: generated structured profile payload.

## Lifecycle Notes

- Users are inactive until email verification succeeds.
- Sessions end through expiry, logout, single-session revocation, logout-all, or password reset.
- CV score persistence can update score fields before structured profile JSON exists.
- Profile generation updates `profile_json`.
- Search uses score fields and generated profile content.
