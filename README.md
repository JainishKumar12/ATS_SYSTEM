# 🎯 ATS Resume Scorer

An AI-powered resume analysis platform that scores resumes against real ATS (Applicant Tracking System) criteria, validates claimed skills against actual project/experience evidence, and generates downloadable PDF reports — built as a full-stack system with a FastAPI backend and a Streamlit frontend.

**Live app:** [atssystem-kj79p5gqf5arufhf4a9u7z.streamlit.app](https://atssystem-kj79p5gqf5arufhf4a9u7z.streamlit.app/)
**Repository:** [github.com/JainishKumar12/ATS_SYSTEM](https://github.com/JainishKumar12/ATS_SYSTEM)

---

## ✨ Features

- **Multi-category ATS scoring** — resumes are scored across 5 weighted categories: formatting, keywords, content quality, skill validation, and ATS compatibility.
- **LLM-powered resume parsing** — Groq API extracts structured data (skills, projects, experience, education) from raw resume text.
- **Embedding-based skill validation** — sentence-transformers cross-reference every claimed skill against project/experience descriptions to flag unsupported claims, instead of relying on naive keyword matching.
- **Job description matching** — optional JD comparison mode computes semantic similarity, matched/missing keywords, and skill gaps against a specific job posting.
- **Actionable feedback engine** — rule-based issue detection (missing sections, weak action verbs, unquantified achievements, thin skill evidence) with severity-ranked, fix-it-style recommendations.
- **Downloadable PDF reports** — multi-page reports generated with Jinja2 + WeasyPrint, covering score breakdown, skill validation, JD analysis, and a prioritized action-item checklist.
- **Authenticated history** — Google OAuth / email sign-in via Supabase, with persistent analysis history per user.

---

## 🏗️ Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Streamlit Frontend │ ──────▶ │    FastAPI Backend    │
│   (Streamlit Cloud)  │  HTTPS  │      (Railway)        │
└─────────────────────┘         └──────────┬───────────┘
                                            │
                ┌───────────────────────────┼───────────────────────────┐
                ▼                           ▼                           ▼
        ┌───────────────┐         ┌─────────────────┐         ┌────────────────┐
        │   Groq API     │         │  spaCy + Sentence │         │    Supabase     │
        │ (LLM parsing & │         │  Transformers      │         │ (Auth, History, │
        │   scoring)     │         │ (skill validation) │         │   Postgres DB)  │
        └───────────────┘         └─────────────────┘         └────────────────┘
```

**Backend** (`backend/`) — FastAPI application exposing `/api/v1/analyze-resume`, `/api/v1/generate-pdf`, `/api/v1/history`, and auth-protected endpoints. Resume parsing and scoring logic, the skill-validation embedding pipeline, the rule-based feedback engine, and Jinja2/WeasyPrint report generation all live here.

**Frontend** (`frontend/`) — Multi-page Streamlit application (Home, ATS Scorer, History, Resources) with Supabase-backed authentication (email/password + Google OAuth), file upload, results dashboard, and PDF/summary export.

**Database** — Supabase (Postgres) for user authentication and persistent analysis history.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI, Uvicorn |
| LLM / NLP | Groq API, spaCy, Sentence-Transformers, NLTK |
| Frontend | Streamlit |
| Database & Auth | Supabase (Postgres, Google OAuth) |
| PDF Generation | Jinja2, WeasyPrint |
| Deployment | Railway (backend, Railpack builder), Streamlit Cloud (frontend) |

---

## 📁 Project Structure

```
ATS_SYSTEM/
├── backend/
│   ├── api/
│   │   ├── auth.py               # Supabase JWT auth dependency
│   │   └── routes.py             # API endpoints (analyze, PDF export, history)
│   ├── core/
│   │   └── config.py             # App-wide configuration / settings
│   ├── database/
│   │   └── supabase_db.py        # History persistence
│   ├── logs/
│   │   └── ats_scorer.log        # Application logs
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── services/
│   │   ├── ats_scorer.py         # Scoring + skill validation logic
│   │   ├── feedback_engine.py    # Rule-based issue detection
│   │   ├── groq_parser.py        # LLM-based resume/JD parsing
│   │   ├── jd_matcher.py         # Job description comparison
│   │   ├── pdf_export.py         # WeasyPrint PDF generation
│   │   ├── recommendation_engine.py  # Suggestion/recommendation generation
│   │   ├── report_generator.py   # Jinja2 HTML report rendering
│   │   ├── resume_analyzer.py    # Pipeline orchestrator
│   │   ├── resume_parser.py      # File parsing (PDF/DOCX → text)
│   │   └── utils/
│   │       ├── file_utils.py     # File handling helpers, default fallback results
│   │       └── matching.py       # Shared matching/comparison helpers
│   ├── templates/                # Jinja2 HTML templates for PDF reports
│   │   ├── action_items.html
│   │   ├── jd_comparison.html
│   │   ├── quick_actions.html
│   │   └── summary.html
│   └── main.py                   # FastAPI app entrypoint
├── frontend/
│   ├── .streamlit/
│   │   ├── config.toml           # Streamlit theme/app config
│   │   └── secrets.toml          # Local secrets (gitignored)
│   ├── assets/
│   │   └── style.css             # Custom CSS for the Streamlit UI
│   ├── components/
│   │   ├── _helpers.py           # Shared formatting/styling helpers
│   │   ├── action_items.py
│   │   ├── dashboard.py          # Results dashboard orchestrator
│   │   ├── detailed_feedback.py
│   │   ├── jd_comparison.py
│   │   ├── recommendations.py
│   │   ├── score_display.py
│   │   ├── skill_validation.py
│   │   └── strengths_issues.py
│   ├── mlmodel/                  # Local ML assets used by the frontend
│   ├── services/
│   │   ├── api_client.py         # Backend HTTP client
│   │   └── supabase_client.py    # Auth client
│   ├── views/
│   │   ├── history.py
│   │   ├── landing.py
│   │   ├── resources.py
│   │   └── scorer.py             # Main analysis page
│   └── streamlit_app.py          # App entrypoint / router
├── .env                          # Local environment variables (gitignored)
├── .gitignore
├── railway.json                  # Railway deployment configuration
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- A [Groq API key](https://console.groq.com)
- A [Supabase](https://supabase.com) project (Postgres + Auth enabled)
- Google OAuth credentials (if using Google sign-in)

### 1. Clone the repository

```bash
git clone https://github.com/JainishKumar12/ATS_SYSTEM.git
cd ATS_SYSTEM
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
# Groq
GROQ_API_KEY=your_groq_api_key

# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Google OAuth (for sign-in)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

> ⚠️ Double-check the exact Supabase variable names against your `supabase_client.py` / config — adjust above if your code expects different names.

### 3. Install dependencies

```bash
pip install -r requirements.txt --break-system-packages
python -m spacy download en_core_web_sm
```

### 4. Run the backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Run the frontend

```bash
streamlit run frontend/streamlit_app.py
```

The app will be available at `http://localhost:8501`, talking to the backend at `http://localhost:8000`.

---

## ☁️ Deployment Notes

- **Backend (Railway):** Built with Railpack (see `railway.json` for deployment configuration). PDF generation (WeasyPrint) requires system-level libraries not included by default — set the following environment variable in Railway to install them at deploy time:
  ```
  RAILPACK_DEPLOY_APT_PACKAGES=libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2 libglib2.0-0 libffi-dev shared-mime-info fonts-liberation
  ```
- **Frontend (Streamlit Cloud):** Deployed directly from `frontend/streamlit_app.py`; configured via `frontend/.streamlit/config.toml`, with secrets supplied through Streamlit Cloud's secrets manager (mirrors `frontend/.streamlit/secrets.toml` locally). Update `api_client.py`'s base URL to point at the deployed Railway backend.

---

## 📊 How Scoring Works

Each resume is scored out of 100 across five weighted components:

| Component | Weight | What it measures |
|---|---|---|
| Formatting | 20 | Structure, section headers, bullet consistency |
| Keywords | 25 | Keyword density and relevance |
| Content Quality | 25 | Action verbs, quantified achievements |
| Skill Validation | 15 | Skills backed by project/experience evidence |
| ATS Compatibility | 15 | Clean formatting with no parsing blockers |

Skill validation uses sentence-transformer embeddings to semantically match each claimed skill against the resume's project and experience text — not just exact keyword matching — so a skill phrased differently in context can still be correctly validated.

---

## 🔧 Key Engineering Decisions

A few non-obvious problems solved during development, documented here for anyone extending the project:

- **Skill validation batching.** The original `validate_skills_with_projects` called `embedder.encode()` once per skill-project pair in a nested loop, causing requests to time out at 60+ seconds for resumes with many skills. Rewriting it to batch all encode calls into two matrix operations brought this down to ~3 seconds.
- **Severity thresholds tuned for realistic resumes.** Early issue-detection logic only flagged "skills lack evidence" when unvalidated skills outnumbered validated ones (~50%+) — missing genuinely weak-but-not-terrible cases like 14/30 (47%) unvalidated. Thresholds were adjusted to a tiered Moderate/High system that better reflects real resume quality.
- **Railway build system mismatch.** The project initially shipped a `nixpacks.toml` for system dependencies, which Railway silently ignored because the project builds with **Railpack**, not Nixpacks. WeasyPrint's system libraries (Pango, Cairo, GLib) are instead installed via the `RAILPACK_DEPLOY_APT_PACKAGES` environment variable — a Railpack-specific mechanism, not a config file.
- **Response schema completeness.** Fields like `suggestions` and `critical_issues` existed in the API response schema but were never populated by the backend pipeline, silently defaulting to empty arrays. Fixed by deriving them directly from detected issues (`generate_suggestions`, `generate_critical_issues`) rather than maintaining a second source of truth.

---

## 🗺️ Roadmap

- [ ] Voice-based mock interview practice (Groq Whisper + Web Speech API)
- [ ] Coding round simulation with Judge0 API integration

---

## 📄 License

This project is for educational and portfolio purposes.# ATS_SYSTEM
