# Nextserve AI Enterprise Autonomous Operations Platform

An enterprise-grade, multi-agent AI operations platform designed for **Nextserve Institute of Technology and Management (NSITM)**. Integrates specialized autonomous agents under **Level 3 Human-in-the-Loop (HITL) Governance** ("Zero-Unapproved-Writes") with persistent PostgreSQL memory, multi-channel alerting (Telegram & Gmail), ambient voice interaction, and rich glassmorphism web dashboard.

---

## 🏛️ Grounded Institutional Truth & Governance

All agent operations are strictly anchored in authoritative institutional repository memory (`configs/MEMORY.md`):
- **26 Accredited Diplomas**: Fullstack Web Development, AI & LLM Engineering, Data Science & Machine Learning, Mobile App Dev (Flutter/React Native), UI/UX Product Design, Cyber Security, Cloud DevOps, and 19 additional specialized diplomas.
- **Tuition & Payment Terms**: Standard one-off tuition vs. 3-tranche instalment plans (Tranche 1: 40% upon admission, Tranche 2: 30% at Week 4, Tranche 3: 30% at Week 8).
- **Institutional Refund Policy**: Strict 80% refund threshold before Day 1 of classes; 0% refund after Day 1 commences.
- **Campus Locations**: Lagos Campus (12 Montgomery Road, Yaba, Lagos) & Global Virtual Campus.
- **Level 3 HITL Governance**: Zero unapproved writes. Code commits, CMS live deployments, email dispatches, and social post publications halt at approval gates requiring authorized human sign-off via Telegram cards or the web dashboard.

---

## 🚀 Architectural Modules & Capabilities

```text
nextserve-ai/
├── agents/
│   ├── school/                # Phase 3: Academic Advising & Admissions Agent
│   │   ├── agent.py           # LangGraph StateGraph agent with fallback logic
│   │   ├── tools.py           # get_course_details, calculate_tuition_instalments, RAG search
│   │   └── calendar_tools.py  # Institutional academic calendar, cohorts, and pitch contests
├── coding_agent/              # Phase 4: Autonomous Coding Agent
│   ├── agent.py               # Issue analysis, AST validation, git diff synthesizer
│   ├── github_adapter.py      # Git branch, PR creation, commit simulation
│   └── tools.py               # AST parser, static analyzer, linter tools
├── website_agent/             # Phase 5: Website & Content Management Agent
│   ├── agent.py               # Page updater, SEO scoring, preflight checks, rollback
│   ├── cms_adapter.py         # Static HTML/Markdown CMS publisher & staging engine
│   └── tools.py               # SEO score calculator, broken link checker
├── social_agent/              # Phase 6: Content & Social Media Agent
│   ├── agent.py               # Multi-channel copy synthesizer (X, LinkedIn, IG, WhatsApp, FB)
│   ├── campaigns.py           # Institutional campaign catalog from MEMORY.md
│   ├── tools.py               # Character counter & platform constraints validator
│   └── schemas.py             # Pydantic schemas for campaign drafts and approval decisions
├── app/
│   ├── services/
│   │   ├── composite_workflow.py # Multi-Agent Composite Orchestrator (Section 1 Demo)
│   │   ├── voice_service.py      # Phase 7: Whisper STT & OpenAI TTS Voice Engine
│   │   ├── telegram_service.py   # Telegram Bot Level 3 HITL approval card dispatcher
│   │   └── gmail_service.py      # SMTP & Gmail worker notifications
│   ├── db/
│   │   ├── models.py          # SQLAlchemy PostgreSQL models & pgvector schemas
│   │   ├── session.py         # Engine & connection pool
│   │   └── vector_store.py    # Semantic cosine search (<=>)
│   └── api/router.py          # Unified API Router
├── api/routes/
│   ├── composite.py           # Composite Orchestrator endpoints (/presets, /start, /resume)
│   ├── voice.py               # Phase 7 Voice endpoints (/transcribe, /speak, /capabilities)
│   ├── social.py              # Phase 6 Social endpoints (/campaigns, /generate, /drafts)
│   ├── coding.py              # Phase 4 Coding endpoints
│   ├── website.py             # Phase 5 Website CMS endpoints
│   └── school.py              # Phase 3 Academic Advising endpoints
├── frontend/                  # Modern Glassmorphic Web Dashboard
│   ├── index.html             # Multi-tab operational workspace + Ambient Voice Assistant
│   ├── styles.css             # Glassmorphism design system & micro-animations
│   └── app.js                 # Reactive state manager, Voice STT/TTS engine, Pipeline visualizer
└── tests/                     # 36 Automated Unit & Integration Tests (100% Pass)
```

---

## ⚡ Core Operational Features

### 1. Multi-Agent Composite Orchestrator (Section 1 Demo)
Coordinates an end-to-end operational pipeline across 3 specialist agents with Level 3 governance:
1. **Stage 1 (Academic Advising Agent)**: Validates curriculum specifications, attendance invariants, and 3-tranche tuition formulas.
2. **Stage 2 (Autonomous Coding Agent)**: Synthesizes a verified git patch modifying catalog files, validated via AST static analysis.
3. **Stage 3 (Website CMS Agent)**: Generates a staged website announcement with automated SEO scoring and pre-flight validation.
4. **Stage 4 (Level 3 HITL Gate)**: Halts execution, generates an interactive Telegram approval card and dashboard decision modal.
5. **Stage 5 (Production Dispatch)**: Upon approval, merges git patch to `main`, deploys CMS live, registers immutable audit logs, and sends email/Telegram confirmations.

### 2. Phase 7: Ambient Voice Interaction
- **Speech-to-Text (STT)**: Microphone audio recorded via Web MediaRecorder, transcribed via OpenAI Whisper (`whisper-1`) with intelligent fallback.
- **Text-to-Speech (TTS)**: Dual-layer audio streaming with OpenAI TTS (`tts-1`) featuring 6 selectable voices (*alloy, nova, echo, shimmer, onyx, fable*) and client-side Web Speech API zero-latency fallback.
- **Ambient Voice Assistant**: Fullscreen glassmorphic overlay with dynamic CSS breathing orb visualizer and real-time transcript streaming.

### 3. Phase 6: Content & Social Media Studio
- **Institutional Campaigns**: Pre-configured campaign briefs grounded in `MEMORY.md` (*Nextserve Content Pitch Contest, WAEC Finisher Transition, Summer Immersion, Alumni Reactivation, Cohort 3 Intake, 10-Part Webinar Series*).
- **Multi-Platform Copy Generation**: Simultaneous synthesis of optimized copy for X/Twitter (strict 280-char enforcement), LinkedIn, Instagram, WhatsApp, and Facebook.
- **Platform Constraints Engine**: Automated character counting, hashtag extraction, and link validation.
- **Level 3 Approval**: Drafts require explicit human review before publication to social channels.

---

## 🛠️ Quickstart Guide

### 1. Clone & Configure Environment
```bash
cp .env.example .env
# Edit .env to set OPENAI_API_KEY, DATABASE_URL, TELEGRAM_BOT_TOKEN
```

### 2. Start PostgreSQL with pgvector
```bash
docker compose up -d
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install python-multipart
```

### 4. Run Development Server
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Access the Web Dashboard
Open your browser to:
- **Web Dashboard**: `http://127.0.0.1:8000/app/`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

## 🧪 Automated Testing

All 36 unit and integration tests execute with 100% pass rate:
```bash
python -m pytest tests/ -v
```

Test breakdown:
- `tests/test_composite_workflow.py`: Preset blueprints, end-to-end 5-stage pipeline, approval merge, rejection rollback.
- `tests/test_voice_service.py`: STT transcription, TTS voice synthesis, voice capabilities discovery.
- `tests/test_social_agent.py`: Institutional campaigns, character limit validation, multi-channel copy generation, Level 3 post publication.
- `tests/test_school_agent.py`: Knowledge base semantic search, tuition calculation, course lookup.
- `tests/test_school_calendar_integration.py`: Cohort schedules, marketing calendars, pitch contests.
- `tests/test_coding_agent.py`: AST validation, patch generation, PR submission gate.
- `tests/test_website_agent.py`: CMS page drafting, SEO auditing, pre-flight safety checks.
