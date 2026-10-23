"""
Nextserve School of Information Technology and Management (NSITM)
Comprehensive Knowledge Base & Domain Intelligence.

Authoritative source of truth for the NextClaw AI Agent and Telegram Bot.
Extracted and verified directly from the NSITM production systems.
"""

from decimal import Decimal
from typing import Dict, Any, List, Optional

INSTITUTION_INFO = {
    "name": "Nextserve School of Information Technology and Management (NSITM)",
    "short_name": "Nextserve",
    "established_year": 2012,
    "years_of_experience": 14,
    "tagline": "Practical Tech & Management Training, Built for the Real World",
    "founder": {
        "title": "Founder & Academic Director",
        "education": "Federal Polytechnic Nekede (HND Computer Science)",
        "background": "Years of institutional and practical teaching at Synergy Systems and Yaba College of Technology.",
        "ethos": "Built around 14 years of direct, in-person instruction and practical curriculum development."
    },
    "philosophy": [
        {
            "title": "Project-Based Learning",
            "description": "Every programme is built around real deliverables — not slides or theory-only modules."
        },
        {
            "title": "Practical Over Theoretical",
            "description": "Students leave with something they built and portfolio proof, not just memorized notes."
        },
        {
            "title": "Live Project Model",
            "description": "Later-stage students collaborate on real client-facing deliverables under instructor supervision."
        },
        {
            "title": "Intimate Cohort Sizes",
            "description": "Deliberately small class sizes so instructors know students by name, not by roster number."
        }
    ],
    "stats": {
        "graduates": "10,000+",
        "instructors": "50+",
        "programmes_count": 26,
        "active_years": 14
    },
    "delivery_formats": {
        "online": "Virtual live interactive classes accessible nationwide with mentors.",
        "in_person": "Physical hands-on training hub located in Lagos, Nigeria.",
        "hybrid": "Flexible combination of online live sessions and physical campus labs."
    },
    "contacts": {
        "whatsapp_number": "+2348093344991",
        "whatsapp_link": "https://wa.me/2348093344991",
        "email": "nsitmonline@gmail.com",
        "address": "Lagos Hub, Nigeria (with nationwide online delivery)"
    }
}

PROGRAMMES_DATA: List[Dict[str, Any]] = [
    # ── Tech Development (15 programmes - 6 Months) ───────────────────
    {
        "course_code": "TECH-FSW",
        "name": "Fullstack Web Development",
        "slug": "fullstack-web-development",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("360000.00"),
        "instalment_fee": Decimal("380000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("152000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("114000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("114000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["HTML5", "CSS3", "JavaScript ES6+", "React", "Node.js", "Express", "MongoDB", "REST APIs", "Git", "Deployment"],
        "summary": "Complete fullstack engineering from UI design and responsive web apps to backend APIs, databases, authentication, and cloud deployment. Includes real capstone client projects.",
        "careers": ["Fullstack Software Developer", "Web Applications Engineer", "JavaScript Specialist"],
        "schedule": "Weekdays (Mon/Wed/Fri) or Weekend Cohorts (Online & In-Person Lagos)"
    },
    {
        "course_code": "TECH-FEW",
        "name": "Front-End Web Development",
        "slug": "front-end-web-development",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("210000.00"),
        "instalment_fee": Decimal("230000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("92000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("69000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("69000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["HTML5", "CSS3 / Modern Flexbox & Grid", "Tailwind CSS", "JavaScript", "React.js", "Redux", "Component Design", "Responsive Layouts"],
        "summary": "Master building fluid, pixel-perfect user interfaces, state management, and modern interactive web experiences with React.",
        "careers": ["Front-End Developer", "React Engineer", "UI Developer"],
        "schedule": "Weekdays (Mon/Wed) or Weekend Cohorts"
    },
    {
        "course_code": "TECH-BEW",
        "name": "Back-End Web Development",
        "slug": "back-end-web-development",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Node.js", "Express.js", "Python / Django", "PostgreSQL", "MongoDB", "JWT Auth", "REST APIs", "Caching & Redis"],
        "summary": "Architect robust server-side systems, microservices, databases, authentication pipelines, and high-performance APIs.",
        "careers": ["Backend Engineer", "API Developer", "Database Administrator"],
        "schedule": "Weekdays (Tue/Thu) or Weekend Cohorts"
    },
    {
        "course_code": "TECH-UIX",
        "name": "UI/UX Design",
        "slug": "ui-ux-design",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Figma", "User Research", "Wireframing", "Interactive Prototyping", "Design Systems", "Usability Testing"],
        "summary": "Design digital products people love. Learn user-centered design, heuristics, wireframes, and design systems in Figma.",
        "careers": ["UI/UX Designer", "Product Designer", "User Researcher"],
        "schedule": "Weekend & Evening Live Sessions"
    },
    {
        "course_code": "TECH-DAN",
        "name": "Data Analytics",
        "slug": "data-analytics",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Advanced Excel", "SQL Queries", "Power BI", "Tableau", "Data Storytelling", "Dashboard Creation"],
        "summary": "Transform messy raw datasets into executive dashboards, business insights, and predictive metrics that drive business decisions.",
        "careers": ["Data Analyst", "Business Intelligence Analyst", "Reporting Specialist"],
        "schedule": "Flexible Weekend Cohorts"
    },
    {
        "course_code": "TECH-DSC",
        "name": "Data Science",
        "slug": "data-science",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Python", "Pandas", "NumPy", "Scikit-Learn", "Statistical Modeling", "Exploratory Data Analysis", "Model Evaluation"],
        "summary": "Extract patterns from complex data using Python, statistics, predictive modeling, and data pipelines.",
        "careers": ["Data Scientist", "Quantitative Analyst", "Machine Learning Associate"],
        "schedule": "Weekdays & Weekend Labs"
    },
    {
        "course_code": "TECH-CYB",
        "name": "Cyber Security",
        "slug": "cyber-security",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Network Security", "Vulnerability Scanning", "SOC Operations", "Threat Intelligence", "Incident Response", "Security Compliance"],
        "summary": "Defend enterprise systems against malicious attacks, monitor threat landscapes, and implement security controls.",
        "careers": ["Cybersecurity Analyst", "Information Security Specialist", "SOC Analyst"],
        "schedule": "Weekend Hands-on Labs"
    },
    {
        "course_code": "TECH-SWE",
        "name": "Software Engineering",
        "slug": "software-engineering",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Data Structures & Algorithms", "System Architecture", "Design Patterns", "Clean Code", "Testing & CI/CD", "Database Engineering"],
        "summary": "Foundational software engineering principles for building scalable, maintainable, high-throughput software systems.",
        "careers": ["Software Engineer", "Systems Architect", "Core Developer"],
        "schedule": "Weekdays & Project Sprints"
    },
    {
        "course_code": "TECH-AIML",
        "name": "AI/Machine Learning",
        "slug": "ai-machine-learning",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Deep Learning", "Neural Networks", "NLP & LLMs", "PyTorch / TensorFlow", "Computer Vision", "AI Agent Workflows"],
        "summary": "Develop predictive machine learning models, natural language algorithms, and next-generation AI agent architectures.",
        "careers": ["AI Engineer", "Machine Learning Specialist", "NLP Developer"],
        "schedule": "Weekend Masterclasses"
    },
    {
        "course_code": "TECH-ETH",
        "name": "Ethical Hacking",
        "slug": "ethical-hacking",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Kali Linux", "Metasploit", "Penetration Testing", "Burp Suite", "OWASP Top 10", "Network Exploitation"],
        "summary": "Learn white-hat offensive security, web application pentesting, network vulnerability assessment, and defensive remediation.",
        "careers": ["Penetration Tester", "Security Auditor", "Ethical Hacker"],
        "schedule": "Weekend Live Labs"
    },
    {
        "course_code": "TECH-DVO",
        "name": "DevOps Engineering",
        "slug": "devops-engineering",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Docker", "Kubernetes", "Linux Administration", "CI/CD Pipelines", "Terraform", "Monitoring & Logging"],
        "summary": "Automate delivery pipelines, containerize applications, and manage scalable cloud infrastructure reliability.",
        "careers": ["DevOps Engineer", "Site Reliability Engineer (SRE)", "Cloud Engineer"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "TECH-MOB",
        "name": "Mobile App Development",
        "slug": "mobile-app-development",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["React Native", "Flutter", "Dart", "Mobile UI Patterns", "API Integration", "App Store & Play Store Deployment"],
        "summary": "Create fast, responsive native mobile applications for iOS and Android using modern cross-platform frameworks.",
        "careers": ["Mobile Application Developer", "React Native Developer", "Flutter Developer"],
        "schedule": "Weekdays & Practical Projects"
    },
    {
        "course_code": "TECH-CLD",
        "name": "Cloud/Automation Engineering",
        "slug": "cloud-automation-engineering",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["AWS Services", "Cloud Architecture", "Infrastructure as Code", "Ansible", "Bash/Python Scripting", "Cost Optimization"],
        "summary": "Design resilient cloud infrastructure and automate operational tasks on global hyperscalers like AWS.",
        "careers": ["Cloud Architect", "Cloud Automation Specialist", "Cloud Administrator"],
        "schedule": "Weekend Hands-on Labs"
    },
    {
        "course_code": "TECH-BDC",
        "name": "Cloud Computing/Big Data Engineering",
        "slug": "cloud-computing-big-data-engineering",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 4,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Apache Spark", "Hadoop", "Data Lakehouses", "Kafka", "ETL Pipelines", "Cloud Warehousing"],
        "summary": "Process terabytes of high-velocity data, build scalable distributed pipelines, and power big-data architectures.",
        "careers": ["Big Data Engineer", "Data Pipeline Architect", "Distributed Systems Engineer"],
        "schedule": "Weekend Live Sessions"
    },
    {
        "course_code": "TECH-CGD",
        "name": "Creative Graphics Design",
        "slug": "creative-graphics-design",
        "category": "tech_development",
        "category_label": "Tech Development",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("250000.00"),
        "instalment_fee": Decimal("270000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("108000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("81000.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("81000.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Adobe Photoshop", "Adobe Illustrator", "Brand Identity Systems", "Typography", "Print & Digital Media", "Packaging Design"],
        "summary": "Craft impactful brand visuals, digital marketing assets, vector illustrations, and brand identity manuals.",
        "careers": ["Graphic Designer", "Brand Identity Specialist", "Visual Designer"],
        "schedule": "Weekdays & Portfolio Sessions"
    },

    # ── Management (7 programmes - 6 Months) ──────────────────────────
    {
        "course_code": "MGMT-DMK",
        "name": "Digital Marketing",
        "slug": "digital-marketing",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Search Engine Optimization (SEO)", "Meta Ads", "Google Ads", "Email Marketing", "Social Media Strategy", "Conversion Rate Optimization"],
        "summary": "Drive customer acquisition, execute paid campaigns, master search rankings, and scale brand growth online.",
        "careers": ["Digital Marketer", "Growth Hacker", "Performance Marketing Manager"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "MGMT-PRM",
        "name": "Project Management",
        "slug": "project-management",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Agile & Scrum", "JIRA", "Risk Management", "Budgeting", "Stakeholder Communication", "Sprint Planning"],
        "summary": "Lead cross-functional teams to deliver complex tech and business projects on time, within budget, and to spec.",
        "careers": ["Project Manager", "Scrum Master", "Product Operations Lead"],
        "schedule": "Weekend Executive Sessions"
    },
    {
        "course_code": "MGMT-INM",
        "name": "Information Management",
        "slug": "information-management",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Data Governance", "Enterprise Content Management", "Records Management", "Information Architecture", "Compliance"],
        "summary": "Organize, secure, and govern enterprise information assets for audit compliance and fast institutional decision-making.",
        "careers": ["Information Manager", "Records & Compliance Officer", "Content Architect"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "MGMT-QCM",
        "name": "Quality Control Management",
        "slug": "quality-control-management",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Six Sigma Principles", "ISO Standards", "QA Auditing", "Process Mapping", "Defect Prevention"],
        "summary": "Establish uncompromising quality assurance standards, audit operational pipelines, and eliminate institutional inefficiencies.",
        "careers": ["Quality Assurance Manager", "Operations Auditor", "Compliance Lead"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "MGMT-RSK",
        "name": "Risk Management",
        "slug": "risk-management",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Risk Assessment Matrix", "Financial Risk Modeling", "Regulatory Compliance", "Crisis Mitigation", "Business Continuity"],
        "summary": "Identify enterprise hazards, calculate financial exposure, and build bulletproof operational resilience strategies.",
        "careers": ["Risk Analyst", "Compliance Officer", "Risk & Safety Consultant"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "MGMT-HRM",
        "name": "Human Resource Management",
        "slug": "human-resource-management",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Talent Acquisition", "Employee Relations", "Performance Appraisal", "HR Analytics", "Labor Law Compliance", "Compensation & Benefits"],
        "summary": "Attract top talent, cultivate high-performing organizational culture, and manage strategic modern workforce operations.",
        "careers": ["HR Specialist", "People Operations Lead", "Talent Acquisition Lead"],
        "schedule": "Weekend Cohorts"
    },
    {
        "course_code": "MGMT-VAS",
        "name": "Virtual Assistance",
        "slug": "virtual-assistance",
        "category": "management",
        "category_label": "Management",
        "duration": "6 months",
        "credits": 3,
        "tuition": Decimal("150000.00"),
        "instalment_fee": Decimal("165000.00"),
        "instalment_breakdown": [
            {"instalment_number": 1, "amount": Decimal("66000.00"), "timing": "At Enrollment (40%)"},
            {"instalment_number": 2, "amount": Decimal("49500.00"), "timing": "Day 30 (30%)"},
            {"instalment_number": 3, "amount": Decimal("49500.00"), "timing": "Day 60 (30%)"},
        ],
        "skills": ["Executive Calendar Scheduling", "Email Management", "CRM Workflows", "Customer Support Tools", "Travel Coordination", "Meeting Minutes"],
        "summary": "Provide world-class remote administrative assistance to global executives, startup founders, and digital enterprises.",
        "careers": ["Executive Virtual Assistant", "Remote Operations Coordinator", "Online Business Manager"],
        "schedule": "Weekdays & Flexible Cohorts"
    },

    # ── Short-Term (4 programmes - 6 Weeks) ───────────────────────────
    {
        "course_code": "SHORT-MOS",
        "name": "Microsoft Office Suites",
        "slug": "microsoft-office-suites",
        "category": "short_term",
        "category_label": "Short Term",
        "duration": "6 weeks",
        "credits": 2,
        "tuition": Decimal("60000.00"),
        "instalment_fee": None,
        "instalment_breakdown": None,
        "skills": ["Advanced Microsoft Word", "Excel Functions & VLOOKUP/XLOOKUP", "PowerPoint Master Slides", "Outlook Productivity"],
        "summary": "Fast-track 6-week practical mastery of business document formatting, financial spreadsheets, automated formulas, and presentations.",
        "careers": ["Administrative Officer", "Office Productivity Specialist", "Executive Secretary"],
        "schedule": "Mon-Fri Fast-Track or Weekend Accelerated"
    },
    {
        "course_code": "SHORT-IVE",
        "name": "Image/Video Editing",
        "slug": "image-video-editing",
        "category": "short_term",
        "category_label": "Short Term",
        "duration": "6 weeks",
        "credits": 2,
        "tuition": Decimal("60000.00"),
        "instalment_fee": None,
        "instalment_breakdown": None,
        "skills": ["Adobe Premiere Pro", "After Effects Motion", "Color Grading", "Audio Syncing", "Short-Form Video (Reels/TikTok/YouTube)"],
        "summary": "Hands-on editing for content creators, agencies, and social video marketers. Learn cuts, transitions, sound effects, and color grading.",
        "careers": ["Video Editor", "Content Creator", "Multimedia Producer"],
        "schedule": "Weekdays or Weekend Intensive"
    },
    {
        "course_code": "SHORT-CAD",
        "name": "AutoCAD/ArchiCAD/Revit/SolidWorks",
        "slug": "autocad-archicad-revit-solidworks",
        "category": "short_term",
        "category_label": "Short Term",
        "duration": "6 weeks",
        "credits": 2,
        "tuition": Decimal("60000.00"),
        "instalment_fee": None,
        "instalment_breakdown": None,
        "skills": ["2D Architectural Drafting", "3D Modeling", "Revit BIM Modeling", "SolidWorks Part Modeling", "Technical Drawings"],
        "summary": "Specialized design software for engineers, architects, builders, and product developers. Produce professional blueprint deliverables.",
        "careers": ["CAD Drafter", "Architectural Modeler", "Design Technician"],
        "schedule": "Practical Hub Lab Sessions"
    },
    {
        "course_code": "SHORT-ACC",
        "name": "Sage/QuickBook/Vision/Tally",
        "slug": "sage-quickbook-vision-tally",
        "category": "short_term",
        "category_label": "Short Term",
        "duration": "6 weeks",
        "credits": 2,
        "tuition": Decimal("60000.00"),
        "instalment_fee": None,
        "instalment_breakdown": None,
        "skills": ["QuickBooks Online", "Sage 50 Accounting", "Chart of Accounts", "Payroll Processing", "Invoicing & Reconciliations", "Financial Reporting"],
        "summary": "Computerized accounting and inventory software training for small business accountants, bookkeepers, and finance staff.",
        "careers": ["Bookkeeper", "Account Assistant", "Financial Administrator"],
        "schedule": "Flexible Fast-Track"
    }
]

PAYMENT_INSTALMENT_RULES = {
    "method": "Direct Bank Transfer",
    "bank_details": {
        "bank": "Guaranty Trust Bank (GTB)",
        "account_name": "Nextserve School of Information Technology and Management",
        "account_number": "Provided upon completing enrollment Step 4"
    },
    "confirmation_time": "2 to 3 business days",
    "instalment_plan": {
        "eligible_categories": ["tech_development", "management"],
        "total_tranches": 3,
        "split_formula": "40% upfront deposit at enrollment, 30% after 30 days, 30% after 60 days",
        "breakdown": [
            {"tranche": 1, "percent": 40, "label": "First Deposit", "due": "Paid during initial enrollment"},
            {"tranche": 2, "percent": 30, "label": "Second Instalment", "due": "30 days after first payment confirmation"},
            {"tranche": 3, "percent": 30, "label": "Final Instalment", "due": "60 days after first payment confirmation"}
        ],
        "note": "Short-term courses (6 weeks, ₦60,000) require 100% full payment upon enrollment and are not eligible for instalments."
    },
    "portal_link": "/my-payment",
    "portal_description": "Students on instalment plans can visit the My Payment page anytime, enter their registered email, and receive a secure one-click link to check their balance and upload follow-up receipts."
}

ACADEMIC_POLICIES = {
    "attendance": {
        "rule": "80% Mandatory Attendance",
        "description": "Students must attend and actively participate in at least 80% of scheduled virtual live sessions or physical classes to qualify for course completion and certification."
    },
    "capstone": {
        "rule": "Capstone Project Defense",
        "description": "Every student must build, submit, and successfully defend a comprehensive, real-world capstone project evaluated by industry expert instructors before graduation."
    },
    "refund_policy": {
        "rule": "Strict No-Refund Once Started",
        "description": "Tuition is non-refundable once classes commence and course learning materials or LMS access have been issued.",
        "prior_cancellation": "Written cancellation requests submitted at least 7 calendar days before the cohort start date are eligible for a refund minus a 10% administrative processing fee.",
        "deferral": "Students in good standing facing unforeseen personal emergencies may request a formal cohort deferral to join the subsequent cohort without paying tuition again."
    },
    "code_of_conduct": {
        "rule": "Professional & Ethical Integrity",
        "description": "Mutual respect, zero tolerance for harassment or discrimination, academic honesty (no plagiarism), and professional conduct during group collaborations."
    }
}

ENROLLMENT_WORKFLOW = {
    "steps_count": 4,
    "steps": [
        {
            "step": 1,
            "name": "Personal & Contact Details",
            "details": "Enter full name, email, valid Nigerian phone number (+234 / 080...), preferred delivery format (Online, In-Person, or Hybrid), and optional referral code."
        },
        {
            "step": 2,
            "name": "Institutional Policy Acknowledgment",
            "details": "Review and agree to the Terms of Service, No-Refund Policy, Code of Conduct, and 80% Attendance Policy."
        },
        {
            "step": 3,
            "name": "Payment Plan Selection",
            "details": "Choose Full Payment or Instalment Plan (40% initial deposit). Displays payment summary and calculation."
        },
        {
            "step": 4,
            "name": "Receipt Upload & Confirmation",
            "details": "Transfer fees to Nextserve's institutional GTBank account and upload your payment slip/receipt (PDF, JPG, PNG up to 5MB)."
        }
    ],
    "abandonment_protection": "Partial student details are saved automatically at Step 1. If an applicant pauses, our admissions team can reach out to assist them with completing enrollment."
}

FREQUENT_QUESTIONS = [
    {
        "q": "How do I enroll in a programme at Nextserve?",
        "a": "Visit our website and click 'View Programmes' or 'Enroll Now' on any course card. This opens a guided 4-step form: personal details, policy acknowledgment, payment selection, and receipt upload."
    },
    {
        "q": "Can I pay in instalments?",
        "a": "Yes! All Tech Development and Management programmes support our 3-part instalment plan: 40% initial deposit at enrollment, 30% due after 30 days, and the remaining 30% due after 60 days."
    },
    {
        "q": "Are short-term courses eligible for instalment payments?",
        "a": "No, our 6-week short-term programmes (₦60,000) require full upfront payment upon enrollment."
    },
    {
        "q": "Are programmes delivered online or in person?",
        "a": "Both! Nextserve offers Online virtual cohorts accessible across Nigeria, physical in-person classes at our Lagos training hub, and Hybrid delivery formats."
    },
    {
        "q": "How long does payment confirmation take?",
        "a": "Our administrative finance team verifies bank transfer receipts within 2 to 3 business days. You will receive an official confirmation notification via email and Telegram."
    },
    {
        "q": "What is required to receive a Nextserve certificate?",
        "a": "To qualify for your accredited Nextserve Certificate of Completion, you must maintain at least 80% class attendance and successfully defend your Capstone Project."
    },
    {
        "q": "Where do I track my instalment payments or pay my balance?",
        "a": "Visit the 'My Payment' link (/my-payment) on our website, enter your registered email, and we will email you a secure direct link to view your payment history and submit follow-up receipts."
    },
    {
        "q": "Can I get a refund if I change my mind?",
        "a": "Tuition refund requests must be submitted in writing at least 7 days before the cohort start date (subject to a 10% administrative processing fee). Once classes start, payments are non-refundable, but you may request a cohort deferral."
    },
    {
        "q": "Who founded Nextserve and when was it established?",
        "a": "Nextserve was founded in 2012 (14 years of active experience) by an alumnus of Federal Polytechnic Nekede (HND Computer Science) with extensive institutional instructional experience at Synergy Systems and Yaba College of Technology."
    },
    {
        "q": "How do I speak with an admissions counselor right now?",
        "a": "You can tap the WhatsApp button on the website or message us directly on WhatsApp at +2348093344991 for instant one-on-one admissions support."
    }
]

# ── Verified Marketing Content Calendar (Link 1 Extract) ────────────────────────
MARKETING_CALENDAR_DATA: List[Dict[str, Any]] = [
    # ── Foundation / General Posts ──
    {"title": "Community Relaunch Announcement", "post_date": "May 2026", "status": "Posted", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Community"},
    {"title": "UNN CS Group Chat — Nextserve Announcement", "post_date": "May 2026", "status": "Posted", "platforms": ["WhatsApp", "Telegram"], "category": "Outreach"},
    {"title": "Cohort Launch Facebook Campaign", "post_date": "June 2026", "status": "Posted", "platforms": ["Facebook"], "category": "Enrollment"},
    {"title": "Summer Programme 2026 Announcement", "post_date": "June 2026", "status": "Posted", "platforms": ["Facebook", "Instagram"], "category": "Summer Programme"},
    {"title": "Why I Came Back to Nextserve", "post_date": "June 2026", "status": "Backlog", "platforms": ["LinkedIn", "Facebook"], "category": "Founder Story"},
    {"title": "WAEC is Done. What Happens Next?", "post_date": "July 2026", "status": "Posted", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "WAEC Campaign"},
    {"title": "The Digital Literacy Gap in Nigeria", "post_date": "July 2026", "status": "Backlog", "platforms": ["LinkedIn", "Twitter/X"], "category": "Thought Leadership"},
    {"title": "Why We Stopped Opening New Centers", "post_date": "August 2026", "status": "Draft", "platforms": ["LinkedIn"], "category": "Strategy"},
    {"title": "Why Cohort-Based Learning Works: What Our Data Shows", "post_date": "March 16, 2027", "status": "Backlog", "platforms": ["LinkedIn"], "category": "Case Study"},
    {"title": "Cohort 4 is Coming: Register Your Interest", "post_date": "March 23, 2027", "status": "Backlog", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Enrollment"},
    {"title": "VIDEO: Two Roads — Cohort 4 Enrollment Closing", "post_date": "April 10, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Enrollment Deadline"},
    {"title": "Cohort 3 Graduation and Project Showcase", "post_date": "April 14, 2027", "status": "Backlog", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Graduation & Showcase"},
    {"title": "The Nextserve Story: Where We Started and Where We Are", "post_date": "April 21, 2027", "status": "Backlog", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Brand Heritage"},
    {"title": "Cohort 4 Enrollment is Open", "post_date": "April 24, 2027", "status": "Backlog", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Cohort Kickoff"},

    # ── Video Series: Dev Series (Episodes 1 - 5) ──
    {"title": "VIDEO: First Code — Dev Ep 1", "post_date": "May 18, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Software Engineering"},
    {"title": "VIDEO: Bug Hunt — Dev Ep 2", "post_date": "May 25, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Software Engineering"},
    {"title": "VIDEO: Deployment Day — Dev Ep 3", "post_date": "June 1, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Software Engineering"},
    {"title": "VIDEO: Code Review — Dev Ep 4", "post_date": "June 8, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Software Engineering"},
    {"title": "VIDEO: Launch Night — Dev Ep 5", "post_date": "June 15, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Software Engineering"},

    # ── Video Series: UI/UX Series (Episodes 1 - 5) ──
    {"title": "VIDEO: First Wireframe — UIUX Ep 1", "post_date": "May 25, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "UI/UX Product Design"},
    {"title": "VIDEO: Color Chaos — UIUX Ep 2", "post_date": "June 1, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "UI/UX Product Design"},
    {"title": "VIDEO: User Feedback — UIUX Ep 3", "post_date": "June 8, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "UI/UX Product Design"},
    {"title": "VIDEO: Prototype Reveal — UIUX Ep 4", "post_date": "June 15, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "UI/UX Product Design"},
    {"title": "VIDEO: Final Handoff — UIUX Ep 5", "post_date": "June 22, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "UI/UX Product Design"},

    # ── Video Series: Virtual Assistance (VA Series Episodes 1 - 5) ──
    {"title": "VIDEO: First Client — VA Ep 1", "post_date": "July 13, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Virtual Assistance"},
    {"title": "VIDEO: Calendar Chaos — VA Ep 2", "post_date": "July 20, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Virtual Assistance"},
    {"title": "VIDEO: Systems In Place — VA Ep 3", "post_date": "July 27, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Virtual Assistance"},
    {"title": "VIDEO: Inbox Zero — VA Ep 4", "post_date": "August 3, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Virtual Assistance"},
    {"title": "VIDEO: Retainer Client — VA Ep 5", "post_date": "August 10, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Virtual Assistance"},

    # ── Video Series: Student Journey (Tobi Series Episodes 1 - 5) ──
    {"title": "VIDEO: Meet Tobi — Tobi Ep 1", "post_date": "August 31, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Student Journey"},
    {"title": "VIDEO: Heard That Before — Tobi Ep 2", "post_date": "September 7, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Student Journey"},
    {"title": "VIDEO: Worth a Shot — Tobi Ep 3", "post_date": "September 14, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Student Journey"},
    {"title": "VIDEO: Almost Gave Up — Tobi Ep 4", "post_date": "September 21, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Student Journey"},
    {"title": "VIDEO: I Built That — Tobi Ep 5", "post_date": "September 28, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Student Journey"},

    # ── Video Series: Two Roads Series ──
    {"title": "VIDEO: Two Roads — Cohort 2 Enrollment Closing", "post_date": "October 19, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Enrollment Drive"},

    # ── Video Series: Foundation Tracks (Before Nextserve Episodes 1 - 5) ──
    {"title": "VIDEO: Before Nextserve — Computing and Digital Literacy", "post_date": "November 2, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Digital Literacy"},
    {"title": "VIDEO: Before Nextserve — Coding", "post_date": "November 9, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Coding"},
    {"title": "VIDEO: Before Nextserve — Creative Graphics Design", "post_date": "November 16, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Graphics Design"},
    {"title": "VIDEO: Before Nextserve — Front-End Website Development", "post_date": "November 23, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "Web Development"},
    {"title": "VIDEO: Before Nextserve — AI Content Creation", "post_date": "December 7, 2026", "status": "Planning", "platforms": ["Facebook", "Instagram", "Twitter/X"], "category": "AI Tools"},

    # ── Video Series: Parent & Sponsor Perspectives (The Other Voice Episodes 1 - 4) ──
    {"title": "VIDEO: The Other Voice — What Is This One Now Ep 1", "post_date": "January 5, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram"], "category": "Parent & Sponsor Perspective"},
    {"title": "VIDEO: The Other Voice — Asking Around Ep 2", "post_date": "January 12, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram"], "category": "Parent & Sponsor Perspective"},
    {"title": "VIDEO: The Other Voice — The Conversation Ep 3", "post_date": "January 19, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram"], "category": "Parent & Sponsor Perspective"},
    {"title": "VIDEO: The Other Voice — What She Saw Ep 4", "post_date": "January 26, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram"], "category": "Parent & Sponsor Perspective"},

    # ── Video Series: Live Project Delivery (The Build Log Episodes 1 - 5) ──
    {"title": "VIDEO: The Build Log — Blank Ep 1", "post_date": "February 2, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Live Client Projects"},
    {"title": "VIDEO: The Build Log — The Error Ep 2", "post_date": "February 9, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Live Client Projects"},
    {"title": "VIDEO: The Build Log — The Commit Ep 3", "post_date": "February 16, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Live Client Projects"},
    {"title": "VIDEO: The Build Log — Live Ep 4", "post_date": "February 23, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Live Client Projects"},
    {"title": "VIDEO: The Build Log — The Result Ep 5", "post_date": "March 2, 2027", "status": "Planning", "platforms": ["Facebook", "Instagram", "LinkedIn", "Twitter/X"], "category": "Live Client Projects"}
]

# ── Strategic Campaigns & Academic Cohort Tracker (Link 2 Extract) ─────────────
CAMPAIGN_TRACKER_DATA: List[Dict[str, Any]] = [
    {
        "campaign_name": "Cohort 2 Enrollment",
        "campaign_type": "Enrollment",
        "phase": "Phase One",
        "status": "Planning",
        "start_date": "August 25, 2026",
        "end_date": "September 21, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Fill Cohort 2 for Fullstack Web Development and Front-End Web Development with high-intent enrollees.",
        "target_audience": "Nigerian professionals looking to transition into tech, university students supplementing degrees.",
        "posts_planned": 8,
        "primary_kpi": "Enrollments",
        "kpi_target": "Minimum viable cohort size achieved across flagship courses.",
        "notes": "Must lead with student proof of work, testimonials, and live instructor demos."
    },
    {
        "campaign_name": "WAEC Finisher Campaign",
        "campaign_type": "Enrollment",
        "phase": "Phase One",
        "status": "Active",
        "start_date": "July 8, 2026",
        "end_date": "August 1, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Convert WAEC finishers into summer tech immersion programme and foundational coding enrollees.",
        "target_audience": "Students who just completed WAEC exams (May/June sitting) and their parents.",
        "posts_planned": 4,
        "primary_kpi": "Enrollments",
        "kpi_target": "Minimum 5 direct enrollments sourced from WAEC cohort.",
        "notes": "Time-sensitive window before tertiary admissions resume."
    },
    {
        "campaign_name": "Pitch Contest 2026",
        "campaign_type": "Event",
        "phase": "Phase One",
        "status": "Active",
        "start_date": "July 8, 2026",
        "end_date": "February 7, 2027",
        "budget": Decimal("450000.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Launch and run the Nextserve Content Pitch Contest to generate high-performing user-generated creative tech assets.",
        "target_audience": "Nigerian content creators, graphic designers, video producers, writers, and creative tech talents.",
        "posts_planned": 17,
        "primary_kpi": "Contest Entries",
        "kpi_target": "Minimum 20 registered participants and submissions.",
        "notes": "HARD CONDITION: Do not publicize contest parameters without approved judging criteria."
    },
    {
        "campaign_name": "Cohort 3 Enrollment",
        "campaign_type": "Enrollment",
        "phase": "Phase Two",
        "status": "Planning",
        "start_date": "December 28, 2026",
        "end_date": "January 26, 2027",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Fill Cohort 3 starting January 26, 2027 across software engineering, data, and management tracks.",
        "target_audience": "General Nigerian public interested in tech careers, university graduates, and webinar attendees.",
        "posts_planned": 8,
        "primary_kpi": "Enrollments",
        "kpi_target": "Minimum 20 enrolled students.",
        "notes": "Two Roads video series and webinar funnels act as primary traffic sources."
    },
    {
        "campaign_name": "Corporate Training Pipeline",
        "campaign_type": "Partnership",
        "phase": "Phase Two",
        "status": "Planning",
        "start_date": "November 1, 2026",
        "end_date": "March 31, 2027",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Build and convert a pipeline of corporate enterprise training clients for customized workforce IT upskilling.",
        "target_audience": "HR directors, L&D managers, operations leads, and C-suite at Nigerian companies.",
        "posts_planned": 5,
        "primary_kpi": "Revenue Generated",
        "kpi_target": "Minimum 5 corporate training proposals submitted.",
        "notes": "PADIO LinkedIn profile is the primary thought leadership and outreach channel."
    },
    {
        "campaign_name": "Personal Brand — PADIO",
        "campaign_type": "Personal Brand",
        "phase": "Phase One",
        "status": "Active",
        "start_date": "July 8, 2026",
        "end_date": "April 28, 2027",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Establish Ekene Muolokwu (PADIO) as the visible, credible face of practical Nigerian tech education.",
        "target_audience": "Nigerian tech professionals, HR leads, prospective students, and university communities.",
        "posts_planned": 23,
        "primary_kpi": "Followers Gained",
        "kpi_target": "500 LinkedIn followers by end of campaign.",
        "notes": "LinkedIn is primary platform with cross-posting to Facebook and Twitter/X."
    },
    {
        "campaign_name": "Alumni Reactivation",
        "campaign_type": "Retention",
        "phase": "Phase One",
        "status": "Planning",
        "start_date": "August 5, 2026",
        "end_date": "October 31, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Identify and reconnect with former Nextserve students from 14 years of operations to build community and testimonials.",
        "target_audience": "Former Nextserve students from any year (estimated 10,000+ graduates across 14 years).",
        "posts_planned": 4,
        "primary_kpi": "Community Members",
        "kpi_target": "50 alumni questionnaire responses.",
        "notes": "Highest-priority non-enrollment campaign; vital for referral and placement network."
    },
    {
        "campaign_name": "Webinar Series (10 Role-Targeted Masterclasses)",
        "campaign_type": "Brand Awareness",
        "phase": "Phase One & Two",
        "status": "Active",
        "start_date": "August 2026",
        "end_date": "January 23, 2027",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Run 10 free role-targeted webinars under the umbrella masterclass series to introduce careers in coding, UI/UX, data, and VA.",
        "target_audience": "Career switchers, students, and aspiring digital professionals.",
        "posts_planned": 10,
        "primary_kpi": "Registrations",
        "kpi_target": "Minimum 200 cumulative webinar registrations.",
        "notes": "Direct pipeline into Cohort 2 and Cohort 3 enrollment funnels."
    },
    {
        "campaign_name": "Development Services Launch",
        "campaign_type": "Product Launch",
        "phase": "Phase Two",
        "status": "Planning",
        "start_date": "October 1, 2026",
        "end_date": "December 31, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Announce the launch of Nextserve Development Services (software development, UI design, web development agency wing).",
        "target_audience": "SMEs, startups, and institutions seeking outsourced engineering.",
        "posts_planned": 6,
        "primary_kpi": "Client Inquiries",
        "kpi_target": "Minimum 3 qualified corporate client inquiries.",
        "notes": "Provides live client-facing project briefs for advanced Nextserve cohort students."
    },
    {
        "campaign_name": "Weekend Professionals Cohort",
        "campaign_type": "Enrollment",
        "phase": "Phase One",
        "status": "Active",
        "start_date": "September 1, 2026",
        "end_date": "November 30, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Launch and fill the Weekend Professionals Cohort with a tailored curriculum for full-time 9-5 workers.",
        "target_audience": "Working professionals seeking upskilling without quitting their day jobs.",
        "posts_planned": 6,
        "primary_kpi": "Enrollments",
        "kpi_target": "Minimum 10 enrolled professionals.",
        "notes": "Focus on hybrid delivery, Saturday intensive labs, and Sunday evening mentor syncs."
    },
    {
        "campaign_name": "Nextserve Summer Programme",
        "campaign_type": "Enrollment",
        "phase": "Phase One",
        "status": "Active",
        "start_date": "July 1, 2026",
        "end_date": "September 14, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Drive enrollments for the Nextserve Summer Tech Immersion Programme.",
        "target_audience": "Secondary school leavers, undergraduate vacationers, and teens.",
        "posts_planned": 5,
        "primary_kpi": "Enrollments",
        "kpi_target": "Minimum 20 enrolled students.",
        "notes": "Fast-paced immersion with hands-on coding, graphics, and computer science foundations."
    },
    {
        "campaign_name": "Secondary School Outreach & Partnerships",
        "campaign_type": "Partnership",
        "phase": "Phase One",
        "status": "Planning",
        "start_date": "September 15, 2026",
        "end_date": "December 31, 2026",
        "budget": Decimal("0.00"),
        "campaign_manager": "Muolokwu Ekene Dominic (PADIO)",
        "campaign_objective": "Secure permissions and deliver tech career orientation presentations to graduating secondary school students.",
        "target_audience": "Secondary school principals, counselors, PTA boards, and senior secondary students.",
        "posts_planned": 4,
        "primary_kpi": "School Approvals",
        "kpi_target": "10 schools granted presentation permissions.",
        "notes": "Builds long-term pipeline for post-secondary diplomas."
    }
]

# ── Synthesized Academic Cohort Cycles & Timetable ────────────────────────────
COHORT_SCHEDULES: List[Dict[str, Any]] = [
    {
        "cohort_name": "Cohort 2 (2026)",
        "tracks": ["Fullstack Web Development", "Front-End Web Development", "Tech Diplomas"],
        "enrollment_window": "August 25, 2026 — September 21, 2026",
        "orientation_date": "September 14, 2026",
        "class_start_date": "September 21, 2026",
        "status": "In Session / Concluded",
        "delivery": "Lagos Hub Lab & Virtual Live Online"
    },
    {
        "cohort_name": "Weekend Professionals Cohort (2026)",
        "tracks": ["Management, Tech Development & Short-Term Accelerator"],
        "enrollment_window": "September 1, 2026 — November 30, 2026",
        "orientation_date": "October 24, 2026",
        "class_start_date": "November 2, 2026",
        "status": "Active Enrollment",
        "delivery": "Saturdays 10:00 AM - 4:00 PM (Lagos Hub) + Sunday Virtual Syncs"
    },
    {
        "cohort_name": "Cohort 3 (2027)",
        "tracks": ["All 26 Tech, Management & Short-Term Programmes"],
        "enrollment_window": "December 28, 2026 — January 26, 2027",
        "orientation_date": "January 19, 2027",
        "class_start_date": "January 26, 2027",
        "status": "Upcoming Flagship Intake",
        "delivery": "Nationwide Online Virtual Campus & Lagos Campus Hub"
    },
    {
        "cohort_name": "Cohort 4 (2027)",
        "tracks": ["Fullstack, UI/UX, Data, Cyber Security, Cloud, Management"],
        "enrollment_window": "March 23, 2027 — April 10, 2027",
        "orientation_date": "April 17, 2027",
        "class_start_date": "April 24, 2027",
        "status": "Scheduled Next Intake",
        "delivery": "Nationwide Online Virtual Campus & Lagos Campus Hub",
        "milestone": "Preceded by Cohort 3 Graduation & Capstone Project Showcase on April 14, 2027"
    }
]
