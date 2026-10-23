#!/usr/bin/env python3
"""
Nextserve School of Information Technology and Management (NSITM)
Executive Owner & Administrator Agent Console.

Designed for the school owner to query school intelligence,
calculate tuition instalments, inspect Gmail inquiries, and monitor
real-time Telegram alerts directly.
"""

import os
import sys
import asyncio
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agents.school.agent import query_school_agent
from agents.school.tools import calculate_tuition_instalments, get_institution_info
from app.knowledge.nsitm_knowledge import PROGRAMMES_DATA, INSTITUTION_INFO
from app.services.telegram_service import telegram_service
from app.services.gmail_service import gmail_service


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 72)
    print(" 🏛️  NEXTSERVE AI EXECUTIVE CONSOLE — NSITM SCHOOL OPERATING AGENT")
    print("     Practical Tech & Management Training • Established 2012")
    print("=" * 72)


def print_menu():
    print("\nSelect an action:")
    print("  [1] 💬 Ask NextClaw Anything (Courses, Fees, Policies, Admissions)")
    print("  [2] 💰 Calculate 3-Part Instalment Breakdown (in ₦ Naira)")
    print("  [3] 📬 Check Gmail Inquiries & Dispatch Telegram Approval Card")
    print("  [4] 📋 Browse All 26 NSITM Programmes by Category")
    print("  [5] 🏛️ View Institutional History & Leadership Summary")
    print("  [6] 📱 Test Real-Time Telegram Activity Notification (Payment/Lead/Join)")
    print("  [0] 🚪 Exit Console")
    print("-" * 72)


def handle_ask_agent():
    print("\n--- NextClaw Executive Inquiry ---")
    print("(Type 'back' to return to the main menu)")
    while True:
        prompt = input("\n👤 Owner > ").strip()
        if not prompt:
            continue
        if prompt.lower() in ["back", "exit", "quit", "b"]:
            break
        print("\n🤖 NextClaw is thinking...\n")
        res = query_school_agent(prompt)
        print(res.get("response", "No response returned."))
        print("-" * 50)


def handle_calculate_instalments():
    print("\n--- Tuition Instalment Calculator ---")
    print("Available 6-Month Categories: Tech Development & Management")
    course_name = input("Enter programme name or keyword (e.g. Fullstack, UI/UX, Cyber Security, Digital Marketing): ").strip()
    if not course_name:
        return
    print("\n" + calculate_tuition_instalments.invoke({"programme_name": course_name}))


def handle_check_gmail():
    print("\n--- Checking Live Gmail Admissions Inbox ---")
    unread = gmail_service.fetch_latest_unread(mark_as_read=False)
    if not unread:
        print("📬 No unread student inquiries in the inbox at this moment.")
        return

    print(f"📧 Found Unread Inquiry from: {unread.get('sender_name')} <{unread.get('sender')}>")
    print(f"📌 Subject: {unread.get('subject')}")
    print(f"📝 Content:\n{unread.get('body')[:300]}...\n")

    dispatch = input("Would you like NextClaw to draft a reply and send an approval card to your Telegram? (y/n): ").strip().lower()
    if dispatch == "y":
        from agents.school.tools import draft_and_request_email_approval
        result = draft_and_request_email_approval.invoke({
            "to_email": unread.get("sender"),
            "subject": f"Re: {unread.get('subject')}",
            "body": "Dear Applicant,\n\nThank you for reaching out to Nextserve (NSITM). Our admissions team has received your inquiry. Classes are offered in Online, Lagos Campus Hub, and Hybrid formats with flexible instalment options.\n\nBest regards,\nNextserve Admissions Team",
            "sender_name": unread.get("sender_name"),
            "inquiry_context": unread.get("body")
        })
        print("\n" + result)


def handle_browse_programmes():
    print("\n--- 26 NSITM Accredited Programmes ---")
    categories = {}
    for p in PROGRAMMES_DATA:
        cat = p["category_label"]
        categories.setdefault(cat, []).append(p)

    for cat_name, progs in categories.items():
        print(f"\n📂 {cat_name.upper()} ({len(progs)} Programmes):")
        print(f"{'Code':<12} {'Programme Name':<38} {'Duration':<10} {'Full Tuition':<14} {'Instalment'}")
        print("-" * 88)
        for p in progs:
            full_t = f"₦{p['tuition']:,.0f}"
            inst_t = f"₦{p['instalment_fee']:,.0f}" if p.get('instalment_fee') else "Full Only"
            print(f"{p['course_code']:<12} {p['name']:<38} {p['duration']:<10} {full_t:<14} {inst_t}")


def handle_institution_info():
    print("\n--- Nextserve (NSITM) Institutional Summary ---")
    print(get_institution_info.invoke({}))


def handle_test_telegram_alerts():
    print("\n--- Test Real-Time Telegram Alerts ---")
    print("  [a] Simulate Student Tuition Payment (₦152,000 for Fullstack)")
    print("  [b] Simulate Step 1 Lead Capture (Prospective Student)")
    print("  [c] Simulate Developer Community Join Application")
    print("  [d] Return")

    choice = input("Select test alert: ").strip().lower()
    if choice == "a":
        res = telegram_service.send_payment_alert(
            student_name="Paschal Okpalaugo",
            email="paschal@example.com",
            programme="Fullstack Web Development",
            amount=152000.0,
            plan_type="Instalment Plan",
            tranche=1,
            receipt_url="https://nextserve.edu.ng/receipts/demo_receipt.pdf"
        )
        print("✅ Payment alert dispatched to your Telegram bot!")
    elif choice == "b":
        res = telegram_service.send_partial_enrollment_alert(
            student_name="Adaeze Nwosu",
            email="adaeze@example.com",
            phone="+2348031234567",
            programme="UI/UX Design",
            delivery_format="Online Virtual Cohort"
        )
        print("✅ Step 1 Lead alert dispatched to your Telegram bot!")
    elif choice == "c":
        res = telegram_service.send_community_join_alert(
            name="Chinedu Eze",
            email="chinedu@example.com",
            role="Backend Developer (Node.js & Python)",
            portfolio_or_github="https://github.com/chinedueze"
        )
        print("✅ Community Join alert dispatched to your Telegram bot!")


def main():
    while True:
        print_banner()
        print_menu()
        choice = input("Enter choice (0-6): ").strip()

        if choice == "1":
            handle_ask_agent()
        elif choice == "2":
            handle_calculate_instalments()
        elif choice == "3":
            handle_check_gmail()
        elif choice == "4":
            handle_browse_programmes()
        elif choice == "5":
            handle_institution_info()
        elif choice == "6":
            handle_test_telegram_alerts()
        elif choice in ["0", "exit", "quit"]:
            print("\nExiting NextClaw Executive Console. Have a productive day!\n")
            break
        else:
            print("\nInvalid selection. Please try again.")

        input("\nPress Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main()
