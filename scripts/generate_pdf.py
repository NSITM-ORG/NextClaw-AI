"""
Script to generate an executive-grade PDF Presentation Guide for Nextserve AI & NextClaw.
Uses ReportLab with custom page templates, modern color palette, and structured layout.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Nextserve AI & NextClaw — Project Architecture & Presentation Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential — Nextserve AI Operational System")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def create_presentation_pdf(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1E3A8A")     # Dark Blue
    c_secondary = colors.HexColor("#0284C7")   # Bright Cyan-Blue
    c_dark = colors.HexColor("#0F172A")        # Slate 900
    c_text = colors.HexColor("#334155")        # Slate 700
    c_light = colors.HexColor("#F8FAFC")       # Slate 50
    c_border = colors.HexColor("#CBD5E1")      # Slate 300
    c_accent = colors.HexColor("#10B981")      # Emerald 500

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_text,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    quote_style = ParagraphStyle(
        'Quote_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14.5,
        textColor=c_dark,
        spaceBefore=4,
        spaceAfter=4
    )

    qa_q_style = ParagraphStyle(
        'QA_Q',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_A',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=6
    )

    story = []

    # Title Block
    story.append(Paragraph("Nextserve AI & NextClaw Operational Assistant", title_style))
    story.append(Paragraph("Enterprise Multi-Agent Architecture, HITL Governance & Presentation Pitch Deck", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceBefore=2, spaceAfter=14))

    # 1. Executive Summary & Pitch
    story.append(Paragraph("1. Executive Summary & 60-Second Elevator Pitch", h1_style))
    pitch_text = (
        "<b>\"Hi everyone, today I'm presenting Nextserve AI</b>, an enterprise-grade, autonomous multi-agent "
        "operating platform powered by <b>NextClaw</b>, our real-time operational assistant.<br/><br/>"
        "The core problem we solved is operational friction in educational and tech organizations: student inquiries "
        "get delayed, software bugs take hours to triage, content publication lacks SEO guardrails, and administrative staff "
        "are overwhelmed by inbox management.<br/><br/>"
        "To solve this, we built a fully asynchronous <b>FastAPI</b> backend backed by <b>PostgreSQL + pgvector</b> "
        "that coordinates three specialized AI agents under strict <b>Human-in-the-Loop (Level-3)</b> governance. "
        "Our continuous background workers monitor Gmail, draft intelligent responses, route interactive approval cards "
        "to Telegram, and converse with users in real-time. Everything is production-ready, fully tested, and auditable.\""
    )
    
    pitch_box = Table(
        [[Paragraph(pitch_text, quote_style)]],
        colWidths=[504]
    )
    pitch_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(pitch_box)
    story.append(Spacer(1, 12))

    # 2. Architecture Overview
    story.append(Paragraph("2. System Architecture & Core Technology Stack", h1_style))
    story.append(Paragraph(
        "Nextserve AI is engineered around an asynchronous event-driven design, cleanly separating high-throughput API "
        "routing, vector semantic search, background state polling, and external communication adapters.",
        body_style
    ))

    stack_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Key Responsibilities</b>", body_style)],
        [Paragraph("<b>Core API Framework</b>", body_style), Paragraph("FastAPI + Uvicorn (Python 3.13)", body_style), Paragraph("Asynchronous REST endpoints, Starlette event loop, OpenAPI schema.", body_style)],
        [Paragraph("<b>Database & Storage</b>", body_style), Paragraph("PostgreSQL 16 + pgvector", body_style), Paragraph("Hybrid store: vector embeddings for academic policies and relational models for tickets.", body_style)],
        [Paragraph("<b>Agent Orchestration</b>", body_style), Paragraph("LangGraph & LangChain", body_style), Paragraph("ReAct tool-calling loops, multi-turn conversational memory, offline deterministic fallback.", body_style)],
        [Paragraph("<b>Background Engine</b>", body_style), Paragraph("Continuous Asyncio Workers", body_style), Paragraph("Gmail IMAP BODY.PEEK poller (20s) and Telegram getUpdates long-poller (1s).", body_style)],
        [Paragraph("<b>HITL Interface</b>", body_style), Paragraph("Telegram Bot API", body_style), Paragraph("Interactive HTML approval cards with inline buttons and real-time user discussion.", body_style)],
    ]
    t_stack = Table(stack_data, colWidths=[120, 140, 244])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 14))

    # 3. The Three Specialized AI Agents
    story.append(Paragraph("3. The 3 Specialized Autonomous Agents", h1_style))

    story.append(Paragraph("A. NextClaw School & Academic Advising Agent", h2_style))
    story.append(Paragraph(
        "Acts as a 24/7 intelligent academic counselor for prospective and enrolled students. "
        "Equipped with tools for course catalog queries, syllabus lookup, tuition fee breakdowns, and refund policy analysis. "
        "Includes intent classification to ensure casual chit-chat receives warm, natural conversational replies rather than "
        "raw vector search dumps.",
        body_style
    ))
    story.append(Paragraph("• <b>Course Retrieval:</b> Deep catalog lookups (CS101, CS201, CS350, DS105, MATH201) with prerequisite graphs and instructor contacts.", bullet_style))
    story.append(Paragraph("• <b>Policy Guidance:</b> Instant answers on add/drop deadlines, payment installment structures, and grade disputes.", bullet_style))
    story.append(Paragraph("• <b>Conversational Polish:</b> Responds to social greetings (hi, hello, how are you) with a supportive, branded intro.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("B. Autonomous Coding Agent", h2_style))
    story.append(Paragraph(
        "A virtual junior software engineer dedicated to bug triage and automated patch engineering.",
        body_style
    ))
    story.append(Paragraph("• <b>GitHub Ticket Ingestion:</b> Reads issue descriptions, stack traces, and affected repository paths.", bullet_style))
    story.append(Paragraph("• <b>Patch Generation:</b> Synthesizes targeted git diffs and complementary test cases.", bullet_style))
    story.append(Paragraph("• <b>Level-3 Safety Gate:</b> Pull requests cannot be submitted automatically without human supervisor approval.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("C. Website & Content Management Agent", h2_style))
    story.append(Paragraph(
        "Automates educational content marketing and university publication pipelines.",
        body_style
    ))
    story.append(Paragraph("• <b>Headless CMS Integration:</b> Stages articles and curriculum updates directly in the CMS.", bullet_style))
    story.append(Paragraph("• <b>Automated SEO Engine:</b> Verifies meta descriptions, keyword frequency, and readability indices prior to staging.", bullet_style))
    story.append(Paragraph("• <b>Human Authorization:</b> Prevents unauthorized publishing of live web content.", bullet_style))

    story.append(Spacer(1, 14))

    # 4. Continuous Background Engine
    story.append(Paragraph("4. Continuous Background Engine & Notification Flow", h1_style))
    story.append(Paragraph(
        "Rather than forcing the operator to manually trigger scripts, Nextserve AI incorporates an autonomous background engine:",
        body_style
    ))
    story.append(Paragraph("• <b>Gmail Continuous Worker (20s Cycle):</b> Connects securely via IMAP. Utilizes <code>BODY.PEEK[]</code> to preserve unread status in the user's primary inbox. Formats incoming inquiries into a standardized draft signed off as <i>NextClaw (Nextserve AI Operational Assistant)</i>.", bullet_style))
    story.append(Paragraph("• <b>Telegram Interactive Cards:</b> Sends an HTML card to the Telegram admin with truncated preview (max 1,000 characters) and inline buttons: <code>[✅ Approve & Send]</code> and <code>[❌ Reject]</code>.", bullet_style))
    story.append(Paragraph("• <b>Telegram Long-Polling Worker:</b> Listens continuously for callback taps and natural chat messages without requiring public domain webhooks or third-party tunneling utilities (e.g. ngrok).", bullet_style))
    story.append(Paragraph("• <b>Human-in-the-Loop Execution:</b> On approval tap, the worker triggers SMTP dispatch, commits status <code>APPROVED</code> into PostgreSQL, and records an immutable audit log.", bullet_style))

    story.append(Spacer(1, 14))

    # 5. Live Demo Guide
    story.append(Paragraph("5. Step-by-Step Live Demonstration Script", h1_style))
    
    demo_steps = [
        ("Step 1: Live Interactive Chat on Telegram", 
         "Open @GodlypaschalBot on your phone or desktop. Send 'hi'. Show the conversational greeting. "
         "Then send 'Tell me about CS101 and CS350' to showcase the instant academic advising lookup."),
        ("Step 2: Email Notification & Approval Loop", 
         "Send a live email from your smartphone to chigbookpalaugo@gmail.com with subject 'Question on Tuition'. "
         "Within 20 seconds, point to Telegram as the card arrives with the AI draft and [✅ Approve & Send] / [❌ Reject] buttons."),
        ("Step 3: One-Click Approval & SMTP Dispatch", 
         "Click [✅ Approve & Send]. Point out the instant Telegram confirmation and verify that the sender received the professional reply."),
        ("Step 4: Swagger Documentation & System Health", 
         "Navigate to http://localhost:8000/docs. Highlight the interactive OpenAPI spec, demonstrating the clean modular architecture."),
    ]

    for title, desc in demo_steps:
        box = Table(
            [[Paragraph(f"<b>{title}</b><br/>{desc}", body_style)]],
            colWidths=[504]
        )
        box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_light),
            ('BOX', (0,0), (-1,-1), 0.5, c_border),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(box)
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))

    # 6. Anticipated Technical Questions
    story.append(Paragraph("6. Anticipated Q&A (How to Answer as the Lead Architect)", h1_style))
    
    qa_list = [
        ("Why did you build this on FastAPI instead of Django?",
         "FastAPI is natively asynchronous (built on Starlette and Pydantic). Because NextClaw operates continuous background pollers for Gmail and Telegram while serving high-throughput REST endpoints, FastAPI gives us non-blocking async event loops, ultra-fast serialization, and automatic OpenAPI documentation without the overhead of heavy sync frameworks."),
        ("How do you prevent duplicate email alerts in the worker?",
         "We use a two-tier deduplication strategy: first, an in-memory UID cache for sub-millisecond lookups during the worker loop; second, a unique constraint on email_uid in our PostgreSQL database to ensure state persists across server restarts."),
        ("How does the Telegram bot work locally without a public webhook URL?",
         "We implemented a background TelegramBotWorker that uses Telegram's long-polling getUpdates API. On startup, it clears any old external webhooks and opens an async polling loop that retrieves updates directly, meaning it works anywhere out of the box without needing ngrok or a public domain."),
        ("What is your AI Safety / Human-in-the-Loop policy?",
         "The AI operates under Level-3 Human-in-the-Loop governance: it never sends emails or publishes code unilaterally. It drafts responses, stores them with status PENDING, and waits for an admin's signed Telegram callback before executing."),
    ]

    for q, a in qa_list:
        story.append(Paragraph(f"Q: {q}", qa_q_style))
        story.append(Paragraph(f"A: {a}", qa_a_style))

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_filename}")


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Nextserve_AI_Presentation_Guide.pdf")
    create_presentation_pdf(output_path)
