# Assumptions and Limitations

## Assumptions

- Each user has at most one persistent profile record keyed by `user_id`.
- Users interact primarily through the browser frontend.
- Email verification is required before login is useful for protected features.
- CV uploads are expected to contain machine-readable text or text extractable from supported document formats.
- Search is intended for authenticated users only.
- Structured profile generation is derived from the CV and is not manually curated in the current implementation.

## Product Limitations

- There is no manual editing workflow for generated profile content.
- There is no public profile publishing flow for anonymous visitors.
- There are no social or networking features such as messaging or endorsements.
- There is no administrator portal or team workspace model.
- There is no mobile app.

## Technical Limitations

- `DOC` support depends on legacy parsing tooling and may be less reliable than `PDF` or `DOCX`.
- OCR support is not implemented for scanned image-based CVs.
- Advanced async processing is in-process job tracking, not a durable queue-backed worker architecture.
- Search quality depends on the behavior of the database search function and the completeness of stored profile JSON.
- AI output quality depends on model configuration, prompt quality, and source CV quality.
- The frontend currently surfaces only part of the structured profile schema.

## Operational Limitations

- Email flows depend on valid SMTP configuration.
- AI flows depend on valid OpenAI API keys and reachable external services.
- Full security posture depends on environment configuration, especially HTTPS and cookie settings in production.
