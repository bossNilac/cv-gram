# AI Processing

The AI-processing subsystem scores CVs and generates structured profile data from uploaded documents.

## Capabilities

- Detect whether an uploaded document is a CV.
- Score CVs across education, experience, skills, projects, and AI signal.
- Generate highlights, strengths, weaknesses, and explanatory notes.
- Generate structured profile JSON for profile rendering and search enrichment.
- Support a longer-running advanced review through in-memory async task tracking.

## Processing Stages

1. Receive uploaded file.
2. Validate extension and size.
3. Extract text from `PDF`, `DOC`, or `DOCX`.
4. Reject empty, unreadable, corrupted, oversized, unsupported, or non-CV content.
5. Send extracted text and scoring instructions to the configured model.
6. Validate the returned structure.
7. Normalize and clamp score values.
8. Persist score fields or profile JSON when requested.
9. Return the result to the frontend.

## Models and Configuration

The backend reads model settings from environment-backed configuration:

- `PRIMARY_MODEL`
- `ESCALATION_MODEL`
- `ADV_MODEL`
- `AUTO_ESCALATE`
- `MIN_CONFIDENCE`
- `OPENAI_API_KEY`
- `OPENAI_ADV_API_KEY`

The primary model handles normal scoring. Escalation can be used when confidence is below the configured threshold. The advanced model is used by the longer asynchronous review path.

## Async Review

Advanced review creates an in-memory task record and returns a process ID. The frontend polls task status and retrieves the result when the task reaches `done`.

This is suitable for local development and small single-process runs. It is not durable across backend restarts and is not a replacement for a queue-backed worker system.

## Limitations

- Scanned image-only CVs are not supported without OCR.
- AI output quality depends on model behavior, prompt quality, and input CV quality.
- Weakly structured CVs may produce lower-confidence extraction.
- Advanced async tasks are not persisted.
