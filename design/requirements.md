# CV_GRAM Requirements

This document is inferred from the current implementation in the backend, frontend, and existing README. It reflects what the product is designed to support today.

## 1. User Requirements

### 1.1 Public and onboarding requirements
- Users must be able to land on a public home page that explains the product and routes them to registration or login.
- Users must be able to create an account with an email address and password.
- Users must verify their email address before they can use protected CV and profile features.
- Users must be able to log in with valid credentials.
- Users must be able to request a password reset if they forget their password.
- Users must be able to set a new password from a reset link.

### 1.2 Account and session requirements
- Authenticated users must be able to view basic account information such as email, verification state, and account timestamps.
- Authenticated users must be able to sign out from the current device.
- Authenticated users must be able to view active sessions.
- Authenticated users must be able to revoke individual sessions.
- Authenticated users must be able to revoke all sessions at once.

### 1.3 CV review requirements
- Authenticated users must be able to upload a CV in `PDF`, `DOC`, or `DOCX` format.
- Users must be able to run an AI-assisted CV review and receive an overall score.
- Users must be able to see component scores for education, experience, skills, projects, and AI signal.
- Users must be able to review generated highlights, strengths, and weaknesses for a CV.
- Users must be informed when an uploaded file is invalid, unreadable, unsupported, too large, or not a CV.
- Users must be able to run an advanced asynchronous review and track its progress.

### 1.4 Profile generation and storage requirements
- Users must be able to save CV scoring results to their account.
- Users must be able to generate a structured profile from an uploaded CV.
- Users must be able to view their own structured profile.
- Users must be able to view another user’s stored profile by profile identifier.
- Structured profiles must expose identity, summary, skills, experience, education, and projects when available.

### 1.5 Search and discovery requirements
- Authenticated users must be able to search stored profiles.
- Users must be able to search using text filters such as name, location, experience text, and education text.
- Users must be able to filter by minimum or bounded score values.
- Users must be able to open a result and inspect the related profile.
- Search results must show enough profile summary information to support candidate comparison.

## 2. System Requirements

### 2.1 Frontend requirements
- The system must provide a browser-based frontend implemented with Vue 3 and Vue Router.
- The frontend must expose routes for landing, login, registration, forgot password, reset password, email verification, dashboard, CV review, profile view, profile search, and sessions.
- The frontend must maintain authenticated requests through cookie-based sessions.
- The frontend must redirect unauthenticated users to the login page when protected requests return `401`.
- The frontend must support both development API routing and same-origin production deployment.

### 2.2 Backend and API requirements
- The system must provide a FastAPI backend.
- The backend must expose authentication endpoints for register, login, logout, logout all, session listing, single-session revocation, password reset request, password reset completion, and email verification.
- The backend must expose profile endpoints for the current user profile, another user profile, current user scores, another user scores, and profile search.
- The backend must expose parser endpoints for health checks, synchronous CV scoring, persistent CV scoring, advanced asynchronous scoring, async task polling, async result retrieval, and structured profile generation.
- Protected endpoints must require an active authenticated session.

### 2.3 Security and identity requirements
- Passwords must be hashed using Argon2.
- Authentication must be backed by HTTP-only session cookies.
- The system must store and validate session expiry and session revocation status.
- Email verification tokens and password reset tokens must be generated securely, stored as hashes, and expire after a defined lifetime.
- Password reset must invalidate existing active sessions.
- The system must rate limit authentication and CV processing endpoints.

### 2.4 Data and persistence requirements
- The system must persist users, sessions, email verification tokens, password reset tokens, and profile records in PostgreSQL.
- The system must persist CV score components and overall score for each profile record.
- The system must persist structured profile JSON for profile display and search enrichment.
- The system must support ranked profile search through a database-side search function.

### 2.5 CV processing and AI requirements
- The system must parse uploaded CV files in memory.
- The system must validate file extension and reject unsupported types.
- The system must reject corrupted or unreadable files before or during parsing.
- The system must extract text from supported file types before AI evaluation.
- The AI evaluation flow must determine whether the uploaded document is a CV.
- The AI evaluation flow must generate structured scoring output and explanatory content.
- The system must support a primary model and an escalation path for lower-confidence results.
- The system must support advanced asynchronous scoring jobs with server-side job tracking.
- The system must generate a LinkedIn-style structured profile representation from CV content.

### 2.6 Deployment and operational requirements
- The system must support local frontend development through Vite.
- The system must support local backend development through Uvicorn.
- The system must support a full-stack run mode that builds the frontend and serves it from the backend on one port.
- The system must support SMTP-based email delivery for verification and password reset flows.
- Email links must derive their public base URL from the incoming request context.

## 3. User Stories

- As a visitor, I want to understand what CV_GRAM does from the landing page so that I can decide whether to register.
- As a new user, I want to register with my email and password so that I can access protected features.
- As a new user, I want to verify my email so that my account becomes active.
- As a returning user, I want to log in securely so that I can access my dashboard and stored profile data.
- As a user who forgot my password, I want to request a reset email so that I can regain access to my account.
- As a user resetting my password, I want all previous sessions revoked so that my account is secure after the change.
- As an authenticated user, I want to upload my CV so that the platform can assess it.
- As an authenticated user, I want an overall CV score and component scores so that I can understand my strengths and weaknesses.
- As an authenticated user, I want explanatory highlights, strengths, and weaknesses so that the score is actionable.
- As an authenticated user, I want to save my CV score so that I can reuse it later in my profile and search workflows.
- As an authenticated user, I want to generate a structured professional profile from my CV so that I can present my information in a searchable way.
- As an authenticated user, I want to view my structured profile so that I can inspect what has been extracted and stored.
- As an authenticated user, I want to view another stored profile so that I can compare candidates or profiles.
- As an authenticated user, I want to search profiles by text and score thresholds so that I can find relevant people faster.
- As an authenticated user, I want ranked search results so that I can prioritize the most relevant profiles.
- As an authenticated user, I want to see and revoke active sessions so that I can manage account access across devices.
- As an advanced user, I want to run a longer asynchronous review so that more intensive CV analysis can complete without blocking the UI.

## 4. MoSCoW Prioritization

### Must Have
- User registration, login, logout, and authenticated session handling.
- Email verification before access to protected features.
- Password reset request and password reset completion.
- Secure password hashing and token handling.
- Active session listing and revocation.
- CV upload with support for `PDF`, `DOC`, and `DOCX`.
- Validation for unsupported, unreadable, corrupted, oversized, or non-CV uploads.
- AI-based CV scoring with overall and component scores.
- Storage of CV scores in the user profile record.
- Generation and storage of structured profile data from a CV.
- Viewing the current user profile and another stored user profile.
- Search over stored profiles with text and numeric score filters.
- PostgreSQL persistence for users, sessions, tokens, and profile records.
- FastAPI backend and Vue frontend integrated into a working full-stack application.

### Should Have
- Dashboard view summarizing account state, latest score snapshot, and session count.
- Highlights, strengths, and weaknesses in CV review output.
- Advanced asynchronous CV review with task status polling and result retrieval.
- Ranked search output that reflects match relevance when text filters are used.
- Profile pages that show experience, education, projects, and skills in a readable form.
- Request-derived public base URLs for email links.
- Rate limiting on sensitive or expensive endpoints.

### Could Have
- More detailed search filters for additional structured profile fields.
- Pagination and richer sorting controls on search results.
- Better distinction between candidate types, industries, or role families in search UX.
- OCR support for scanned CVs that currently fail text extraction.
- Expanded profile sections such as awards, certifications, volunteer work, and publications surfaced more fully in the UI.
- Better admin or recruiter workflows around reviewing many profiles in sequence.

### Won't Have For Now
- Public anonymous access to stored user profiles.
- Manual profile editing independent of CV upload and extraction.
- Native mobile applications.
- Social networking features such as messaging, endorsements, or connection graphs.
- Multi-tenant administration, team workspaces, or role-based access control beyond the current authenticated-user model.
- Non-email authentication methods such as SSO, OAuth login providers, or MFA.
