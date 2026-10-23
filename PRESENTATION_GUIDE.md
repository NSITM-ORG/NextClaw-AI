# Nextserve AI & NextClaw Operational Assistant
## Complete Project Architecture, Pitch Deck & Presentation Guide

---

## 1. Executive Summary & Elevator Pitch
*(Use this when introducing the project in under 60 seconds)*

> "Hi everyone, today I'm presenting **Nextserve AI**, an enterprise-grade, autonomous multi-agent operating platform powered by **NextClaw**, our real-time operational assistant for **Nextserve Institute of Technology and Management (NSITM)**.
> 
> Educational and tech institutions lose thousands of hours to operational friction: new diploma curriculum updates take weeks to synchronize across catalogs and portals, content marketing is slow, code patches for registration and tuition policies require manual dev triage, and student advisors are overwhelmed by inquiries across email, chat, and voice.
> 
> To solve this, we built a fully asynchronous **FastAPI** backend with **PostgreSQL + pgvector** coordinating four specialized autonomous agents under strict **Level 3 Human-in-the-Loop (HITL)** governance ('Zero-Unapproved-Writes'). Our system features an end-to-end **Composite Orchestrator Pipeline**, continuous **Gmail and Telegram background workers**, an **Ambient Voice Assistant (Whisper + TTS)**, and a **Social Media Studio**. Everything is grounded in authoritative institutional repository memory, fully automated across 36 unit and integration tests, and auditable."

---

## 2. System Architecture at a Glance

```mermaid
graph TD
    User[Student / Admin / Public] -->|Web UI / Voice| Dash[Glassmorphic Dashboard :8000/app/]
    User -->|Inquiry Email| Gmail[Gmail Inbox]
    User -->|Telegram Chat| TG[@GodlypaschalBot]

    subgraph Multi-Agent Operations Layer
        Orch[Composite Pipeline Orchestrator]
        School[Academic Advising Agent]
        Coding[Autonomous Coding Agent]
        CMS[Website & CMS Agent]
        Social[Content & Social Media Agent]
        Voice[Whisper STT & TTS Voice Engine]
    end

    subgraph Level 3 HITL Governance Gate
        HITL[Zero-Unapproved-Writes Gate]
        TGCard[Interactive Telegram Card]
        Audit[PostgreSQL Immutable Audit Trail]
    end

    subgraph Database Layer
        PG[(PostgreSQL + pgvector)]
        PG --> Catalog[26 Accredited Diplomas & Policies]
        PG --> Runs[Composite Runs & Social Drafts]
    end

    Dash --> Orch
    Dash --> Voice
    Dash --> Social
    Orch --> School
    Orch --> Coding
    Orch --> CMS
    Orch --> HITL
    HITL --> TGCard
    HITL --> Audit
    Social --> HITL
```

---

## 3. The Specialized Autonomous Agents

### 1. Academic Advising Agent (`agents/school/`)
- **Knowledge Memory**: Grounded in 26 accredited diplomas, Lagos campus (12 Montgomery Rd, Yaba) & Virtual Campus, and 3-tranche tuition instalment plans.
- **Institutional Invariants**: Enforces strict refund thresholds (80% before Day 1, 0% after Day 1), 80% attendance requirement, and capstone project guidelines.
- **Calendar Tools**: Synchronizes marketing calendars, cohort intakes (Cohort 3 in 2027), and Content Pitch Contests.

### 2. Autonomous Coding Agent (`coding_agent/`)
- **AST Code Analysis**: Parses Python ASTs to validate method signatures, detect syntax issues, and prevent catalog corruption.
- **Patch Synthesis**: Generates targeted unified git diffs modifying repository files safely.
- **Zero-Unapproved-Writes**: Cannot commit or merge directly; requires Level 3 HITL authorization.

### 3. Website & Content Management Agent (`website_agent/`)
- **Staging & Publishing**: Generates HTML/Markdown drafts for course announcements, tuition policies, and news updates.
- **Automated SEO Engine**: Evaluates title length, meta description, heading structure, and keyword density.
- **Rollback Protection**: Instant snapshot rollback to previous stable versions.

### 4. Content & Social Media Agent (`social_agent/`)
- **MEMORY.md Campaigns**: Instant access to official institutional campaigns (*Content Pitch Contest, WAEC Finisher Transition, Summer Immersion, Alumni Reactivation, Cohort 3 Intake, 10-Part Webinar Series*).
- **Multi-Channel Tailoring**: Concurrently drafts copy for X/Twitter (strict 280-char limit), LinkedIn, Instagram, WhatsApp, and Facebook.
- **AI Visual Prompts**: Generates tailored photographic/digital banner prompts for every campaign.
- **HITL Governance**: Every social campaign draft requires explicit review and approval before publication.

### 5. Ambient Voice Interaction Engine (`app/services/voice_service.py`)
- **Speech-to-Text**: Real-time microphone audio recording via Web MediaRecorder transcribed by OpenAI Whisper (`whisper-1`).
- **Text-to-Speech**: Streaming synthesized speech via OpenAI TTS (`tts-1`) across 6 voices (*alloy, nova, echo, shimmer, onyx, fable*) with client-side Web Speech API zero-latency fallback.
- **Visualizer**: Ambient fullscreen glassmorphic modal with a reactive breathing orb visualizer and live transcript stream.

---

## 4. Multi-Agent Composite Orchestrator Pipeline (Section 1 Demo)

Demonstrates the synchronized, multi-agent autonomous workflow:
1. **Stage 1 (Academic Synthesis)**: School Agent verifies diploma parameters, curriculum specs, and 3-tranche tuition formulas.
2. **Stage 2 (Autonomous Coding)**: Coding Agent synthesizes an AST-verified git patch updating knowledge files.
3. **Stage 3 (CMS Staging)**: Website Agent stages live announcement with automated SEO score.
4. **Stage 4 (Level 3 Governance Gate)**: Pipeline halts execution, registers an `ApprovalRequest` in PostgreSQL, and dispatches an interactive Telegram card.
5. **Stage 5 (Production Dispatch)**: Upon approval, git patch merges, CMS publishes live, immutable audit logs record the event, and notifications dispatch via Telegram and Gmail.

---

## 5. How to Demo This Like a Pro (Step-by-Step Script)

Follow this 6-step sequence to showcase the complete platform:

### Step 1: Open the Glassmorphic Dashboard
1. Open your browser to **`http://localhost:8000/app/`**.
2. Highlight the dark mode glassmorphism interface: live metrics, navigation tabs, and agent indicators.

### Step 2: Run the Multi-Agent Composite Orchestrator Pipeline
1. Click the **Automations** tab.
2. Click the preset blueprint card: **"AI & LLM Engineering Curriculum & Agent Patch"** or **"Mobile App Dev with Flutter"**.
3. Click **"Run Composite Pipeline"**.
4. Show the live execution:
   - Stage 1 completes (Academic specs & 3-tranche instalment formulas verified).
   - Stage 2 completes (Git patch synthesized with AST verification).
   - Stage 3 completes (CMS announcement staged with SEO audit).
   - Stage 4 halts at **Level 3 Approval Required**.
5. Inspect the subtabs:
   - Click **"Academic Specs"** to view verified invariants.
   - Click **"Code Diff"** to view syntax-highlighted git diff.
   - Click **"CMS Staging"** to view live webpage preview.
6. Click **"Authorize & Deploy Live"**.
7. Watch Stage 5 complete: patch merged, CMS live, audit trail recorded, and Telegram alert dispatched!

### Step 3: Demo Ambient Voice Assistant (Whisper + TTS)
1. Click the **Voice Mic button** in the chat bar.
2. The **Ambient Voice Assistant** modal opens with a reactive glowing orb visualizer.
3. Speak or simulate inquiry: *"What is the tuition instalment structure for Fullstack Web Development?"*
4. Nextserve AI transcribes your voice via Whisper, reasons over institutional memory, streams audio speech via OpenAI TTS, and speaks the answer aloud.

### Step 4: Demo the Social Media Studio
1. Click the **Social Studio** tab.
2. In the Campaign dropdown, select **"Nextserve Content Pitch Contest 2026"**.
3. Select Tone: **"Inspiring"**.
4. Click **"Synthesize Campaign Copy"**.
5. Show the generated outputs across tabs:
   - Click **"X / Twitter"**: Note the strict 280-character badge (e.g. `242/280 chars PASSED ✅`).
   - Click **"LinkedIn"**: Professional long-form narrative with structured bullet points and industry hashtags.
   - Click **"WhatsApp"**: Formatted bulletin with emoji bullet points.
   - Show the **AI Image Banner Prompt** generated specifically for design teams.
6. Click **"Approve & Schedule Post"** to demonstrate Level 3 governance.

### Step 5: Demo Live Telegram Bot & Email Loop
1. Open Telegram to **`@GodlypaschalBot`** and send a greeting or course query.
2. Send an inquiry email to **`chigbookpalaugo@gmail.com`**.
3. Within 20 seconds, demonstrate the continuous background worker detecting the email, drafting a polite response signed by NextClaw, and forwarding an interactive approval card to Telegram with `[Approve & Send]` and `[Reject]`.

### Step 6: Show the 100% Automated Test Suite
1. Run in terminal:
   ```bash
   python -m pytest tests/ -v
   ```
2. Point out all 36 tests passing:
   - `test_composite_workflow.py` (Pipelines, approvals, rollbacks)
   - `test_voice_service.py` (Whisper STT, TTS voices, capabilities)
   - `test_social_agent.py` (Multi-channel copy, character limits, governance)
   - `test_coding_agent.py` (AST checks, PR submission gates)
   - `test_website_agent.py` (CMS staging, SEO scoring)
   - `test_school_agent.py` (Catalog lookup, semantic RAG)

---

## 6. Technology Stack Summary

- **Backend Framework**: FastAPI, Python 3.13, Starlette, Pydantic v2
- **Database**: PostgreSQL 16 + pgvector (semantic cosine similarity `<=>`)
- **Agent Framework**: LangGraph StateGraph, LangChain, OpenAI GPT-4o
- **Audio & Voice**: OpenAI Whisper (`whisper-1`), OpenAI TTS (`tts-1`), Web Audio API, Web Speech API
- **Protocols & Integrations**: IMAP (fetching via `BODY.PEEK[]`), SMTP (dispatch), Telegram Bot API (long-polling)
- **Frontend**: Vanilla HTML5, CSS3 Glassmorphism design tokens, Modern JavaScript
- **Testing**: Pytest, Starlette TestClient, 36 automated unit & integration tests
