# Search Design

## Purpose

Search allows authenticated users to discover stored profiles using text queries and score thresholds.

## Inputs

- Text inputs:
- `q_name`
- `q_location`
- `q_experience`
- `q_education`

- Numeric filters:
- `overall_min`, `overall_max`
- `projects_min`, `projects_max`
- `experience_min`, `experience_max`
- `education_min`, `education_max`
- `skills_min`, `skills_max`

- Paging:
- `limit`
- `offset`

## Processing Model

- The frontend sends filter state to `/profiles/search/`
- The backend forwards filters to the PostgreSQL function `search_profiles_v3`
- The database returns matched profile rows plus a `rank`
- The backend normalizes `profile_json` and returns the result list
- The frontend presents summary profile data, scores, and a link to the full profile

## Output Behavior

- When text filters are present, the UI treats `rank` as match relevance
- When text filters are not present, the UI falls back to positional ordering
- Search results display:
- full name where available
- headline where available
- location where available
- overall score
- top visible skills

## Design Notes

- Search depends on prior score persistence and profile generation to provide rich results
- The backend already supports more numeric filters than the current UI exposes
- Search should be treated as recruiter-style discovery rather than public browsing

## Improvement Opportunities

- Expose additional filters for projects and education score
- Add explicit sort options
- Add pagination controls in the UI
- Add search empty-state guidance
- Document the ranking strategy from the database function
