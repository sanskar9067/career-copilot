# Career Copilot — Backend

Django REST API that powers **Career Copilot**, an AI-assisted career platform. It handles user authentication, resume storage, RAG-based resume Q&A, ATS scoring, mock interview generation, and personalized career roadmap creation using OpenAI, LangChain, LangGraph, Qdrant, PostgreSQL, and Redis.

---

## Features

| Module | Description |
|--------|-------------|
| **User Auth** | Sign up and login with JWT-based authentication |
| **User Profile** | Upload resume (PDF) and store career details (current role, target role, experience) |
| **Resume Q&A** | Index resume into Qdrant vector store and answer questions via RAG + OpenAI |
| **ATS Score** | Analyze resume against current/target role and return an ATS-style score with feedback |
| **Interview Agent** | Generate a 10-question mock interview plan; evaluate answers and return structured feedback |
| **Roadmap Generator** | LangGraph multi-agent pipeline to build a learning roadmap and project ideas from resume + job description |

---

## Tech Stack

- **Framework:** Django 6.0, Django REST Framework
- **Database:** PostgreSQL
- **Cache / session store:** Redis (via `django-redis`)
- **Vector DB:** Qdrant (resume embeddings)
- **AI / LLM:** OpenAI (`gpt-4o-mini`, `gpt-5`), LangChain, LangGraph
- **Auth:** JWT (`PyJWT`) — custom implementation
- **CORS:** `django-cors-headers`

---

## Project Structure

```
careercopilot/
├── careercopilot/          # Django project settings, URLs, utilities
│   ├── settings.py
│   ├── urls.py
│   └── utils/
│       └── redis_client.py
├── user/                   # User registration & login
├── userinfo/               # Resume upload & profile data
├── resumeanalyzer/         # RAG indexing & retrieval (Qdrant)
├── atsscore/               # ATS resume scoring agent
├── intervieweragent/       # Mock interview plan & evaluation
├── roadmapgenerator/       # LangGraph career roadmap pipeline
├── manage.py
└── requirements.txt
```

---

## Prerequisites

Before running the backend, ensure the following services are available:

| Service | Purpose | Default URL |
|---------|---------|-------------|
| PostgreSQL | Primary database | `localhost:5432` |
| Redis | Interview plan caching | `localhost:6379` |
| Qdrant | Resume vector store | `http://localhost:6333` |
| OpenAI API | LLM & embeddings | Requires API key |

---

## Installation

### 1. Clone and enter the project

```bash
cd careercopilot
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the project root (or export variables in your shell):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

The app uses `python-dotenv` to load environment variables in agent modules.

### 5. Database setup

Update credentials in `careercopilot/settings.py` if needed (defaults shown below), then create the PostgreSQL database and run migrations:

```bash
# Create database (example)
createdb research_agent

python manage.py migrate
```

**Default database config** (`settings.py`):

| Setting | Value |
|---------|-------|
| Engine | PostgreSQL |
| Name | `research_agent` |
| User | `admin` |
| Password | `password123` |
| Host | `localhost` |
| Port | `5432` |

### 6. Start external services

```bash
# Redis
redis-server

# Qdrant (Docker example)
docker run -p 6333:6333 qdrant/qdrant
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Authentication

Protected endpoints require a JWT in the request header:

```
Authorization: Bearer <token>
```

Tokens are issued on successful login and encode the user's `user_id` using Django's `SECRET_KEY` and HS256.

**Public endpoints:** `signup/`, `login/`  
**Protected endpoints:** All others

---

## API Reference

Base URL: `http://127.0.0.1:8000`

### Auth

#### `POST /signup/`

Create a new user account.

**Request body (JSON):**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "yourpassword"
}
```

**Response `201`:**

```json
{ "message": "User created successfully" }
```

---

#### `POST /login/`

Authenticate and receive a JWT.

**Request body (JSON):**

```json
{
  "email": "jane@example.com",
  "password": "yourpassword"
}
```

**Response `200`:**

```json
{
  "message": "Login successful",
  "token": "<jwt_token>"
}
```

---

### User Profile

#### `POST /create_user_info/`

Upload resume and career profile. Requires auth.

**Request body (multipart/form-data):**

| Field | Type | Description |
|-------|------|-------------|
| `resume` | file | PDF resume |
| `current_role` | string | Current job title |
| `current_company` | string | Current employer |
| `target_role` | string | Desired job title |
| `years_of_experience` | integer | Years of experience |

**Response `201`:**

```json
{ "message": "User info created successfully" }
```

---

#### `PATCH /update_user_info/`

Update existing profile and resume. Same fields as create. Requires auth.

**Response `200`:**

```json
{ "message": "User info updated successfully" }
```

---

### Resume Analyzer (RAG Q&A)

#### `POST /index_resume/`

Chunk and embed the user's uploaded resume into a Qdrant collection named `resume_{user_id}`. Requires auth.

**Response `200`:**

```json
{ "message": "Resume indexed successfully" }
```

---

#### `POST /retrieve_resume/`

Ask a natural-language question about the indexed resume. Requires auth.

**Request body (JSON):**

```json
{
  "query": "What are my strongest technical skills?"
}
```

**Response `200`:**

```json
{
  "message": "Resume retrieved successfully",
  "response": "<JSON string from OpenAI>"
}
```

The AI agent returns structured JSON based on resume context retrieved via similarity search.

---

### ATS Score

#### `GET /score_resume/`

Score the user's resume against their current and target roles. Requires auth.

**Response `200`:**

```json
{
  "message": "Resume scored successfully",
  "score": "<JSON string with score, reason, and improvement tips>"
}
```

Uses `PyPDFLoader` to read the resume PDF and `gpt-4o-mini` for scoring.

---

### Interview Agent

#### `POST /interviewer_agent/`

Generate a personalized 10-question mock interview plan. Stores the plan in Redis under `interview_plan_{user_id}`. Requires auth.

**Request body (JSON):**

```json
{
  "job_description": "We are looking for a Senior Full Stack Engineer..."
}
```

**Response `200`:**

```json
{
  "message": "Interview plan generated successfully",
  "interview_plan": "<JSON string with 10 questions>"
}
```

Each question includes `id`, `category`, `difficulty`, and `question`.

---

#### `GET /get_interview_plan/`

Retrieve the cached interview plan from Redis. Requires auth.

**Response `200`:**

```json
{
  "message": "Interview plan retrieved successfully",
  "interview_plan": "<cached plan>"
}
```

---

#### `POST /generate_results/`

Evaluate the candidate's interview answers and return structured feedback. Requires auth.

**Request body (JSON):**

```json
{
  "job_description": "We are looking for a Senior Full Stack Engineer...",
  "answers": ["Answer to Q1", "Answer to Q2", "..."]
}
```

**Response `200`:**

```json
{
  "message": "Results generated successfully",
  "results": "<JSON with overall_score, strengths, weaknesses, question_wise_feedback, etc.>"
}
```

---

### Roadmap Generator

#### `POST /roadmap_generator/`

Run the LangGraph multi-agent pipeline to produce a personalized career roadmap. **This is a long-running request** (multiple LLM calls with web search). Requires auth.

**Request body (JSON):**

```json
{
  "job_description": "Senior Software Engineer role requiring Python, Django, AWS...",
  "user_query": "Focus on backend and system design",
  "duration": 10,
  "hours_per_day": 8
}
```

`current_role` and `target_role` are read from the user's profile.

**Response `200`:**

```json
{
  "user_id": 1,
  "current_role": "Systems Engineer",
  "target_role": "Generative AI Engineer",
  "job_description": "...",
  "duration": 10,
  "hours_per_day": 8,
  "user_query": "...",
  "skills": "...",
  "required_skills": "...",
  "market_demand": "...",
  "roadmap": "...",
  "project_ideas": "...",
  "result": "true | false with reason"
}
```

---

## AI Agents & Pipelines

### Resume Q&A (`resumeanalyzer/`)

1. **Indexing** — PDF is loaded, split into chunks (1000 chars, 200 overlap), embedded with `text-embedding-3-small`, stored in Qdrant.
2. **Retrieval** — User query triggers similarity search; relevant chunks are passed to `gpt-5` with a resume-analysis system prompt.

### ATS Score (`atsscore/`)

Loads resume PDF, sends content to `gpt-4o-mini` with ATS scoring criteria based on current/target role. Returns JSON score with reasoning and improvement suggestions.

### Interview Agent (`intervieweragent/`)

- **Plan generation** — `gpt-4o-mini` produces exactly 10 structured interview questions aligned with resume, roles, and job description.
- **Evaluation** — `gpt-4o-mini` scores answers across communication, technical, and problem-solving dimensions with per-question feedback.

### Roadmap Generator (`roadmapgenerator/`)

LangGraph state machine with the following sequential pipeline:

```
START
  → extract_skills          (RAG from Qdrant + gpt-4o-mini)
  → extract_required_skills (job description analysis)
  → extract_market_demand   (web search enabled)
  → generate_roadmap        (gpt-5 + web search)
  → generate_project_ideas  (gpt-5 + web search)
  → generate_result         (feasibility check)
  → [if result == "false"] regenerate roadmap, else END
```

---

## Data Models

### `User`

| Field | Type |
|-------|------|
| `first_name` | CharField |
| `last_name` | CharField |
| `email` | EmailField (unique) |
| `password` | CharField |
| `created_at` | DateTimeField |
| `updated_at` | DateTimeField |

### `UserInfo`

| Field | Type |
|-------|------|
| `user` | ForeignKey → User |
| `resume` | FileField (`resume/`) |
| `current_role` | CharField |
| `current_company` | CharField |
| `target_role` | CharField |
| `years_of_experience` | IntegerField |

---

## CORS

CORS is enabled for local frontend development:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

---

## Error Handling

Most endpoints return errors in this shape:

```json
{
  "message": "Human-readable error description",
  "error": "Detailed exception message"
}
```

Roadmap generator errors return a plain string body with HTTP `500`.

---

## Notes

- **Long requests:** The roadmap generator can take several minutes due to multiple sequential LLM + web search calls. Clients should use direct requests to Django (not a short-timeout proxy) or implement async job polling for production.
- **Resume format:** Resume indexing and ATS scoring expect PDF files.
- **Qdrant collections:** One collection per user — `resume_{user_id}`. Re-indexing overwrites the collection.
- **Redis keys:** Interview plans are cached as `interview_plan_{user_id}`.
- **Security:** Passwords are stored in plain text in the current implementation. JWT secret uses Django `SECRET_KEY`. Do not use as-is in production without hashing passwords and securing secrets.

---

## License

See repository root for license information.
