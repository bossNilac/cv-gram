# Data Dictionary

This data dictionary summarizes the current persistent data model.

## `users`

- Purpose: stores account identity and account lifecycle state
- Key fields:
- `id`: UUID primary key
- `email`: user email address
- `password_hash`: Argon2 password hash
- `is_active`: email verification state
- `created_at`: account creation timestamp
- `updated_at`: last account update timestamp

## `sessions`

- Purpose: stores browser/device login sessions
- Key fields:
- `id`: session UUID
- `user_id`: owning user UUID
- `token_hash`: SHA-256 hash of raw session token
- `created_at`: session creation timestamp
- `expires_at`: session expiry time
- `revoked_at`: revocation timestamp, null when active
- `ip`: client IP at session creation
- `agent`: user agent string

## `email_verification`

- Purpose: stores email verification tokens
- Key fields:
- `id`: token UUID
- `user_id`: target user UUID
- `token_hash`: SHA-256 hash of verification token
- `created_at`: token creation time
- `expires_at`: token expiry time
- `used_at`: when token was consumed

## `password_reset_tokens`

- Purpose: stores password reset tokens
- Key fields:
- `id`: token UUID
- `user_id`: target user UUID
- `token_hash`: SHA-256 hash of reset token
- `created_at`: token creation time
- `expires_at`: token expiry time
- `used_at`: when token was consumed

## `profile`

- Purpose: stores scoring output and structured profile data for a user
- Key fields:
- `user_id`: UUID, one profile row per user
- `overall_score`: overall CV score
- `projects_score`: projects component score
- `experience_score`: experience component score
- `education_score`: education component score
- `skills_score`: skills component score
- `profile_json`: stored structured profile payload

## Derived and Search Data

- `profile_json` contains the generated structured candidate profile
- It is used to render the profile page and enrich search results
- Search depends on a database-side search function named `search_profiles_v3`
- Search results expose a `rank` field when applicable

## Data Lifecycle Notes

- A user is created inactive and becomes active after email verification
- A session is created on login and ends through expiry or revocation
- Password reset revokes all active sessions for the user
- CV scoring can update score fields even if profile JSON is still missing
- CV profile generation updates `profile_json` on the profile row
