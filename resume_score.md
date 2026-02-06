# EliteScore API — v1 (Extract: Resume Scores)

Base URL
--------
All endpoints are prefixed with `/v1`.

Content Types
-------------
- Request: application/json
- Response: application/json

Response Envelope
-----------------
Schema: ApiResponse<T>
{
  "success": boolean,
  "message": string | null,
  "data": T | null
}

Data Model
----------
ResumeScores
{
  "user_id": int,
  "overall_score": number,
  "projects_score": number,
  "experience_score": number,
  "education_score": number,
  "skills_score": number
}

==================================================
# Resource Path: /v1

## GET /v1/users/resume-scores
Summary: Get resume scoring breakdown for the authenticated user.
Auth: required
Response (200 OK):
{
  "user_id": int,
  "overall_score": number,
  "projects_score": number,
  "experience_score": number,
  "education_score": number,
  "skills_score": number
}
Errors:
- 404 Not Found — No resume scores found for the user

--------------------------------------------------
## GET /v1/users/resume-scores/{user_id}
Summary: Get resume scoring breakdown for a specific user.
Auth: none
Path Params:
- user_id (int)
Response (200 OK):
{
  "user_id": int,
  "overall_score": number,
  "projects_score": number,
  "experience_score": number,
  "education_score": number,
  "skills_score": number
}
Errors:
- 404 Not Found — No resume scores found for the user

==================================================

Examples — cURL
---------------

# Get my resume scores
curl -X GET "$BASE/v1/users/resume-scores" \
  -H "Authorization: Bearer <token>"

# Get resume scores by user ID
curl -X GET "$BASE/v1/users/resume-scores/42"
