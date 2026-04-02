BEGIN;

INSERT INTO public.users (id, email, password_hash, is_active, created_at, updated_at)
VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    'ana.mitchell@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '30 days',
    NOW() - INTERVAL '2 days'
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    'marcus.lee@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '28 days',
    NOW() - INTERVAL '3 days'
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    'sophia.alvarez@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '25 days',
    NOW() - INTERVAL '4 days'
  ),
  (
    '44444444-4444-4444-4444-444444444444',
    'daniel.okafor@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '22 days',
    NOW() - INTERVAL '5 days'
  ),
  (
    '55555555-5555-5555-5555-555555555555',
    'lena.petrov@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '20 days',
    NOW() - INTERVAL '6 days'
  ),
  (
    '66666666-6666-6666-6666-666666666666',
    'omar.haddad@cvgram.test',
    'seeded-user-no-login',
    TRUE,
    NOW() - INTERVAL '18 days',
    NOW() - INTERVAL '7 days'
  )
ON CONFLICT (id) DO UPDATE
SET
  email = EXCLUDED.email,
  is_active = EXCLUDED.is_active,
  updated_at = EXCLUDED.updated_at;

INSERT INTO public.profile (
  user_id,
  overall_score,
  projects_score,
  experience_score,
  education_score,
  skills_score,
  profile_json
)
VALUES
  (
    '11111111-1111-1111-1111-111111111111',
    86,
    88,
    84,
    82,
    90,
    '{
      "profile": {
        "basics": {
          "full_name": "Ana Mitchell",
          "headline": "Senior Backend Engineer",
          "email": "ana.mitchell@cvgram.test",
          "phone": "+49 30 555 0101",
          "location": "Berlin, Germany",
          "summary": "Backend engineer focused on Python, distributed systems, and platform reliability.",
          "urls": {
            "linkedin": "https://linkedin.com/in/ana-mitchell",
            "github": "https://github.com/anamitchell",
            "portfolio": "",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "Senior Backend Engineer",
            "company": "FlowStack",
            "employment_type": "Full-time",
            "location": "Berlin, Germany",
            "start_date": "2022-04",
            "end_date": null,
            "description": "Led backend services for document workflows and asynchronous processing.",
            "achievements": [
              "Reduced API latency by 34%",
              "Built resumable background processing for 2M monthly tasks"
            ]
          },
          {
            "title": "Backend Engineer",
            "company": "ScaleForge",
            "employment_type": "Full-time",
            "location": "Remote",
            "start_date": "2019-06",
            "end_date": "2022-03",
            "description": "Worked on Python microservices, PostgreSQL, and observability.",
            "achievements": [
              "Designed internal search APIs",
              "Improved deployment safety with automated checks"
            ]
          }
        ],
        "education": [
          {
            "school": "Technical University of Munich",
            "degree": "BSc",
            "field_of_study": "Computer Science",
            "start_date": "2015-10",
            "end_date": "2019-03",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Async Resume Pipeline",
            "role": "Lead Engineer",
            "start_date": "2023-01",
            "end_date": null,
            "url": "https://github.com/anamitchell/resume-pipeline",
            "description": "Pipeline for parsing and scoring CVs with background workers.",
            "highlights": ["Supports polling and result caching"],
            "tech": ["Python", "FastAPI", "PostgreSQL", "Redis"]
          }
        ],
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "System Design"],
        "certifications": [],
        "languages": [{"name": "English", "proficiency": "Fluent"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    78,
    74,
    80,
    76,
    79,
    '{
      "profile": {
        "basics": {
          "full_name": "Marcus Lee",
          "headline": "Data Analyst",
          "email": "marcus.lee@cvgram.test",
          "phone": "+1 415 555 0102",
          "location": "San Francisco, CA",
          "summary": "Analyst with strong SQL, BI, and experimentation experience.",
          "urls": {
            "linkedin": "https://linkedin.com/in/marcus-lee",
            "github": "https://github.com/marcuslee",
            "portfolio": "",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "Data Analyst",
            "company": "Northstar Retail",
            "employment_type": "Full-time",
            "location": "San Francisco, CA",
            "start_date": "2021-02",
            "end_date": null,
            "description": "Owned dashboards, funnel analysis, and experiment reporting.",
            "achievements": [
              "Improved campaign targeting with SQL-based segmentation",
              "Built BI dashboards for executive reporting"
            ]
          }
        ],
        "education": [
          {
            "school": "University of California, Davis",
            "degree": "BSc",
            "field_of_study": "Statistics",
            "start_date": "2016-09",
            "end_date": "2020-06",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Experiment Scorecard",
            "role": "Analyst",
            "start_date": "2022-09",
            "end_date": "2023-01",
            "url": "",
            "description": "Reusable KPI scorecard for A/B test reporting.",
            "highlights": ["Used by marketing and growth teams"],
            "tech": ["SQL", "Looker", "Python"]
          }
        ],
        "skills": ["SQL", "Python", "Looker", "A/B Testing", "Data Visualization", "Statistics"],
        "certifications": [],
        "languages": [{"name": "English", "proficiency": "Native"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  ),
  (
    '33333333-3333-3333-3333-333333333333',
    81,
    83,
    75,
    88,
    80,
    '{
      "profile": {
        "basics": {
          "full_name": "Sophia Alvarez",
          "headline": "Product Designer",
          "email": "sophia.alvarez@cvgram.test",
          "phone": "+34 91 555 0103",
          "location": "Madrid, Spain",
          "summary": "Product designer combining UX research, systems thinking, and interface craft.",
          "urls": {
            "linkedin": "https://linkedin.com/in/sophia-alvarez",
            "github": "",
            "portfolio": "https://portfolio.sophia.design",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "Product Designer",
            "company": "Orbit Health",
            "employment_type": "Full-time",
            "location": "Madrid, Spain",
            "start_date": "2021-08",
            "end_date": null,
            "description": "Led design for patient onboarding and scheduling experiences.",
            "achievements": [
              "Improved onboarding completion by 19%",
              "Created reusable design system patterns"
            ]
          }
        ],
        "education": [
          {
            "school": "IE University",
            "degree": "MA",
            "field_of_study": "Human-Centered Design",
            "start_date": "2019-09",
            "end_date": "2021-06",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Care Journey Redesign",
            "role": "Lead Designer",
            "start_date": "2023-02",
            "end_date": null,
            "url": "https://portfolio.sophia.design/care-journey",
            "description": "Case study for redesigning a healthcare scheduling flow.",
            "highlights": ["Full research-to-UI case study"],
            "tech": ["Figma", "UX Research", "Design Systems"]
          }
        ],
        "skills": ["Figma", "UX Research", "Interaction Design", "Design Systems", "Prototyping"],
        "certifications": [],
        "languages": [{"name": "Spanish", "proficiency": "Native"}, {"name": "English", "proficiency": "Fluent"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  ),
  (
    '44444444-4444-4444-4444-444444444444',
    73,
    68,
    77,
    70,
    76,
    '{
      "profile": {
        "basics": {
          "full_name": "Daniel Okafor",
          "headline": "DevOps Engineer",
          "email": "daniel.okafor@cvgram.test",
          "phone": "+44 20 555 0104",
          "location": "London, UK",
          "summary": "DevOps engineer focused on CI/CD, Kubernetes, and cloud infrastructure.",
          "urls": {
            "linkedin": "https://linkedin.com/in/daniel-okafor",
            "github": "https://github.com/danielokafor",
            "portfolio": "",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "DevOps Engineer",
            "company": "Stack Harbor",
            "employment_type": "Full-time",
            "location": "London, UK",
            "start_date": "2020-11",
            "end_date": null,
            "description": "Maintains cloud infrastructure, CI pipelines, and runtime monitoring.",
            "achievements": [
              "Cut release times from 45 minutes to 12 minutes",
              "Standardized Kubernetes deployment templates"
            ]
          }
        ],
        "education": [
          {
            "school": "University of Lagos",
            "degree": "BEng",
            "field_of_study": "Computer Engineering",
            "start_date": "2014-09",
            "end_date": "2019-07",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Cluster Cost Watch",
            "role": "Engineer",
            "start_date": "2023-05",
            "end_date": null,
            "url": "",
            "description": "Internal tool for tracking cluster and environment costs.",
            "highlights": ["Improved monthly cost visibility"],
            "tech": ["Terraform", "AWS", "Kubernetes", "Grafana"]
          }
        ],
        "skills": ["AWS", "Terraform", "Kubernetes", "GitHub Actions", "Docker", "Grafana"],
        "certifications": [],
        "languages": [{"name": "English", "proficiency": "Fluent"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  ),
  (
    '55555555-5555-5555-5555-555555555555',
    69,
    71,
    65,
    74,
    70,
    '{
      "profile": {
        "basics": {
          "full_name": "Lena Petrov",
          "headline": "Junior Frontend Developer",
          "email": "lena.petrov@cvgram.test",
          "phone": "+49 89 555 0105",
          "location": "Munich, Germany",
          "summary": "Frontend developer building Vue interfaces with a strong eye for component structure.",
          "urls": {
            "linkedin": "https://linkedin.com/in/lena-petrov",
            "github": "https://github.com/lenapetrov",
            "portfolio": "",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "Frontend Developer",
            "company": "Pixel Dock",
            "employment_type": "Full-time",
            "location": "Munich, Germany",
            "start_date": "2023-01",
            "end_date": null,
            "description": "Builds Vue views, form flows, and reusable UI components.",
            "achievements": [
              "Shipped profile and dashboard pages",
              "Improved design consistency across product surfaces"
            ]
          }
        ],
        "education": [
          {
            "school": "Munich University of Applied Sciences",
            "degree": "BSc",
            "field_of_study": "Media Informatics",
            "start_date": "2019-10",
            "end_date": "2023-07",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Vue Resume Explorer",
            "role": "Frontend Developer",
            "start_date": "2024-01",
            "end_date": null,
            "url": "https://github.com/lenapetrov/vue-resume-explorer",
            "description": "Frontend for browsing and filtering resume profiles.",
            "highlights": ["Responsive search interface"],
            "tech": ["Vue", "JavaScript", "CSS"]
          }
        ],
        "skills": ["Vue", "JavaScript", "CSS", "HTML", "Component Design"],
        "certifications": [],
        "languages": [{"name": "German", "proficiency": "Native"}, {"name": "English", "proficiency": "Fluent"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  ),
  (
    '66666666-6666-6666-6666-666666666666',
    84,
    79,
    87,
    83,
    86,
    '{
      "profile": {
        "basics": {
          "full_name": "Omar Haddad",
          "headline": "Machine Learning Engineer",
          "email": "omar.haddad@cvgram.test",
          "phone": "+971 4 555 0106",
          "location": "Dubai, UAE",
          "summary": "Machine learning engineer with NLP and recommendation system experience.",
          "urls": {
            "linkedin": "https://linkedin.com/in/omar-haddad",
            "github": "https://github.com/omarhaddad",
            "portfolio": "",
            "website": ""
          }
        },
        "experience": [
          {
            "title": "Machine Learning Engineer",
            "company": "SignalRank",
            "employment_type": "Full-time",
            "location": "Dubai, UAE",
            "start_date": "2021-04",
            "end_date": null,
            "description": "Develops NLP ranking models and production inference services.",
            "achievements": [
              "Raised relevance metrics by 11%",
              "Deployed model APIs with batch and realtime inference"
            ]
          }
        ],
        "education": [
          {
            "school": "American University of Beirut",
            "degree": "MSc",
            "field_of_study": "Computer Science",
            "start_date": "2018-09",
            "end_date": "2020-06",
            "grade": "",
            "activities": "",
            "description": ""
          }
        ],
        "projects": [
          {
            "name": "Resume Skill Matcher",
            "role": "ML Engineer",
            "start_date": "2024-02",
            "end_date": null,
            "url": "https://github.com/omarhaddad/resume-skill-matcher",
            "description": "Model pipeline for matching candidate skills to role clusters.",
            "highlights": ["Open-source experiment with vector search"],
            "tech": ["Python", "PyTorch", "FastAPI", "PostgreSQL"]
          }
        ],
        "skills": ["Python", "Machine Learning", "NLP", "PyTorch", "FastAPI", "Vector Search"],
        "certifications": [],
        "languages": [{"name": "Arabic", "proficiency": "Native"}, {"name": "English", "proficiency": "Fluent"}],
        "publications": [],
        "honors_awards": [],
        "volunteer": []
      }
    }'::jsonb
  )
ON CONFLICT (user_id) DO UPDATE
SET
  overall_score = EXCLUDED.overall_score,
  projects_score = EXCLUDED.projects_score,
  experience_score = EXCLUDED.experience_score,
  education_score = EXCLUDED.education_score,
  skills_score = EXCLUDED.skills_score,
  profile_json = EXCLUDED.profile_json;

COMMIT;
