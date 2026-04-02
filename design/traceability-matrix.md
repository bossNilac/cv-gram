# Traceability Matrix

This matrix maps major requirements to implementation areas.

| Requirement Area | Frontend | Backend | Data |
|---|---|---|---|
| Register account | `RegisterView.vue` | `auth_router.py -> /register` | `users`, `email_verification` |
| Verify email | `VerifyEmailView.vue` | `auth_router.py -> /verify-mail` | `users`, `email_verification` |
| Login/logout | `LoginView.vue`, navigation | `auth_router.py -> /login`, `/logout` | `sessions` |
| Forgot/reset password | `ForgotPassword.vue`, `ResetPasswordView.vue` | `auth_router.py -> /password/forgot`, `/password/reset` | `password_reset_tokens`, `sessions`, `users` |
| View account state | `DashboardView.vue` | `auth_router.py -> /me` | `users` |
| Session management | `SessionsView.vue` | `auth_router.py -> /sessions`, `/logout_all`, `DELETE /sessions/{id}` | `sessions` |
| CV score review | `ScoreResumeView.vue` | `parser.py -> /resume/score` | transient, optional `profile` |
| Save CV score | `ScoreResumeView.vue` | `parser.py -> PUT /resume/score` | `profile` |
| Async advanced scoring | `ScoreResumeView.vue` | `parser.py -> /resume/adv/score_async`, `/resume/task_status/{id}`, `/resume/result/{id}` | in-memory job store |
| Generate profile | `ScoreResumeView.vue` | `parser.py -> /resume/cv` | `profile.profile_json` |
| View own profile | `ProfileView.vue` | `resume_score.py -> /profiles/me` | `profile` |
| View another profile | `ProfileView.vue` | `resume_score.py -> /profiles/user/{user_id}` | `profile` |
| Search profiles | `SearchProfilesView.vue` | `resume_score.py -> /profiles/search/` | `profile`, DB search function |

## Coverage Notes

- Core requirements are implemented end-to-end for authentication, CV processing, score persistence, profile generation, and profile search.
- Some backend-supported filters are not fully exposed in the frontend UI.
- Some generated structured profile sections are stored but not fully rendered on profile screens.
