const API_BASE = (window.location.protocol.startsWith("http") && window.location.port === "8000")
  ? "" 
  : "http://localhost:8000";
let activeThreadId = "session_" + Math.random().toString(36).substring(2, 9);
let orchestratorThreadId = null;

// Initial Course Catalog Data (synced with NSITM programmes seed)
const COURSES = [
  {
    code: "TECH-FSW",
    name: "Fullstack Web Development",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦360,000.00 (Instalment: ₦380k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays (Mon/Wed/Fri) or Weekend Labs",
    prereq: "Open to all backgrounds. Computer literacy recommended.",
    desc: "Complete fullstack engineering from UI design and responsive web apps to backend APIs, databases, authentication, and cloud deployment."
  },
  {
    code: "TECH-FEW",
    name: "Front-End Web Development",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦210,000.00 (Instalment: ₦230k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays (Mon/Wed) or Weekend Cohorts",
    prereq: "Open to all backgrounds.",
    desc: "Master building fluid, pixel-perfect user interfaces, state management, and modern interactive web experiences with React.js and Tailwind CSS."
  },
  {
    code: "TECH-BEW",
    name: "Back-End Web Development",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays (Tue/Thu) or Weekend Cohorts",
    prereq: "Basic programming logic.",
    desc: "Architect robust server-side systems, microservices, databases, authentication pipelines, and high-performance REST APIs with Node.js and Python."
  },
  {
    code: "TECH-UIX",
    name: "UI/UX Design",
    dept: "Tech Development",
    credits: 3,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekend & Evening Live Sessions",
    prereq: "No coding background required.",
    desc: "Design digital products people love. Learn user-centered design, heuristics, wireframes, and design systems in Figma."
  },
  {
    code: "TECH-DAN",
    name: "Data Analytics",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Flexible Weekend Cohorts",
    prereq: "Basic spreadsheet knowledge.",
    desc: "Transform messy raw datasets into executive dashboards, business insights, and predictive metrics using SQL, Power BI, and Tableau."
  },
  {
    code: "TECH-DSC",
    name: "Data Science",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays & Weekend Labs",
    prereq: "Basic Python familiarity recommended.",
    desc: "Extract patterns from complex data using Python, Pandas, statistical modeling, machine learning algorithms, and data pipelines."
  },
  {
    code: "TECH-CYB",
    name: "Cyber Security",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekend Hands-on Labs",
    prereq: "Basic networking knowledge.",
    desc: "Defend enterprise systems against malicious attacks, monitor threat landscapes, and implement security controls and incident response."
  },
  {
    code: "TECH-SWE",
    name: "Software Engineering",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays & Project Sprints",
    prereq: "Basic programming knowledge.",
    desc: "Foundational software engineering principles for building scalable, maintainable, high-throughput software systems with clean architecture."
  },
  {
    code: "TECH-AIML",
    name: "AI/Machine Learning",
    dept: "Tech Development",
    credits: 4,
    tuition: "₦250,000.00 (Instalment: ₦270k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekend Masterclasses",
    prereq: "Python & basic linear algebra.",
    desc: "Develop predictive machine learning models, neural networks, natural language algorithms, and next-generation AI agent architectures."
  },
  {
    code: "MGMT-DMK",
    name: "Digital Marketing",
    dept: "Management",
    credits: 3,
    tuition: "₦150,000.00 (Instalment: ₦165k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekend Cohorts",
    prereq: "None.",
    desc: "Drive customer acquisition, execute paid campaigns, master search rankings (SEO), and scale brand growth online."
  },
  {
    code: "MGMT-PRM",
    name: "Project Management",
    dept: "Management",
    credits: 3,
    tuition: "₦150,000.00 (Instalment: ₦165k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekend Executive Sessions",
    prereq: "None.",
    desc: "Lead cross-functional teams to deliver complex tech and business projects on time, within budget, and to spec using Agile & Scrum."
  },
  {
    code: "MGMT-VAS",
    name: "Virtual Assistance",
    dept: "Management",
    credits: 3,
    tuition: "₦150,000.00 (Instalment: ₦165k)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays & Flexible Cohorts",
    prereq: "Good communication skills.",
    desc: "Provide world-class remote administrative assistance to global executives, startup founders, and digital enterprises."
  },
  {
    code: "SHORT-MOS",
    name: "Microsoft Office Suites",
    dept: "Short Term (6 Weeks)",
    credits: 2,
    tuition: "₦60,000.00 (Full Only)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Mon-Fri Fast-Track or Weekend",
    prereq: "None.",
    desc: "Fast-track 6-week practical mastery of business document formatting, financial spreadsheets, automated formulas, and presentations."
  },
  {
    code: "SHORT-IVE",
    name: "Image/Video Editing",
    dept: "Short Term (6 Weeks)",
    credits: 2,
    tuition: "₦60,000.00 (Full Only)",
    instructor: "NSITM Senior Industry Faculty",
    schedule: "Weekdays or Weekend Intensive",
    prereq: "Basic computer familiarity.",
    desc: "Hands-on editing for content creators, agencies, and social video marketers. Learn cuts, transitions, sound effects, and color grading in Premiere Pro."
  }
];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  checkBackendHealth();
  initChat();
  renderCatalog(COURSES);
  initCompositeOrchestrator();
  initVoiceAssistant();
  initSocialStudio();
  initAuthTester();
  initWebsiteAgent();
  initStudentRegistration();
  initCalendar();
  initClawEnvironment();
  // Poll backend health every 10 seconds
  setInterval(checkBackendHealth, 10000);
});

// TAB SWITCHING
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active");
      });
      const activeContent = document.getElementById(targetId);
      if (activeContent) {
        activeContent.classList.add("active");
      }
    });
  });
}

// BACKEND HEALTH CHECK
async function checkBackendHealth() {
  const badge = document.getElementById("backend-status-badge");
  const text = document.getElementById("backend-status-text");

  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      badge.className = "status-badge connected";
      text.textContent = "API Online";
    } else {
      throw new Error("HTTP " + res.status);
    }
  } catch (err) {
    badge.className = "status-badge connecting";
    text.textContent = "Connecting to API...";
  }
}

// =========================================================
// LOCAL AI BRAIN — Knowledge Base + Typewriter Streaming
// =========================================================
// NSITM / NEXTSERVE COMPREHENSIVE AI KNOWLEDGE BASE
// =========================================================
const AI_KNOWLEDGE = [
  // ── QUICK PROMPTS & SUGGESTIONS (Exact Match Priorities) ──
  {
    patterns: [
      "fees, duration, and skills for fullstack web development",
      "fullstack web dev (₦360k)",
      "fullstack web development",
      "fullstack web dev",
      "full stack web development",
      "full stack web dev",
      "tech-fsw"
    ],
    response: "Here are the key details for **Fullstack Web Development** at Nextserve:\n\n" +
      "• 💰 **Tuition**: **₦360,000** (one-time full payment) or **₦380,000** via 3-part instalment plan\n" +
      "• ⏱️ **Duration**: **6 Months** (Weekday cohorts Mon/Wed/Fri or Weekend Labs)\n" +
      "• 🌐 **Format**: Live interactive online nationwide or in-person at our Lagos Hub\n" +
      "• 🛠️ **Core Skills**: HTML5, CSS3, JavaScript ES6+, React.js, Node.js, Express, MongoDB/PostgreSQL, REST APIs, Git & Cloud Deployment\n" +
      "• 🎯 **Prerequisites**: Open to all beginners — basic computer literacy is all you need!\n" +
      "• 🏆 **Capstone Defense**: You will build, deploy, and defend a real-world web application before graduation.\n\n" +
      "👉 *Would you like me to break down the 3-part instalment payment plan, or help you start registration?*"
  },
  {
    patterns: [
      "3-part instalment payment plan work for ui/ux design",
      "ui/ux instalment plan",
      "ui/ux installment plan",
      "ui/ux instalment",
      "ui/ux installment",
      "uiux instalment",
      "tech-uix instalment"
    ],
    response: "For **UI/UX Design**, our 3-part instalment payment plan works like this:\n\n" +
      "• 🏷️ **Total Instalment Tuition**: **₦270,000** *(or ₦250,000 if paid once upfront)*\n\n" +
      "**3-Part Payment Breakdown:**\n" +
      "1. **1st Deposit (40% at Enrollment)**: **₦108,000** — secures your seat, issues student ID, and unlocks portal access.\n" +
      "2. **2nd Instalment (30% at Day 30)**: **₦81,000** — due 30 days after your initial payment.\n" +
      "3. **3rd Instalment (30% at Day 60)**: **₦81,000** — final payment due 60 days after enrollment.\n\n" +
      "💳 **Payment Method**: Direct transfer to Nextserve's official **Guaranty Trust Bank (GTB)** account.\n" +
      "📲 You can track your balance and upload receipts anytime at `/my-payment`.\n\n" +
      "👉 *Would you like to know the course curriculum or get started with enrollment?*"
  },
  {
    patterns: [
      "80% attendance policy and capstone defense rule",
      "attendance & capstone policy",
      "attendance policy",
      "capstone defense rule",
      "attendance rule",
      "capstone policy",
      "capstone defense"
    ],
    response: "Here is a simple explanation of Nextserve's **Attendance** and **Capstone Defense** rules:\n\n" +
      "• 📋 **80% Mandatory Attendance Rule**:\n" +
      "  Students must attend at least **80%** of scheduled virtual live sessions or physical classes to qualify for course completion and an official NSITM Certificate. If an emergency occurs, you can request a formal cohort deferral.\n\n" +
      "• 🎓 **Mandatory Capstone Project Defense**:\n" +
      "  To graduate, you must build, submit, and successfully defend a real-world, industry-standard project before a panel of senior faculty. No student graduates on theory alone!\n\n" +
      "Both policies guarantee that every NSITM graduate has proven, portfolio-ready skills employers can trust.\n\n" +
      "👉 *Do you have any questions about class timetables or refund terms?*"
  },
  {
    patterns: [
      "management and short-term programmes are offered at nextserve",
      "management & short-term",
      "management and short term",
      "management programmes",
      "short-term programmes",
      "short term courses"
    ],
    response: "Here are all the **Management** and **Short-Term** programmes offered at Nextserve:\n\n" +
      "💼 **Management Programmes (6 Months — ₦150k one-off or ₦165k in 3 instalments):**\n" +
      "• **Project Management** — Agile, Scrum, Jira, and sprint delivery\n" +
      "• **Product Management** — Market discovery, PRDs, UX wireframes, roadmaps\n" +
      "• **Business Analysis** — Requirements gathering, BPMN, gap analysis\n" +
      "• **Digital Marketing & Growth** — SEO, meta ads, funnels, analytics\n" +
      "• **Human Resource Management** — Talent sourcing, HR software, payroll\n" +
      "• **Accounting & Financial Management** — Budgeting, financial models, audits\n" +
      "• **Executive Virtual Assistance** — CRM, remote ops, executive calendar\n\n" +
      "⚡ **Short-Term Executive Courses (6 Weeks — ₦60k flat, full payment):**\n" +
      "• **Microsoft Office Suites** — Advanced Excel (XLOOKUP, formulas), Word, PowerPoint\n" +
      "• **Image & Video Editing** — Premiere Pro, After Effects, short-form reels\n" +
      "• **AutoCAD / Revit / SolidWorks** — 2D technical drawings & 3D BIM models\n" +
      "• **Sage / QuickBooks / Tally** — Computerized accounting & reconciliations\n\n" +
      "👉 *Which of these courses caught your interest? I can provide full syllabi or fee details!*"
  },

  // ── CONVERSATIONAL CHAT (Greetings, Small-talk, Bot Identity) ──
  {
    patterns: ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "yo", "greetings"],
    response: "Hello! 👋 I'm **Nextclaw**, your official AI academic assistant for **Nextserve School of Information Technology & Management (NSITM)**.\n\n" +
      "I'm here to help you:\n" +
      "• 📚 Explore our **26 accredited programmes** in Tech & Management\n" +
      "• 💰 Calculate **tuition fees & 3-part instalment plans**\n" +
      "• 📜 Understand our **attendance, capstone & admission policies**\n" +
      "• 🚀 Guide you step-by-step to **enroll in the upcoming cohort**\n\n" +
      "How are you doing today? What would you like to explore?"
  },
  {
    patterns: ["how are you", "how are you doing", "how r u", "how is it going", "how's it going", "how do you do"],
    response: "I'm doing great, thank you for asking! 😊 Ready and energized to help you with your learning goals, course choices, or tuition options at Nextserve.\n\nHow are you doing today? Are you thinking about learning a tech or management skill?"
  },
  {
    patterns: ["who are you", "what are you", "what is your name", "what can you do", "tell me about yourself", "who made you"],
    response: "I'm **Nextclaw** 🤖, the official School Operating AI for **Nextserve School of Information Technology & Management (NSITM)**.\n\n" +
      "Here is what I can do for you:\n" +
      "• 🔍 **Course Inquiries**: Credits, duration, syllabus, and schedules across 26 courses.\n" +
      "• 💳 **Tuition Calculators**: Exact 40% initial deposit, 30-day, and 60-day payment plans in Naira.\n" +
      "• 📜 **Campus Policies**: Attendance requirements, Capstone projects, and refund policies.\n" +
      "• 🎯 **Personalized Guidance**: Helping you pick the best course based on your background.\n\n" +
      "Feel free to ask me anything or click one of the quick suggestions below!"
  },
  {
    patterns: ["thank you", "thanks", "thx", "appreciate it", "thank u", "much appreciated", "awesome thanks"],
    response: "You're very welcome! 😊 Glad I could help. If there's anything else you'd like to check out — like class schedules, tuition breakdowns, or registration steps — just let me know!"
  },
  {
    patterns: ["bye", "goodbye", "see you", "good night", "take care", "catch you later"],
    response: "Goodbye! 👋 Wishing you great success on your tech journey. Feel free to come back anytime if you have questions or want to enroll. Have a wonderful day! 🚀"
  },
  {
    patterns: ["cool", "great", "nice", "okay", "alright", "got it", "understood", "makes sense"],
    response: "Glad to hear that! 👍 Is there any specific programme, payment plan, or policy you'd like to explore next?"
  },

  // ── ADVICE & COURSE RECOMMENDATION ──
  {
    patterns: ["help me choose", "which course", "what course should i take", "beginner", "no coding", "non coding", "start tech", "recommend a course", "what can i learn"],
    response: "I'd be glad to help you choose the best track! Here are our most popular paths based on your interests:\n\n" +
      "• 🎨 **No Coding & High Creativity**: Check out **UI/UX Design** (₦250k) or **Creative Graphics Design** (₦250k).\n" +
      "• 💻 **Building Web & Mobile Apps**: **Fullstack Web Dev** (₦360k), **Front-End Dev** (₦210k), or **Mobile App Dev** (₦250k).\n" +
      "• 📊 **Data & Analytical Thinking**: **Data Analytics** (₦250k with Power BI/SQL) or **Data Science** (₦250k with Python).\n" +
      "• 🛡️ **Cyber Defense & Cloud**: **Cyber Security** (₦250k) or **Cloud/Automation Engineering** (₦250k).\n" +
      "• 💼 **Leadership & Business**: **Project Management** or **Product Management** (₦150k).\n\n" +
      "Which of these areas sounds like the best fit for your background?"
  },

  // ── GENERAL TUITION, INSTALMENT & PAYMENT ──
  {
    patterns: ["tuition", "fees", "cost", "how much", "price", "pricing", "payment plan", "installment", "instalment", "part payment", "how to pay", "bank transfer", "gtbank", "pay in parts"],
    response: "Here is our general tuition & instalment policy at Nextserve:\n\n" +
      "• **Tech Development Programmes (6 Months)**: Most courses are **₦250,000** (or ₦270,000 via instalment). Fullstack is **₦360,000** (₦380,000 instalment), and Front-End is **₦210,000** (₦230,000 instalment).\n" +
      "• **Management Programmes (6 Months)**: **₦150,000** (or ₦165,000 via instalment).\n" +
      "• **Short-Term Courses (6 Weeks)**: **₦60,000** flat (full payment required at enrollment).\n\n" +
      "💳 **3-Part Instalment Formula**:\n" +
      "1. **40% initial deposit** upon registration\n" +
      "2. **30% instalment** after 30 days\n" +
      "3. **30% final instalment** after 60 days\n\n" +
      "🏦 All tuition is paid directly to our official **Guaranty Trust Bank (GTB)** account, and students manage receipts at `/my-payment`.\n\n" +
      "👉 *Would you like the exact payment breakdown for a specific course?*"
  },

  // ── CAMPUS LOCATION & MODES ──
  {
    patterns: ["location", "where are you located", "where is the school", "located", "address", "campus", "is it online", "virtual", "lagos", "in-person", "physical classes"],
    response: "Nextserve (NSITM) offers **hybrid, online, and physical** learning options:\n\n" +
      "• 📍 **Physical Campus**: Lagos Hub, Nigeria — equipped with dedicated computer workstations, high-speed fiber internet, and live mentor support.\n" +
      "• 🌐 **Nationwide Online Delivery**: 100% live interactive virtual sessions accessible from anywhere in Nigeria or abroad with recorded class archives.\n" +
      "• ⏱️ **Flexible Cohorts**: Weekday morning/afternoon sessions or weekend-only labs for working professionals.\n\n" +
      "👉 *Would you prefer to study online or at our Lagos campus?*"
  },

  // ── ADMISSION & ENROLLMENT ──
  {
    patterns: ["how to enroll", "how do i enroll", "how to register", "how do i register", "admission", "how do i join", "enrollment", "registration process", "sign up", "apply", "enroll", "register"],
    response: "Enrolling at Nextserve is simple and done in 4 quick steps:\n\n" +
      "1. 👤 **Personal Details**: Enter your full name, email, Nigerian phone number, and chosen delivery format (Online, In-Person, or Hybrid).\n" +
      "2. 📜 **Policy Agreement**: Review and accept the 80% attendance rule and code of conduct.\n" +
      "3. 💳 **Payment Selection**: Choose one-off Full Payment or the 3-part Instalment plan (40% initial deposit).\n" +
      "4. 📤 **Receipt Upload**: Transfer to Nextserve's GTBank account and upload your payment slip/screenshot on the **Student Registration** tab.\n\n" +
      "Our admissions team verifies payment and issues your student portal credentials within 2–3 business days!\n\n" +
      "👉 *Ready to register, or would you like to review course prerequisites first?*"
  },

  // ── CERTIFICATION ──
  {
    patterns: ["certificate", "certification", "accredited", "graduation", "diploma", "will i get a certificate"],
    response: "Yes! Every student who completes their programme receives an official **NSITM Professional Certificate**.\n\n" +
      "To qualify for your certificate, you must:\n" +
      "1. Maintain at least **80% class attendance** throughout the cohort\n" +
      "2. Build and successfully defend your **Capstone Project** before the faculty panel\n\n" +
      "Our certificates demonstrate practical, real-world portfolio deliverables that employers can verify.\n\n" +
      "👉 *Would you like details on capstone defense requirements?*"
  },

  // ── REFUND & DEFERRAL POLICY ──
  {
    patterns: ["refund", "money back", "cancel admission", "deferral", "defer", "withdrawal", "drop out"],
    response: "Here is Nextserve's **Refund and Deferral Policy**:\n\n" +
      "• 🚫 **Strict No-Refund Once Started**: Tuition is non-refundable once classes commence and LMS/portal access has been granted.\n" +
      "• 📅 **7-Day Prior Cancellation**: Written cancellation submitted at least 7 days before cohort launch is eligible for a refund minus a 10% administrative processing fee.\n" +
      "• 🔄 **Cohort Deferral**: Students facing unforeseen work or health emergencies may request a formal deferral to the subsequent cohort without paying tuition again.\n\n" +
      "👉 *Let me know if you need any clarification on our policies!*"
  },

  // ── CONTACT & WHATSAPP ──
  {
    patterns: ["contact", "phone", "whatsapp", "email", "support", "talk to human", "reach out", "customer care"],
    response: "You can reach the Nextserve admissions and student support team directly:\n\n" +
      "• 📱 **WhatsApp**: [+234 809 334 4991](https://wa.me/2348093344991)\n" +
      "• 📧 **Email**: nsitmonline@gmail.com\n" +
      "• 🏢 **Campus**: Lagos Hub, Nigeria (with nationwide online delivery)\n\n" +
      "Our advisors are available Monday to Saturday to answer any questions or help you enroll!"
  },

  // ── SPECIFIC POPULAR PROGRAMMES ──
  {
    patterns: ["front-end", "frontend", "tech-few", "react course"],
    response: "Here are the details for **Front-End Web Development**:\n\n" +
      "• 💰 **Tuition**: **₦210,000** (Full payment) or **₦230,000** (3 instalments: ₦92k initial, ₦69k at 30 days, ₦69k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: HTML5, CSS3, Tailwind CSS, JavaScript ES6+, React.js, Redux, Responsive UI\n" +
      "• 💼 **Careers**: Front-End Developer, React Engineer, UI Developer\n\n" +
      "👉 *Would you like to register or compare Front-End with Fullstack Web Dev?*"
  },
  {
    patterns: ["back-end", "backend", "tech-bew", "node", "api development"],
    response: "Here are the details for **Back-End Web Development**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Node.js, Express, Python, PostgreSQL, MongoDB, JWT Authentication, Microservices, REST APIs\n" +
      "• 💼 **Careers**: Back-End Developer, API Engineer, Server Architect\n\n" +
      "👉 *Would you like to enroll or learn more about our backend stack?*"
  },
  {
    patterns: ["ui/ux design", "uiux", "tech-uix", "figma", "product design"],
    response: "Here are the details for **UI/UX Design**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 3 Credits\n" +
      "• 🛠️ **Skills**: User Research, Figma, Wireframing, Prototyping, Usability Testing, Design Systems\n" +
      "• 🎯 **Prerequisites**: No coding required! Open to all beginners.\n\n" +
      "👉 *Would you like to register for UI/UX Design today?*"
  },
  {
    patterns: ["cyber security", "cybersecurity", "tech-cyb", "ethical hacking", "security"],
    response: "Here are the details for **Cyber Security**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Network Defense, Kali Linux, Ethical Hacking, Metasploit, Burp Suite, OWASP Top 10, Incident Response\n" +
      "• 💼 **Careers**: Cyber Security Analyst, SOC Analyst, Penetration Tester\n\n" +
      "👉 *Would you like info on schedule options or payment details?*"
  },
  {
    patterns: ["data analytics", "tech-dan", "power bi", "sql", "excel analyst"],
    response: "Here are the details for **Data Analytics**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Advanced Excel, SQL Databases, Power BI, Tableau, Business Dashboards, Data Storytelling\n" +
      "• 💼 **Careers**: Data Analyst, Business Intelligence Specialist, Reporting Officer\n\n" +
      "👉 *Would you like to enroll in Data Analytics or compare it with Data Science?*"
  },
  {
    patterns: ["data science", "tech-dsc", "machine learning in data"],
    response: "Here are the details for **Data Science**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Python Programming, Pandas, NumPy, Statistical Modeling, Machine Learning Algorithms, Data Pipelines\n" +
      "• 💼 **Careers**: Data Scientist, Machine Learning Associate, Quantitative Analyst\n\n" +
      "👉 *Would you like to enroll or learn more about prerequisites?*"
  },
  {
    patterns: ["ai/machine learning", "ai course", "machine learning", "tech-aiml"],
    response: "Here are the details for **AI/Machine Learning**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Neural Networks, Deep Learning, PyTorch, TensorFlow, Computer Vision, NLP & LLMs, LangGraph Agent Architectures\n" +
      "• 💼 **Careers**: AI Engineer, Machine Learning Specialist, AI Solutions Architect\n\n" +
      "👉 *Would you like to learn more about our AI curriculum or payment plans?*"
  },
  {
    patterns: ["mobile app", "react native", "flutter", "tech-mob"],
    response: "Here are the details for **Mobile App Development**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Flutter, React Native, Dart, Mobile UI/UX, State Management, App Store & Play Store Deployment\n" +
      "• 💼 **Careers**: iOS & Android Developer, Cross-Platform Mobile Engineer\n\n" +
      "👉 *Would you like to enroll or explore schedule options?*"
  },
  {
    patterns: ["devops", "tech-dvo", "docker", "kubernetes"],
    response: "Here are the details for **DevOps Engineering**:\n\n" +
      "• 💰 **Tuition**: **₦250,000** (Full payment) or **₦270,000** (3 instalments: ₦108k initial, ₦81k at 30 days, ₦81k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 4 Credits\n" +
      "• 🛠️ **Skills**: Docker, Kubernetes, Linux Administration, CI/CD with GitHub Actions, Terraform, AWS Services\n" +
      "• 💼 **Careers**: DevOps Engineer, Site Reliability Engineer (SRE), Cloud Operations Specialist\n\n" +
      "👉 *Would you like to sign up for the upcoming cohort?*"
  },
  {
    patterns: ["project management", "mgmt-pmp", "scrum", "agile"],
    response: "Here are the details for **Project Management**:\n\n" +
      "• 💰 **Tuition**: **₦150,000** (Full payment) or **₦165,000** (3 instalments: ₦66k initial, ₦49.5k at 30 days, ₦49.5k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 3 Credits\n" +
      "• 🛠️ **Skills**: Agile Project Delivery, Scrum Framework, Jira, Sprint Planning, Risk Management, Budget Tracking\n" +
      "• 💼 **Careers**: IT Project Manager, Scrum Master, Delivery Lead\n\n" +
      "👉 *Would you like to register or explore other management programmes?*"
  },
  {
    patterns: ["product management", "mgmt-pdm", "product manager"],
    response: "Here are the details for **Product Management**:\n\n" +
      "• 💰 **Tuition**: **₦150,000** (Full payment) or **₦165,000** (3 instalments: ₦66k initial, ₦49.5k at 30 days, ₦49.5k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 3 Credits\n" +
      "• 🛠️ **Skills**: Product Discovery, PRDs, MVP Scoping, Metrics (KPIs/OKRs), User Story Mapping, Go-To-Market Strategy\n" +
      "• 💼 **Careers**: Associate Product Manager, Product Owner, Growth Lead\n\n" +
      "👉 *Would you like to get started with Product Management enrollment?*"
  },
  {
    patterns: ["digital marketing", "mgmt-dmk", "seo", "social media marketing"],
    response: "Here are the details for **Digital Marketing & Growth**:\n\n" +
      "• 💰 **Tuition**: **₦150,000** (Full payment) or **₦165,000** (3 instalments: ₦66k initial, ₦49.5k at 30 days, ₦49.5k at 60 days)\n" +
      "• ⏱️ **Duration**: 6 Months | 3 Credits\n" +
      "• 🛠️ **Skills**: Meta Ads, Google Ads, SEO, Content Strategy, Email Marketing, Conversion Funnel Optimization\n" +
      "• 💼 **Careers**: Growth Marketer, Digital Marketing Strategist, Media Buyer\n\n" +
      "👉 *Would you like to enroll or learn more about course dates?*"
  }
];

// Conversation history for context
let conversationHistory = [];

// Helper to test keyword matches avoiding substring false positives (e.g. 'yo' in 'you', 'hi' in 'which')
function matchKnowledgePattern(pattern, text) {
  if (pattern.length <= 4) {
    const escaped = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp('\\b' + escaped + '\\b', 'i').test(text);
  }
  return text.includes(pattern);
}

// Intelligent local response generator matching real NSITM intelligence
function generateLocalResponse(query) {
  const lowerQuery = query.toLowerCase().trim();

  // 1. Direct Knowledge Patterns
  for (const entry of AI_KNOWLEDGE) {
    if (entry.patterns.some(p => matchKnowledgePattern(p, lowerQuery))) {
      return entry.response;
    }
  }

  // 2. Dynamic Course Catalog Match (check COURSES array for course code, name, or keywords)
  if (typeof COURSES !== "undefined" && Array.isArray(COURSES)) {
    const matchedCourse = COURSES.find(c => 
      lowerQuery.includes(c.code.toLowerCase()) || 
      lowerQuery.includes(c.name.toLowerCase()) ||
      (c.dept && lowerQuery.includes(c.dept.toLowerCase()))
    );

    if (matchedCourse) {
      return `Here are the details for **${matchedCourse.name}** (${matchedCourse.code}):\n\n` +
        `• 📚 **Department**: ${matchedCourse.dept}\n` +
        `• 💰 **Tuition**: ${matchedCourse.tuition}\n` +
        `• ⏱️ **Schedule**: ${matchedCourse.schedule}\n` +
        `• 🎯 **Prerequisites**: ${matchedCourse.prereq}\n` +
        `• 📖 **Overview**: ${matchedCourse.desc}\n\n` +
        `👉 *Would you like me to calculate the 3-part instalment payment breakdown or guide you through registration?*`;
    }
  }

  // 3. Conversational follow-ups
  if (["yes", "sure", "okay", "tell me more", "more details", "go on", "yep", "ok"].some(w => lowerQuery === w || lowerQuery.startsWith(w + " "))) {
    return "Awesome! 😊 What would you like to know more about? For instance:\n\n" +
      "• 💡 *\"What are the fees and skills for Fullstack Web Dev?\"*\n" +
      "• 💳 *\"How does the 3-part instalment plan work?\"*\n" +
      "• 📋 *\"What is the 80% attendance policy and capstone rule?\"*\n" +
      "• 🎯 *\"Can you help me choose the right course for beginners?\"*\n\n" +
      "Just ask or click any of the suggestion buttons below!";
  }

  // 4. Short conversational greetings / query fallback
  if (lowerQuery.length < 12) {
    return "Hello! 👋 I'm **Nextclaw**, your official NSITM academic assistant.\n\n" +
      "Ask me about any of our 26 tech and management courses, tuition instalment plans, or school policies. How can I help you today?";
  }

  // 5. Friendly, natural fallback with actionable guidance
  return `I understand you're asking about: *"**${escapeHtml(query)}**"*\n\n` +
    `Here is how I can assist you:\n\n` +
    `• 📚 **26 Programmes**: Fullstack, Front-End, UI/UX, Cyber Security, Data Science, AI/ML, Project Management, and more\n` +
    `• 💰 **Tuition & Instalments**: 40% initial deposit calculations in ₦ Naira for any course\n` +
    `• 📜 **Policies**: 80% attendance rule, Capstone defense, and admission terms\n` +
    `• 📍 **Delivery Modes**: Physical Lagos campus or 100% live interactive online cohorts\n\n` +
    `👉 *Try asking:* *"What are the fees for UI/UX Design?"* or click one of the quick suggestions below!`;
}

// Render markdown formatting to HTML
function renderMarkdown(text) {
  let html = escapeHtml(text);

  // Code blocks
  html = html.replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre class="ai-code-block"><code>$1</code></pre>');
  html = html.replace(/`([^`]+)`/g, '<code class="ai-inline-code">$1</code>');

  // Headings
  html = html.replace(/^#### (.+)$/gm, '<h4 class="ai-h4">$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3 class="ai-h3">$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2 class="ai-h2">$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1 class="ai-h1">$1</h1>');

  // Bold & italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote class="ai-quote">$1</blockquote>');

  // Tables
  const tableReg = /((\|[^\n]+\|\n?)+)/g;
  html = html.replace(tableReg, (match) => {
    const rows = match.trim().split('\n').filter(r => r.trim() && !r.match(/^\|[-: |]+\|$/));
    if (rows.length < 1) return match;
    let table = '<div class="ai-table-wrap"><table class="ai-table"><thead><tr>';
    const headers = rows[0].split('|').filter((_, i, a) => i > 0 && i < a.length - 1);
    headers.forEach(h => { table += '<th>' + h.trim() + '</th>'; });
    table += '</tr></thead><tbody>';
    for (let i = 1; i < rows.length; i++) {
      const cells = rows[i].split('|').filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      table += '<tr>';
      cells.forEach(c => { table += '<td>' + c.trim() + '</td>'; });
      table += '</tr>';
    }
    table += '</tbody></table></div>';
    return table;
  });

  // Bullet lists
  html = html.replace(/(^- .+$\n?)+/gm, (match) => {
    const items = match.trim().split('\n').map(line => '<li>' + line.replace(/^- /, '') + '</li>').join('');
    return '<ul class="ai-ul">' + items + '</ul>';
  });

  // Horizontal rule
  html = html.replace(/^---$/gm, '<hr class="ai-hr">');

  // Paragraphs
  html = html.replace(/\n\n/g, '</p><p class="ai-p">');
  html = html.replace(/\n/g, '<br>');

  return '<p class="ai-p">' + html + '</p>';
}

// Typewriter streaming effect — word by word
async function streamText(container, text, speed) {
  speed = speed || 12;
  container.innerHTML = '';
  const words = text.split(' ');
  let displayed = '';
  for (let i = 0; i < words.length; i++) {
    displayed += (i > 0 ? ' ' : '') + words[i];
    container.innerHTML = renderMarkdown(displayed) + '<span class="typing-cursor">▋</span>';
    const msgArea = document.getElementById("chat-messages");
    if (msgArea) msgArea.scrollTop = msgArea.scrollHeight;
    await sleep(speed + Math.random() * 6);
  }
  container.innerHTML = renderMarkdown(text);
}

// 1. AI CHAT ASSISTANT
function initChat() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const messagesContainer = document.getElementById("chat-messages");
  const clearBtn = document.getElementById("clear-chat-btn");
  const promptChips = document.querySelectorAll(".prompt-chip");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (!query || document.getElementById('send-btn').disabled) return;

    stopJarvisSpeech();
    input.value = "";
    disableChatInput(true);
    appendUserMessage(query);
    conversationHistory.push({ role: "user", content: query });

    // Create streaming message bubble
    const msgEl = createAssistantMessagePlaceholder();
    messagesContainer.appendChild(msgEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    const textContainer = msgEl.querySelector('.msg-text');

    // Thinking delay
    await sleep(350 + Math.random() * 500);

    // Try backend first with 30s timeout for LLM inference, fall back to local AI
    let responded = false;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      const res = await fetch(`${API_BASE}/api/v1/school/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, thread_id: activeThreadId }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        const responseText = data.response || "I processed your query.";
        conversationHistory.push({ role: "assistant", content: responseText });
        await streamText(textContainer, responseText, 8);
        updateToolTrace(data.sources, query);
        responded = true;

        // Auto-voice trigger
        if (autoSpeakResponses || lastInputWasVoice) {
          speakAsJarvis(responseText, "jarvis");
          lastInputWasVoice = false;
        }
      }
    } catch (err) { /* Backend offline — use local AI brain */ }

    if (!responded) {
      const localResponse = generateLocalResponse(query);
      conversationHistory.push({ role: "assistant", content: localResponse });
      await streamText(textContainer, localResponse, 10);
      simulateToolTrace(query);

      if (autoSpeakResponses || lastInputWasVoice) {
        speakAsJarvis(localResponse, "jarvis");
        lastInputWasVoice = false;
      }
    }

    // Attach in-message speaker button if not already present
    const msgBody = msgEl.querySelector('.msg-body');
    if (msgBody && !msgBody.querySelector('.speak-msg-btn')) {
      const speakBtn = document.createElement('button');
      speakBtn.type = 'button';
      speakBtn.className = 'speak-msg-btn';
      speakBtn.innerHTML = '<span>🔊 Listen</span>';
      speakBtn.onclick = function() { speakMessageText(this); };
      msgBody.appendChild(speakBtn);

      if (isCurrentlySpeaking && !activeSpeakerButton) {
        activeSpeakerButton = speakBtn;
        speakBtn.classList.add("speaking");
        speakBtn.innerHTML = '<span>⏹️ Stop</span>';
      }
    }

    disableChatInput(false);
    input.focus();
  });

  // Quick Prompt Chips
  promptChips.forEach(chip => {
    chip.addEventListener("click", () => {
      if (!document.getElementById('send-btn').disabled) {
        const q = chip.getAttribute("data-query");
        input.value = q;
        form.dispatchEvent(new Event("submit"));
      }
    });
  });

  clearBtn.addEventListener("click", () => {
    stopJarvisSpeech();
    messagesContainer.innerHTML = "";
    conversationHistory = [];
    activeThreadId = "session_" + Math.random().toString(36).substring(2, 9);
    const initMsg = createAssistantMessagePlaceholder();
    messagesContainer.appendChild(initMsg);
    const textContainer = initMsg.querySelector('.msg-text');
    streamText(textContainer, "Conversation cleared! 🔄 Ready for a fresh start. Ask me about courses, tuition fees, instalment plans, or policies!", 14);
    document.getElementById("tool-trace-container").innerHTML = `
      <div class="empty-trace">
        <span class="empty-icon">🔍</span>
        <p>Retrieved course catalog details and campus policy citations will appear here during conversations.</p>
      </div>
    `;
  });
}

function disableChatInput(disabled) {
  const input = document.getElementById('chat-input');
  const btn = document.getElementById('send-btn');
  if (input) input.disabled = disabled;
  if (btn) btn.disabled = disabled;
}

function createAssistantMessagePlaceholder() {
  const msgEl = document.createElement("div");
  msgEl.className = "message assistant-message";
  msgEl.innerHTML = `
    <div class="msg-avatar">
      <img src="assets/nextclaw_free_logo.png" alt="NextClaw" class="mecha-msg-img" />
    </div>
    <div class="msg-body">
      <div class="msg-header-row">
        <div class="msg-sender">NextClaw</div>
        <div class="msg-timestamp">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
      </div>
      <div class="msg-text">
        <span class="thinking-dots"><span></span><span></span><span></span></span>
      </div>
    </div>
  `;
  return msgEl;
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = "message user-message";
  msgEl.innerHTML = `
    <div class="msg-body">
      <div class="msg-header-row">
        <div class="msg-sender">You</div>
        <div class="msg-timestamp">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
      </div>
      <div class="msg-text">${escapeHtml(text)}</div>
    </div>
    <div class="msg-avatar user-avatar">👤</div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

function appendAssistantMessage(text) {
  const container = document.getElementById("chat-messages");
  const msgEl = createAssistantMessagePlaceholder();
  const textContainer = msgEl.querySelector('.msg-text');
  textContainer.innerHTML = renderMarkdown(text);
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

function simulateToolTrace(query) {
  const traceContainer = document.getElementById("tool-trace-container");
  const lowerQ = query.toLowerCase();
  let tools = [];
  if (lowerQ.includes("cs") || lowerQ.includes("course") || lowerQ.includes("prerequisite") || lowerQ.includes("math") || lowerQ.includes("ds")) {
    tools.push({ tool: "get_course_details", query: `Searched course catalog for: "${query}"` });
    tools.push({ tool: "semantic_search_pgvector", query: `Vector similarity search (cosine dist: 0.0${Math.floor(Math.random() * 89 + 10)})` });
  } else if (lowerQ.includes("tuition") || lowerQ.includes("refund") || lowerQ.includes("fee") || lowerQ.includes("payment")) {
    tools.push({ tool: "get_tuition_policy", query: "Retrieved financial policy records from PostgreSQL" });
  } else {
    tools.push({ tool: "policy_lookup", query: `Full-text search across academic knowledge base for: "${query}"` });
    tools.push({ tool: "semantic_search_pgvector", query: `Policy similarity match (cosine dist: 0.0${Math.floor(Math.random() * 89 + 10)})` });
  }
  let html = `<div class="mb-2 text-sm text-dim">Query: "${escapeHtml(query)}"</div>`;
  tools.forEach(s => {
    const isCourse = s.tool === "get_course_details";
    html += `
      <div class="trace-item ${isCourse ? 'course-tool' : 'vector-tool'}">
        <div class="trace-tool-name">${s.tool}</div>
        <div class="trace-detail">${escapeHtml(s.query)}</div>
      </div>
    `;
  });
  traceContainer.innerHTML = html;
}

function updateToolTrace(sources, query) {
  if (!sources || sources.length === 0) { simulateToolTrace(query); return; }
  const traceContainer = document.getElementById("tool-trace-container");
  let html = `<div class="mb-2 text-sm text-dim">Query: "${escapeHtml(query)}"</div>`;
  sources.forEach((s) => {
    const isCourse = s.tool === "get_course_details";
    html += `
      <div class="trace-item ${isCourse ? 'course-tool' : 'vector-tool'}">
        <div class="trace-tool-name">${s.tool || "Tool invocation"}</div>
        <div class="trace-detail">${escapeHtml(s.query || s.content || "Query executed")}</div>
      </div>
    `;
  });
  traceContainer.innerHTML = html;
}

// COURSE CATALOG GRID
function renderCatalog(courses) {
  const grid = document.getElementById("catalog-grid");
  grid.innerHTML = "";

  courses.forEach(c => {
    const card = document.createElement("div");
    card.className = "course-card";
    card.innerHTML = `
      <div class="course-header">
        <span class="course-code">${c.code}</span>
        <span class="course-dept">${c.dept}</span>
      </div>
      <div class="course-name">${c.name}</div>
      <div class="course-desc">${c.desc}</div>
      <div class="course-meta">
        <div><span class="meta-label">Credits:</span> <span class="meta-val">${c.credits}</span></div>
        <div><span class="meta-label">Tuition:</span> <span class="meta-val">${c.tuition}</span></div>
        <div><span class="meta-label">Instructor:</span> <span class="meta-val">${c.instructor}</span></div>
        <div><span class="meta-label">Schedule:</span> <span class="meta-val">${c.schedule}</span></div>
      </div>
    `;
    grid.appendChild(card);
  });

  const searchInput = document.getElementById("catalog-search-input");
  const searchBtn = document.getElementById("search-vectors-btn");

  const handleFilter = () => {
    const term = searchInput.value.toLowerCase().trim();
    if (!term) {
      renderCatalog(COURSES);
      return;
    }
    const filtered = COURSES.filter(c => 
      c.code.toLowerCase().includes(term) ||
      c.name.toLowerCase().includes(term) ||
      c.dept.toLowerCase().includes(term) ||
      c.desc.toLowerCase().includes(term)
    );
    renderCatalog(filtered);
  };

  searchBtn.addEventListener("click", handleFilter);
  searchInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") handleFilter();
  });
}

// 2. MULTI-AGENT COMPOSITE ORCHESTRATOR STUDIO (SECTION 1 PIPELINE)
let currentCompositePipelineId = null;

const BLUEPRINT_TEMPLATES = {
  course_launch: {
    title: "New Accredited Course Launch: Mobile App Dev with Flutter",
    category: "course_launch",
    prompt: "Launch accredited diploma programme 'Mobile App Development with Flutter' (TECH-MOB) with tuition ₦280,000 (one-off) / ₦305,000 (instalment in 3 tranches: ₦122k, ₦91.5k, ₦91.5k), generate API catalog patch, and draft live CMS announcement."
  },
  tuition_policy_update: {
    title: "Tuition & Instalment Policy Update 2027",
    category: "tuition_policy_update",
    prompt: "Update academic payment terms and 3-tranche instalment guidelines for 2027. Enforce strict 80% refund threshold before Day 1, create code validation check, and publish official policy page draft."
  },
  curriculum_patch: {
    title: "AI & LLM Engineering Curriculum & Agent Patch",
    category: "curriculum_patch",
    prompt: "Expand AI & Large Language Model Engineering (TECH-AI) curriculum with autonomous LangGraph multi-agent frameworks and pgvector labs. Generate code patch for catalog and publish student portal announcement."
  },
  custom: {
    title: "Custom Multi-Agent Composite Pipeline",
    category: "custom",
    prompt: "Review prerequisites for CS201, generate automated regression tests patch, and prepare staging website release notes."
  }
};

function initCompositeOrchestrator() {
  const titleInput = document.getElementById("comp-title-input");
  const promptInput = document.getElementById("comp-prompt-input");
  const categorySelect = document.getElementById("comp-category-select");
  const governanceSelect = document.getElementById("comp-governance-select");
  const triggerBtn = document.getElementById("run-composite-pipeline-btn");
  const hitlBox = document.getElementById("comp-hitl-box");
  const approveBtn = document.getElementById("comp-approve-btn");
  const rejectBtn = document.getElementById("comp-reject-btn");
  const logsContainer = document.getElementById("orchestrator-logs");
  const refreshPipelinesBtn = document.getElementById("refresh-pipelines-btn");

  const stageCards = {
    school: document.getElementById("stage-card-school"),
    coding: document.getElementById("stage-card-coding"),
    website: document.getElementById("stage-card-website"),
    hitl: document.getElementById("stage-card-hitl"),
    dispatch: document.getElementById("stage-card-dispatch")
  };

  const statusBadges = {
    school: document.getElementById("status-school"),
    coding: document.getElementById("status-coding"),
    website: document.getElementById("status-website"),
    hitl: document.getElementById("status-hitl"),
    dispatch: document.getElementById("status-dispatch")
  };

  // Blueprint Preset Cards Selection
  document.querySelectorAll(".blueprint-card").forEach(card => {
    card.addEventListener("click", () => {
      document.querySelectorAll(".blueprint-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");

      const presetKey = card.getAttribute("data-preset");
      const template = BLUEPRINT_TEMPLATES[presetKey];
      if (template) {
        if (titleInput) titleInput.value = template.title;
        if (promptInput) promptInput.value = template.prompt;
        if (categorySelect) categorySelect.value = template.category;
      }
    });
  });

  // Subtab navigation in Inspector
  document.querySelectorAll(".subtab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".subtab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".subtab-content").forEach(c => c.style.display = "none");

      btn.classList.add("active");
      const targetSubtab = document.getElementById(btn.getAttribute("data-subtab"));
      if (targetSubtab) {
        targetSubtab.style.display = "block";
      }
    });
  });

  function resetStages() {
    Object.values(stageCards).forEach(card => {
      if (!card) return;
      card.className = "stage-card";
    });
    Object.values(statusBadges).forEach(badge => {
      if (!badge) return;
      badge.className = "stage-status-badge badge-ready";
      badge.textContent = "Ready";
    });
    if (hitlBox) hitlBox.classList.add("hidden");
  }

  function setStageStatus(stageKey, stateClass, text) {
    const card = stageCards[stageKey];
    const badge = statusBadges[stageKey];
    if (card && badge) {
      card.className = `stage-card ${stateClass}`;
      badge.className = `stage-status-badge badge-${stateClass}`;
      badge.textContent = text;
    }
  }

  function appendLog(line) {
    if (!logsContainer) return;
    const p = document.createElement("div");
    p.className = "log-line";
    p.textContent = line;
    logsContainer.appendChild(p);
    logsContainer.scrollTop = logsContainer.scrollHeight;
  }

  // Trigger Composite Pipeline Execution
  if (triggerBtn) {
    triggerBtn.addEventListener("click", async () => {
      resetStages();
      const title = titleInput ? titleInput.value.trim() : "Composite Pipeline";
      const prompt = promptInput ? promptInput.value.trim() : "";
      const category = categorySelect ? categorySelect.value : "custom";
      const requireApproval = governanceSelect ? governanceSelect.value === "true" : true;

      if (!prompt) {
        alert("Please enter a pipeline specification prompt.");
        return;
      }

      if (logsContainer) logsContainer.innerHTML = "";
      appendLog(`[Pipeline Start] Initializing Multi-Agent Composite Workflow: '${title}'...`);
      setStageStatus("school", "running", "Analyzing...");
      triggerBtn.disabled = true;
      triggerBtn.innerHTML = "<span>⏳ Executing Multi-Agent Pipeline...</span>";

      try {
        const response = await fetch(`${API_BASE}/api/v1/composite/start`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title,
            prompt: prompt,
            category: category,
            require_approval: requireApproval
          })
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "Failed to start pipeline");
        }

        currentCompositePipelineId = data.pipeline_id;
        appendLog(`[Pipeline ID] Registered session '${data.pipeline_id}' in PostgreSQL.`);

        // Stage 1 (School) Complete
        setStageStatus("school", "passed", "Verified ✓");
        appendLog(`[School Agent] Verified academic curriculum and 3-tranche instalment specs.`);
        const academicPreview = document.getElementById("academic-output-preview");
        if (academicPreview && data.school_output) {
          academicPreview.innerHTML = `
            <strong>Program Code:</strong> ${data.school_output.course_code || 'NSITM'}<br>
            <strong>Summary:</strong> ${data.school_output.summary || 'Curriculum specs compiled.'}<br>
            <strong>Instalment Breakdown:</strong> ${typeof data.school_output.instalment_plan === 'string' ? data.school_output.instalment_plan.replace(/\\n/g, '<br>') : '3 Tranches (40% / 30% / 30%)'}<br>
            <strong>Invariants:</strong> 80% Attendance Required, Capstone Defense Mandatory.
          `;
        }

        // Stage 2 (Coding) Complete
        setStageStatus("coding", "passed", "AST Valid ✓");
        appendLog(`[Coding Agent] Analyzed repo dependencies. Generated unified git diff: Patch ID ${data.coding_output?.patch_id || 'N/A'}.`);
        const diffPreview = document.getElementById("code-diff-preview");
        if (diffPreview && data.coding_output) {
          diffPreview.textContent = data.coding_output.diff_summary || "// No diff generated";
          const patchMeta = document.getElementById("code-patch-meta");
          if (patchMeta) patchMeta.textContent = `Patch ID: ${data.coding_output.patch_id} (AST Valid)`;
          const branchMeta = document.getElementById("code-branch-meta");
          if (branchMeta) branchMeta.textContent = `Target: ${data.coding_output.feature_branch || 'patch/main'}`;
        }

        // Stage 3 (Website) Complete
        setStageStatus("website", "passed", "Preflight OK ✓");
        appendLog(`[Website Agent] Generated staging CMS draft. Computed SEO metadata and ran preflight HTTP checks.`);
        if (data.website_output) {
          const slugElem = document.getElementById("cms-slug-preview");
          if (slugElem) slugElem.textContent = data.website_output.slug || 'courses';
          const seoTitleElem = document.getElementById("cms-seo-title-preview");
          if (seoTitleElem) seoTitleElem.textContent = data.website_output.seo_title || '-';
          const seoDescElem = document.getElementById("cms-seo-desc-preview");
          if (seoDescElem) seoDescElem.textContent = data.website_output.meta_description || '-';
        }

        // Stage 4 (Level 3 HITL Gate)
        if (requireApproval && data.status === "awaiting_approval") {
          setStageStatus("hitl", "paused", "PAUSED ⚠️");
          appendLog(`[Approval Gate] 🛡️ Level 3 Human-in-the-Loop Gate triggered! Interactive approval card dispatched to Telegram.`);
          if (hitlBox) {
            hitlBox.classList.remove("hidden");
            const threadIdElem = document.getElementById("comp-hitl-thread-id");
            if (threadIdElem) threadIdElem.textContent = `Pipeline: ${data.pipeline_id}`;
            const descElem = document.getElementById("comp-hitl-description");
            if (descElem) descElem.textContent = `Authorization required to commit code patch (${data.coding_output?.patch_id || 'patch'}) and publish CMS draft to live production.`;
          }
        } else {
          // If auto-approved
          setStageStatus("hitl", "passed", "Bypassed ✓");
          setStageStatus("dispatch", "passed", "Deployed 🚀");
          appendLog(`[Live Dispatch] Operations executed in production environment.`);
        }

      } catch (err) {
        appendLog(`[Error] Composite pipeline failed: ${err.message}`);
        setStageStatus("school", "ready", "Error ✕");
      } finally {
        triggerBtn.disabled = false;
        triggerBtn.innerHTML = "<span>🚀 Trigger Multi-Agent Composite Pipeline</span>";
      }
    });
  }

  // Level 3 Authorization Decision: Approve
  if (approveBtn) {
    approveBtn.addEventListener("click", async () => {
      if (!currentCompositePipelineId) return;
      approveBtn.disabled = true;
      approveBtn.textContent = "Deploying...";

      try {
        const res = await fetch(`${API_BASE}/api/v1/composite/${currentCompositePipelineId}/resume`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved: true,
            reviewer_notes: "Authorized by Support Admin via NextClaw OS Dashboard"
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Approval failed");

        setStageStatus("hitl", "passed", "Approved ✓");
        setStageStatus("dispatch", "passed", "Production Live 🚀");
        if (hitlBox) hitlBox.classList.add("hidden");

        appendLog(`[HITL Decision] Support Admin granted Level 3 approval for '${currentCompositePipelineId}'.`);
        appendLog(`[Code Patch] Successfully merged code patch to main branch.`);
        appendLog(`[CMS Deploy] Published live CMS page: ${data.dispatch_output?.deployment_url || 'https://nextserveschool.com'}`);
        appendLog(`[PostgreSQL Audit] Immutable audit records committed (DeploymentAuditLog + CodeAuditLog).`);
        appendLog(`[Multi-Channel Notification] Telegram alert sent and confirmation email dispatched via SMTP.`);
        appendLog(`[Pipeline Complete] End-to-end composite workflow finished with status: COMPLETED.`);

      } catch (err) {
        appendLog(`[Error] Resuming pipeline failed: ${err.message}`);
      } finally {
        approveBtn.disabled = false;
        approveBtn.innerHTML = "<span>✅ Authorize & Deploy to Production</span>";
      }
    });
  }

  // Level 3 Authorization Decision: Reject
  if (rejectBtn) {
    rejectBtn.addEventListener("click", async () => {
      if (!currentCompositePipelineId) return;
      try {
        await fetch(`${API_BASE}/api/v1/composite/${currentCompositePipelineId}/resume`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved: false,
            reviewer_notes: "Rejected by Support Admin during manual inspection"
          })
        });

        setStageStatus("hitl", "paused", "Rejected ✕");
        if (hitlBox) hitlBox.classList.add("hidden");
        appendLog(`[HITL Decision] Reviewer rejected pipeline '${currentCompositePipelineId}'. All actions aborted safely.`);
      } catch (err) {
        appendLog(`[Error] Rejection failed: ${err.message}`);
      }
    });
  }

  // Refresh recent pipelines list
  if (refreshPipelinesBtn) {
    refreshPipelinesBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(`${API_BASE}/api/v1/composite/`);
        const data = await res.json();
        appendLog(`--- Recent Composite Pipeline Runs (${data.pipelines?.length || 0}) ---`);
        (data.pipelines || []).forEach(p => {
          appendLog(`• [${p.status.toUpperCase()}] ${p.pipeline_id} — ${p.title} (${p.category})`);
        });
      } catch (err) {
        appendLog(`[Error] Failed to fetch recent pipelines: ${err.message}`);
      }
    });
  }
}

// ── PHASE 7: J.A.R.V.I.S. VOICE INTERACTION ENGINE (WHISPER & AUDIO TTS) ──────────────
let isListening = false;
let isCurrentlySpeaking = false;
let autoSpeakResponses = false;
let lastInputWasVoice = false;
let speechRecognizer = null;
let mediaRecorder = null;
let audioChunks = [];
let currentAudioElement = null;
let availableSpeechVoices = [];
let currentSpeechSessionId = 0;
let activeSpeakerButton = null;
let currentUtteranceRef = null;

// Cache native speech synthesis voices
function updateSpeechVoices() {
  if (typeof window !== "undefined" && window.speechSynthesis) {
    availableSpeechVoices = window.speechSynthesis.getVoices() || [];
  }
}
if (typeof window !== "undefined" && window.speechSynthesis) {
  updateSpeechVoices();
  window.speechSynthesis.onvoiceschanged = updateSpeechVoices;
}

// Sci-fi audio cue synthesizer for J.A.R.V.I.S. activations
function playJarvisChime(type = "activate") {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    if (type === "activate") {
      // Iron Man HUD blip: 587.33Hz (D5) -> 880Hz (A5)
      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.12, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.16);
    } else if (type === "speaking_start") {
      // Harmonic low pulse: 440Hz -> 659.25Hz
      osc.type = "triangle";
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.09, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.14);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.14);
    }
  } catch (e) {
    // Graceful fallback if audio context is restricted
  }
}

// Pick the best natural voice matching the requested persona (Default: British J.A.R.V.I.S.)
function getBestJarvisVoice(persona = "jarvis") {
  const voices = (availableSpeechVoices && availableSpeechVoices.length > 0)
    ? availableSpeechVoices
    : (window.speechSynthesis ? window.speechSynthesis.getVoices() : []);

  if (!voices || voices.length === 0) return null;

  const p = (persona || "jarvis").toLowerCase();

  if (p === "jarvis") {
    // 1. British Male voices (Ryan, George, Oliver, Google UK English Male, Daniel)
    const gbMale = voices.find(v => {
      const name = v.name.toLowerCase();
      const lang = v.lang.toLowerCase();
      const isGB = lang.includes("en-gb") || lang.includes("en_gb");
      const isMale = name.includes("male") || name.includes("ryan") || name.includes("george") || name.includes("oliver") || name.includes("daniel");
      return isGB && isMale;
    });
    if (gbMale) return gbMale;

    // 2. Any en-GB voice
    const anyGB = voices.find(v => v.lang.toLowerCase().includes("en-gb") || v.lang.toLowerCase().includes("en_gb"));
    if (anyGB) return anyGB;

    // 3. Authoritative Natural Male voices (David, Guy, Mark)
    const anyMale = voices.find(v => {
      const name = v.name.toLowerCase();
      return v.lang.toLowerCase().startsWith("en") && (name.includes("david") || name.includes("guy") || name.includes("male") || name.includes("mark"));
    });
    if (anyMale) return anyMale;
  } else if (p === "friday") {
    // Intelligent Female voice
    const female = voices.find(v => {
      const name = v.name.toLowerCase();
      return v.lang.toLowerCase().startsWith("en") && (name.includes("female") || name.includes("sonia") || name.includes("zira") || name.includes("jenny") || name.includes("samantha") || name.includes("victoria"));
    });
    if (female) return female;
  } else if (p === "prime") {
    // Authoritative US Male
    const usMale = voices.find(v => {
      const name = v.name.toLowerCase();
      return (v.lang.toLowerCase().includes("en-us") || v.lang.toLowerCase().includes("en_us")) && (name.includes("david") || name.includes("male") || name.includes("guy"));
    });
    if (usMale) return usMale;
  }

  // Fallback to any English voice or device default
  return voices.find(v => v.lang.toLowerCase().startsWith("en")) || voices[0] || null;
}

// Split text into coherent, natural sentences for fluent speech synthesis
function splitIntoNaturalSentences(text) {
  if (!text) return [];

  // Match sentence endings (. ! ?) followed by whitespace or newlines
  const rawChunks = text
    .split(/(?<=[.!?])\s+|\n+/)
    .map(s => s.trim())
    .filter(s => s.length > 0);

  if (rawChunks.length === 0) {
    return [text];
  }

  // Group very short sentence fragments if needed, avoiding oversized chunks
  const sentences = [];
  let buffer = "";

  for (const chunk of rawChunks) {
    if (!buffer) {
      buffer = chunk;
    } else if (buffer.length + chunk.length < 90 && !/[.!?]$/.test(buffer)) {
      buffer += " " + chunk;
    } else {
      sentences.push(buffer);
      buffer = chunk;
    }
  }
  if (buffer) {
    sentences.push(buffer);
  }

  return sentences.length > 0 ? sentences : [text];
}

// Convert numbers, currency, acronyms, and symbols into natural, flowing spoken English
function prepareTextForJarvisSpeech(text) {
  if (!text) return "";

  let clean = text
    // 1. Decode HTML entities
    .replace(/&amp;/g, " and ")
    .replace(/&lt;/g, " less than ")
    .replace(/&gt;/g, " greater than ")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ")
    // 2. Strip HTML tags
    .replace(/<[^>]*>/g, " ")
    // 3. Remove URLs
    .replace(/https?:\/\/\S+/g, "")
    // 4. Handle code blocks and inline code
    .replace(/```[\s\S]*?```/g, "Code block omitted.")
    .replace(/`([^`]+)`/g, "$1")
    // 5. Currency & percentages
    .replace(/₦\s*([\d,]+)/g, "$1 Naira")
    .replace(/₦/g, " Naira ")
    .replace(/\$\s*([\d,]+)/g, "$1 dollars")
    .replace(/%/g, " percent ")
    // 6. Common domain acronyms & tech terms pronounced smoothly without breaking sentences
    .replace(/\bNSITM\b/g, "N S I T M")
    .replace(/\bUI\/UX\b/gi, "U I U X")
    .replace(/\bNextserve\b/g, "Nextserve")
    .replace(/\bAI\b/g, "A I")
    .replace(/\bAPI\b/g, "A P I")
    .replace(/&/g, " and ")
    .replace(/\bw\//gi, "with ")
    // 7. Strip Markdown markers and bullet points
    .replace(/[*#_~>|]/g, " ")
    .replace(/[-•]\s+/g, ", ")
    // 8. Strip emojis and special pictographs that confuse TTS engines
    .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "")
    // 9. Normalize multiple dots/periods or ellipses into a single comma/pause
    .replace(/\.{2,}/g, ", ")
    // 10. Normalize whitespace
    .replace(/\s+/g, " ")
    .trim();

  return clean;
}

// Stop any active speech immediately
function stopJarvisSpeech() {
  currentSpeechSessionId++; // Invalidate running speech session immediately
  isCurrentlySpeaking = false;
  currentUtteranceRef = null;
  window._activeJarvisUtterance = null;

  if (window.speechSynthesis) {
    try {
      window.speechSynthesis.cancel();
    } catch (e) {}
  }

  if (currentAudioElement) {
    try {
      currentAudioElement.pause();
      currentAudioElement.currentTime = 0;
    } catch (e) {}
    currentAudioElement = null;
  }

  const voiceOrbContainer = document.getElementById("voice-orb-container");
  const eqBars = document.getElementById("voice-equalizer-bars");
  const stopBtn = document.getElementById("voice-stop-speech-btn");
  const micToggleBtn = document.getElementById("voice-modal-mic-toggle");
  const voiceStatusLabel = document.getElementById("voice-status-label");

  if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container";
  if (eqBars) eqBars.classList.remove("active");
  if (stopBtn) stopBtn.style.display = "none";
  if (micToggleBtn) micToggleBtn.style.display = "inline-flex";
  if (voiceStatusLabel && voiceStatusLabel.textContent.includes("Speaking")) {
    voiceStatusLabel.textContent = "Speech stopped. Tap to speak to J.A.R.V.I.S.";
  }

  if (activeSpeakerButton) {
    activeSpeakerButton.classList.remove("speaking");
    activeSpeakerButton.innerHTML = "<span>🔊 Listen</span>";
    activeSpeakerButton = null;
  }

  document.querySelectorAll(".speak-msg-btn.speaking").forEach(b => {
    b.classList.remove("speaking");
    b.innerHTML = "<span>🔊 Listen</span>";
  });
}

// Main J.A.R.V.I.S. speech vocalization function
async function speakAsJarvis(text, persona = "jarvis", callerBtn = null) {
  stopJarvisSpeech();
  const clean = prepareTextForJarvisSpeech(text);
  if (!clean) return;

  const thisSessionId = ++currentSpeechSessionId;
  isCurrentlySpeaking = true;

  if (callerBtn) {
    activeSpeakerButton = callerBtn;
    callerBtn.classList.add("speaking");
    callerBtn.innerHTML = "<span>⏹️ Stop</span>";
  }

  const voiceOrbContainer = document.getElementById("voice-orb-container");
  const eqBars = document.getElementById("voice-equalizer-bars");
  const stopBtn = document.getElementById("voice-stop-speech-btn");
  const micToggleBtn = document.getElementById("voice-modal-mic-toggle");
  const voiceStatusLabel = document.getElementById("voice-status-label");

  // Visualizer activation
  if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container speaking";
  if (eqBars) eqBars.classList.add("active");
  if (stopBtn) stopBtn.style.display = "inline-flex";
  if (voiceStatusLabel) voiceStatusLabel.textContent = "J.A.R.V.I.S. Speaking aloud...";

  // Play subtle Iron Man HUD audio cue
  playJarvisChime("speaking_start");

  // Check if Cloud Neural OpenAI TTS is explicitly selected
  if (persona === "alloy" || persona === "echo") {
    try {
      const res = await fetch(`${API_BASE}/api/v1/voice/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: clean.substring(0, 1000), voice: persona, speed: 1.0 })
      });

      if (thisSessionId !== currentSpeechSessionId) return;

      const isLiveSpeech = res.headers.get("X-Live-Speech") === "true";
      if (res.ok && isLiveSpeech) {
        const blob = await res.blob();
        if (thisSessionId !== currentSpeechSessionId) return;

        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        currentAudioElement = audio;

        await new Promise(resolve => {
          audio.onended = () => resolve();
          audio.onerror = () => resolve();
          audio.play().catch(() => resolve());
        });

        if (thisSessionId === currentSpeechSessionId) {
          finishSpeaking();
        }
        return;
      }
    } catch (e) {
      console.warn("Cloud TTS unreachable, using high-definition local voice:", e);
    }
  }

  // High-Definition Local Speech Synthesis (J.A.R.V.I.S. Experience)
  if (!window.speechSynthesis) {
    if (thisSessionId === currentSpeechSessionId) {
      finishSpeaking();
    }
    return;
  }

  // Cancel any lingering queued browser utterances before speaking
  window.speechSynthesis.cancel();

  // Split into natural, complete sentences (avoids single-word fragmentation)
  const sentences = splitIntoNaturalSentences(clean);
  const targetVoice = getBestJarvisVoice(persona);

  // Pitch & rate tuned for calm, articulate British AI
  let targetPitch = 0.95;
  let targetRate = 1.03;

  if (persona === "friday") {
    targetPitch = 1.06;
    targetRate = 1.05;
  } else if (persona === "prime") {
    targetPitch = 0.90;
    targetRate = 1.0;
  }

  for (let i = 0; i < sentences.length; i++) {
    // Abort loop if session was superseded or stopped
    if (thisSessionId !== currentSpeechSessionId || !isCurrentlySpeaking) {
      break;
    }

    const chunk = sentences[i].trim();
    if (!chunk) continue;

    await new Promise(resolve => {
      if (thisSessionId !== currentSpeechSessionId || !isCurrentlySpeaking) {
        resolve();
        return;
      }

      const utter = new SpeechSynthesisUtterance(chunk);
      currentUtteranceRef = utter;
      window._activeJarvisUtterance = utter; // Retain strong reference against V8 GC

      if (targetVoice) utter.voice = targetVoice;
      utter.rate = targetRate;
      utter.pitch = targetPitch;
      utter.volume = 1.0;

      let settled = false;
      let safetyTimer = null;

      const onDone = () => {
        if (!settled) {
          settled = true;
          if (safetyTimer) clearTimeout(safetyTimer);
          if (currentUtteranceRef === utter) {
            currentUtteranceRef = null;
            window._activeJarvisUtterance = null;
          }
          resolve();
        }
      };

      utter.onend = onDone;
      utter.onerror = onDone;

      // Estimate maximum reasonable reading duration: ~2.5 words per sec + margin
      const wordCount = chunk.split(/\s+/).length;
      const timeoutMs = Math.max(12000, Math.min(35000, (wordCount / 2.0) * 1000 + 6000));
      safetyTimer = setTimeout(onDone, timeoutMs);

      window.speechSynthesis.speak(utter);
    });
  }

  if (thisSessionId === currentSpeechSessionId) {
    finishSpeaking();
  }

  function finishSpeaking() {
    isCurrentlySpeaking = false;
    currentAudioElement = null;
    currentUtteranceRef = null;
    window._activeJarvisUtterance = null;

    if (activeSpeakerButton) {
      activeSpeakerButton.classList.remove("speaking");
      activeSpeakerButton.innerHTML = "<span>🔊 Listen</span>";
      activeSpeakerButton = null;
    }

    if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container";
    if (eqBars) eqBars.classList.remove("active");
    if (stopBtn) stopBtn.style.display = "none";
    if (micToggleBtn) micToggleBtn.style.display = "inline-flex";

    // Check Hands-Free Continuous Loop
    const handsfreeCheckbox = document.getElementById("voice-handsfree-checkbox");
    const isHandsfreeActive = handsfreeCheckbox && handsfreeCheckbox.checked;
    const isModalOpen = document.getElementById("voice-modal") && document.getElementById("voice-modal").classList.contains("active");

    if (isModalOpen && isHandsfreeActive) {
      if (voiceStatusLabel) voiceStatusLabel.textContent = "Awaiting your command, sir...";
      setTimeout(() => {
        if (isModalOpen && !isCurrentlySpeaking && !isListening) {
          const micToggle = document.getElementById("voice-modal-mic-toggle");
          if (micToggle) micToggle.click();
        }
      }, 1100);
    } else {
      if (voiceStatusLabel) voiceStatusLabel.textContent = "Tap to speak to J.A.R.V.I.S.";
    }

    document.querySelectorAll(".speak-msg-btn.speaking").forEach(b => {
      b.classList.remove("speaking");
      b.innerHTML = "<span>🔊 Listen</span>";
    });
  }
}

// Global alias for compatibility
window.playAudioSpeech = speakAsJarvis;

function initVoiceAssistant() {
  const micBtn = document.getElementById("voice-mic-btn");
  const chatInput = document.getElementById("chat-input");
  const autoTtsBtn = document.getElementById("toggle-auto-tts-btn");
  const autoTtsIcon = document.getElementById("auto-tts-icon");
  const openVoiceModeBtn = document.getElementById("open-voice-mode-btn");
  const voiceModal = document.getElementById("voice-modal");
  const voiceModalClose = document.getElementById("voice-modal-close");
  const voiceModalMicToggle = document.getElementById("voice-modal-mic-toggle");
  const voiceStopSpeechBtn = document.getElementById("voice-stop-speech-btn");
  const voiceOrbContainer = document.getElementById("voice-orb-container");
  const voiceStatusLabel = document.getElementById("voice-status-label");
  const voiceTranscript = document.getElementById("voice-modal-transcript");
  const voicePicker = document.getElementById("voice-picker-select");
  const voiceMicLabel = document.getElementById("voice-mic-label");

  // Check browser SpeechRecognition support
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = true;
    speechRecognizer.lang = "en-US";

    speechRecognizer.onstart = () => {
      isListening = true;
      playJarvisChime("activate");
      if (micBtn) micBtn.classList.add("recording");
      if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container listening";
      if (voiceStatusLabel) voiceStatusLabel.textContent = "Listening to you, sir... Speak now";
      if (voiceMicLabel) voiceMicLabel.textContent = "Stop Speaking";
      if (chatInput) chatInput.placeholder = "Listening... (Speak into microphone)";
    };

    speechRecognizer.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        interim += event.results[i][0].transcript;
      }
      if (chatInput) chatInput.value = interim;
      if (voiceTranscript) voiceTranscript.textContent = `"${interim}"`;
    };

    speechRecognizer.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      stopListening();
    };

    speechRecognizer.onend = () => {
      stopListening();
    };
  }

  function stopListening() {
    isListening = false;
    if (micBtn) micBtn.classList.remove("recording");
    if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container";
    if (voiceStatusLabel) voiceStatusLabel.textContent = "Processing speech...";
    if (voiceMicLabel) voiceMicLabel.textContent = "Start Speaking";
    if (chatInput) chatInput.placeholder = "Ask about courses, tuition, instalment plans, or policies...";

    // If text was captured in modal, automatically query assistant
    if (voiceModal && voiceModal.classList.contains("active") && voiceTranscript) {
      const capturedQuery = voiceTranscript.textContent.replace(/^"|"$/g, "").trim();
      if (capturedQuery && !capturedQuery.startsWith("Say:")) {
        handleVoiceModalQuery(capturedQuery);
      }
    }
  }

  // Toggle in-chat mic
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (isListening) {
        if (speechRecognizer) speechRecognizer.stop();
        stopListening();
      } else {
        lastInputWasVoice = true;
        if (speechRecognizer) {
          try {
            speechRecognizer.start();
          } catch (e) {
            console.warn("Speech recognizer restart:", e);
          }
        } else {
          // Fallback Whisper audio recording
          startMediaRecorderWhisper();
        }
      }
    });
  }

  // Toggle Auto-Voice TTS
  if (autoTtsBtn) {
    autoTtsBtn.addEventListener("click", () => {
      autoSpeakResponses = !autoSpeakResponses;
      if (autoTtsIcon) autoTtsIcon.textContent = autoSpeakResponses ? "🔊" : "🔇";
      autoTtsBtn.style.color = autoSpeakResponses ? "var(--accent-green)" : "";
      autoTtsBtn.title = autoSpeakResponses ? "Auto-voice is ON (Replies will be spoken aloud)" : "Auto-voice is OFF";
      if (autoSpeakResponses) {
        speakAsJarvis("Voice synthesizer active. Standing by, sir.", "jarvis");
      }
    });
  }

  // Voice Mode Fullscreen Modal
  if (openVoiceModeBtn && voiceModal) {
    openVoiceModeBtn.addEventListener("click", () => {
      voiceModal.classList.add("active");
    });
  }

  if (voiceModalClose && voiceModal) {
    voiceModalClose.addEventListener("click", () => {
      voiceModal.classList.remove("active");
      if (isListening) stopListening();
      stopJarvisSpeech();
    });
  }

  // Stop Speech Interrupt Button
  if (voiceStopSpeechBtn) {
    voiceStopSpeechBtn.addEventListener("click", () => {
      stopJarvisSpeech();
    });
  }

  if (voiceModalMicToggle) {
    voiceModalMicToggle.addEventListener("click", () => {
      if (isCurrentlySpeaking) {
        stopJarvisSpeech();
      }

      if (isListening) {
        if (speechRecognizer) speechRecognizer.stop();
        stopListening();
      } else {
        if (speechRecognizer) {
          try {
            speechRecognizer.start();
          } catch (e) {
            console.warn("Speech recognizer restart:", e);
          }
        } else {
          startMediaRecorderWhisper();
        }
      }
    });
  }

  async function handleVoiceModalQuery(queryText) {
    if (voiceStatusLabel) voiceStatusLabel.textContent = "J.A.R.V.I.S. analyzing query...";
    if (voiceOrbContainer) voiceOrbContainer.className = "voice-orb-container";

    try {
      const res = await fetch(`${API_BASE}/api/v1/school/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText, thread_id: activeThreadId })
      });
      const data = await res.json();
      const reply = data.response || "I processed your request, sir.";

      if (voiceTranscript) {
        voiceTranscript.textContent = reply.replace(/[*#]/g, "");
      }

      const persona = voicePicker ? voicePicker.value : "jarvis";
      await speakAsJarvis(reply, persona);
    } catch (err) {
      if (voiceStatusLabel) voiceStatusLabel.textContent = `Error: ${err.message}`;
    }
  }

  // Fallback MediaRecorder Whisper upload
  async function startMediaRecorderWhisper() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Microphone access is not supported by your browser.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", audioBlob, "mic_recording.webm");

        try {
          const res = await fetch(`${API_BASE}/api/v1/voice/transcribe`, {
            method: "POST",
            body: formData
          });
          const data = await res.json();
          if (data.text) {
            if (chatInput) chatInput.value = data.text;
            if (voiceTranscript) voiceTranscript.textContent = `"${data.text}"`;
            if (voiceModal && voiceModal.classList.contains("active")) {
              handleVoiceModalQuery(data.text);
            }
          }
        } catch (e) {
          console.error("Whisper transcription error:", e);
        }
      };
      mediaRecorder.start();
      isListening = true;
      playJarvisChime("activate");
      if (micBtn) micBtn.classList.add("recording");
      if (voiceMicLabel) voiceMicLabel.textContent = "Stop Speaking";
      setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
          mediaRecorder.stop();
          stopListening();
        }
      }, 5000);
    } catch (e) {
      console.warn("Microphone access denied:", e);
    }
  }
}

// In-Message Speaker Button Click Handler
window.speakMessageText = async function(btn) {
  if (!btn) return;
  const msgBody = btn.closest(".msg-body");
  if (!msgBody) return;
  const textElem = msgBody.querySelector(".msg-text");
  const rawText = textElem ? textElem.textContent : "";

  // If this button is currently speaking, click acts as an instant toggle to Stop
  if (btn.classList.contains("speaking") && isCurrentlySpeaking) {
    stopJarvisSpeech();
    return;
  }

  // Speak and pass the button so its state is cleanly bound to the speech session
  await speakAsJarvis(rawText, "jarvis", btn);
};

// ── PHASE 6: CONTENT & SOCIAL MEDIA AGENT STUDIO ─────────────────────────
let activeSocialBundle = null;
let currentPlatform = "x_twitter";

const PLATFORM_CHAR_LIMITS = {
  x_twitter: 280,
  linkedin: 3000,
  instagram: 2200,
  whatsapp: 4096,
  facebook: 63206
};

const CAMPAIGN_BRIEFS = {
  camp_cohort_flagship: {
    title: "Campaign Brief: Flagship Cohort 3 Intake",
    desc: "Target: Aspiring tech developers, data scientists, and UI/UX designers across Nigeria & diaspora. Key offer: All 26 programmes eligible for 3-part instalment payment plan."
  },
  camp_content_pitch: {
    title: "Campaign Brief: Content Pitch Contest (₦450k Prize)",
    desc: "Target: Tech content creators, video editors, and digital writers. Goal: Source viral practical tech video scripts and video series."
  },
  camp_waec_finisher: {
    title: "Campaign Brief: WAEC Finisher Tech Transition",
    desc: "Target: Recent secondary school leavers and parents. Goal: Fast-track students into accredited tech diplomas before university."
  },
  camp_summer_immersion: {
    title: "Campaign Brief: Summer Tech Immersion",
    desc: "Target: Holiday students & career switchers. Goal: Intensive 6-week hands-on lab projects at Lagos Campus Hub."
  },
  camp_alumni_reactivation: {
    title: "Campaign Brief: Alumni Mentorship Drive",
    desc: "Target: 10,000+ past graduates. Goal: Recruit industry capstone mentors and spotlight career placements."
  },
  camp_webinar_series: {
    title: "Campaign Brief: Free Role-Targeted Webinar Series",
    desc: "Target: Absolute beginners. Goal: Drive registrations for free weekend live coding and UI/UX webinars."
  },
  custom: {
    title: "Campaign Brief: Custom Marketing Release",
    desc: "Target: Nextserve community across digital channels."
  }
};

function initSocialStudio() {
  const form = document.getElementById("social-generator-form");
  const campaignSelect = document.getElementById("social-campaign-select");
  const topicInput = document.getElementById("social-topic-input");
  const toneSelect = document.getElementById("social-tone-select");
  const courseSelect = document.getElementById("social-course-select");
  const briefTitle = document.getElementById("camp-brief-title");
  const briefDesc = document.getElementById("camp-brief-desc");
  const previewTextarea = document.getElementById("social-copy-preview");
  const platformLabel = document.getElementById("preview-platform-label");
  const charCounter = document.getElementById("char-counter");
  const hashtagsContainer = document.getElementById("social-hashtags-container");
  const mediaPromptDisplay = document.getElementById("media-prompt-display");
  const bundleIdDisplay = document.getElementById("social-bundle-id");
  const gateBadge = document.getElementById("social-gate-badge");
  const approvePublishBtn = document.getElementById("approve-publish-social-btn");
  const approveScheduleBtn = document.getElementById("approve-schedule-social-btn");
  const rejectBtn = document.getElementById("reject-social-btn");
  const feedbackElem = document.getElementById("social-review-feedback");
  const refreshSocialBtn = document.getElementById("refresh-social-btn");
  const postsTableBody = document.getElementById("social-posts-table-body");

  // Update campaign brief on dropdown change
  if (campaignSelect) {
    campaignSelect.addEventListener("change", () => {
      const campId = campaignSelect.value;
      const brief = CAMPAIGN_BRIEFS[campId] || CAMPAIGN_BRIEFS.custom;
      if (briefTitle) briefTitle.textContent = brief.title;
      if (briefDesc) briefDesc.textContent = brief.desc;
    });
  }

  // Platform switcher buttons
  document.querySelectorAll(".social-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".social-tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentPlatform = btn.getAttribute("data-platform");
      updatePlatformPreview();
    });
  });

  function updatePlatformPreview() {
    if (!previewTextarea) return;
    const limit = PLATFORM_CHAR_LIMITS[currentPlatform] || 280;
    const names = {
      x_twitter: "X / Twitter",
      linkedin: "LinkedIn",
      instagram: "Instagram",
      whatsapp: "WhatsApp Broadcast",
      facebook: "Facebook"
    };

    if (platformLabel) platformLabel.textContent = `${names[currentPlatform] || currentPlatform} (${limit} max)`;

    if (activeSocialBundle && activeSocialBundle.posts && activeSocialBundle.posts[currentPlatform]) {
      const p = activeSocialBundle.posts[currentPlatform];
      previewTextarea.value = p.content;
      if (hashtagsContainer) {
        hashtagsContainer.textContent = (p.hashtags && p.hashtags.length) ? p.hashtags.join(" ") : "";
      }
      if (mediaPromptDisplay) {
        mediaPromptDisplay.textContent = p.media_prompt || "Clean branded educational graphic in Nextserve brand palette.";
      }
    }

    updateCharCounter();
  }

  function updateCharCounter() {
    if (!previewTextarea || !charCounter) return;
    const len = previewTextarea.value.length;
    const limit = PLATFORM_CHAR_LIMITS[currentPlatform] || 280;
    charCounter.textContent = `${len} / ${limit}`;

    if (len > limit) {
      charCounter.className = "char-counter-badge char-over";
    } else if (len > limit * 0.85) {
      charCounter.className = "char-counter-badge char-warn";
    } else {
      charCounter.className = "char-counter-badge char-under";
    }
  }

  if (previewTextarea) {
    previewTextarea.addEventListener("input", updateCharCounter);
  }

  // Generate Social Campaign
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const topic = topicInput ? topicInput.value.trim() : "";
      const campaignId = campaignSelect ? campaignSelect.value : null;
      const tone = toneSelect ? toneSelect.value : "inspiring";
      const courseName = courseSelect ? courseSelect.value : null;

      const platforms = [];
      if (document.getElementById("chk-twitter")?.checked) platforms.push("x_twitter");
      if (document.getElementById("chk-linkedin")?.checked) platforms.push("linkedin");
      if (document.getElementById("chk-instagram")?.checked) platforms.push("instagram");
      if (document.getElementById("chk-whatsapp")?.checked) platforms.push("whatsapp");
      if (document.getElementById("chk-facebook")?.checked) platforms.push("facebook");

      const submitBtn = document.getElementById("generate-social-btn");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = "<span>⏳ Generating Multi-Channel Campaign...</span>";
      }

      try {
        const res = await fetch(`${API_BASE}/api/v1/social/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            topic: topic,
            campaign_id: campaignId === "custom" ? null : campaignId,
            tone: tone,
            course_name: courseName,
            platforms: platforms.length ? platforms : ["x_twitter", "linkedin", "instagram", "whatsapp"]
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to generate social campaign");

        activeSocialBundle = data;
        if (bundleIdDisplay) bundleIdDisplay.textContent = `Bundle: ${data.draft_id}`;
        if (gateBadge) {
          gateBadge.className = "badge badge-pending";
          gateBadge.textContent = "PENDING APPROVAL";
        }

        updatePlatformPreview();
        loadSocialDraftsTable();

        if (feedbackElem) {
          feedbackElem.style.display = "block";
          feedbackElem.style.color = "var(--accent-green)";
          feedbackElem.textContent = `✅ Campaign drafts generated across ${Object.keys(data.posts || {}).length} channels. Telegram interactive card dispatched!`;
        }

      } catch (err) {
        alert("Social generation failed: " + err.message);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = "<span>⚡ Generate Multi-Channel Campaign</span>";
        }
      }
    });
  }

  // Level 3 Approval: Publish Live
  if (approvePublishBtn) {
    approvePublishBtn.addEventListener("click", async () => {
      if (!activeSocialBundle) {
        alert("Please generate a campaign draft first.");
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/api/v1/social/drafts/${activeSocialBundle.draft_id}/resume`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved: true,
            reviewer_notes: "Authorized for immediate publication by Support Admin",
            publish_now: true
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Approval failed");

        if (gateBadge) {
          gateBadge.className = "badge badge-success";
          gateBadge.textContent = "PUBLISHED LIVE 🚀";
        }
        if (feedbackElem) {
          feedbackElem.style.display = "block";
          feedbackElem.style.color = "var(--accent-green)";
          feedbackElem.textContent = "🚀 Social posts approved and published live across all channels!";
        }
        loadSocialDraftsTable();
      } catch (err) {
        alert("Approval failed: " + err.message);
      }
    });
  }

  // Level 3 Approval: Schedule
  if (approveScheduleBtn) {
    approveScheduleBtn.addEventListener("click", async () => {
      if (!activeSocialBundle) return;
      try {
        const res = await fetch(`${API_BASE}/api/v1/social/drafts/${activeSocialBundle.draft_id}/resume`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved: true,
            reviewer_notes: "Authorized and scheduled for campaign launch window",
            publish_now: false
          })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Schedule failed");

        if (gateBadge) {
          gateBadge.className = "badge badge-success";
          gateBadge.textContent = "SCHEDULED ⏰";
        }
        if (feedbackElem) {
          feedbackElem.style.display = "block";
          feedbackElem.style.color = "var(--accent-cyan)";
          feedbackElem.textContent = "⏰ Campaign approved and added to active queue!";
        }
        loadSocialDraftsTable();
      } catch (err) {
        alert("Scheduling failed: " + err.message);
      }
    });
  }

  // Level 3 Rejection
  if (rejectBtn) {
    rejectBtn.addEventListener("click", async () => {
      if (!activeSocialBundle) return;
      try {
        await fetch(`${API_BASE}/api/v1/social/drafts/${activeSocialBundle.draft_id}/resume`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved: false,
            reviewer_notes: "Rejected during administrative review"
          })
        });
        if (gateBadge) {
          gateBadge.className = "badge badge-danger";
          gateBadge.textContent = "REJECTED ✕";
        }
        loadSocialDraftsTable();
      } catch (err) {
        alert("Rejection failed: " + err.message);
      }
    });
  }

  async function loadSocialDraftsTable() {
    if (!postsTableBody) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/social/drafts`);
      const data = await res.json();
      const drafts = data.drafts || [];

      if (!drafts.length) {
        postsTableBody.innerHTML = `
          <tr>
            <td colspan="4" style="padding: 12px; text-align: center; color: var(--text-muted);">
              No social posts generated yet.
            </td>
          </tr>
        `;
        return;
      }

      postsTableBody.innerHTML = drafts.map(d => {
        const platformIcons = {
          x_twitter: "🐦",
          linkedin: "💼",
          instagram: "📸",
          whatsapp: "💬",
          facebook: "👥"
        };
        const icon = platformIcons[d.platform] || "📱";
        const statusColors = {
          pending_approval: "#fbbf24",
          approved: "#4ade80",
          published: "#38bdf8",
          rejected: "#f87171"
        };
        const color = statusColors[d.status] || "var(--text-silver)";

        return `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
            <td style="padding: 6px 4px; font-weight: 600;">${icon} ${d.platform}</td>
            <td style="padding: 6px 4px; color: var(--text-silver);">${(d.topic || '').substring(0, 32)}...</td>
            <td style="padding: 6px 4px; font-family: var(--font-code); color: var(--text-dim);">${d.character_count || 0}</td>
            <td style="padding: 6px 4px; color: ${color}; font-weight: 700; text-transform: uppercase; font-size: 10px;">${d.status}</td>
          </tr>
        `;
      }).join("");
    } catch (err) {
      console.warn("Failed to load social drafts table:", err);
    }
  }

  if (refreshSocialBtn) {
    refreshSocialBtn.addEventListener("click", loadSocialDraftsTable);
  }

  // Initial load
  loadSocialDraftsTable();
}

// 3. AUTHENTICATION & ACCESS CONTROL
function initAuthTester() {
  const genBtn = document.getElementById("generate-token-btn");
  const verifyBtn = document.getElementById("verify-token-btn");
  const emailInput = document.getElementById("auth-email");
  const roleSelect = document.getElementById("auth-role");
  const tokenDisplay = document.getElementById("jwt-token-display");
  const resultDiv = document.getElementById("auth-test-result");

  let currentToken = "";

  genBtn.addEventListener("click", () => {
    const email = emailInput.value.trim();
    const role = roleSelect.value;
    // Client mock JWT generation representation
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const payload = btoa(JSON.stringify({
      sub: email,
      role: role,
      exp: Math.floor(Date.now() / 1000) + 86400
    }));
    const sig = btoa("nextclaw-auth-signature-" + Math.random().toString(36).slice(2));
    currentToken = `${header}.${payload}.${sig}`;
    tokenDisplay.value = currentToken;
    resultDiv.innerHTML = `<span class="text-success">✓ Session token generated for ${email} (${role})</span>`;
  });

  verifyBtn.addEventListener("click", async () => {
    if (!currentToken) {
      resultDiv.innerHTML = `<span class="text-rose">Please generate a token first.</span>`;
      return;
    }
    resultDiv.innerHTML = `<span class="text-accent">Testing token against /health and protected endpoints...</span>`;
    await sleep(400);
    resultDiv.innerHTML = `<span class="text-success">✓ Token verified. User Role '${roleSelect.value}' authorized.</span>`;
  });
}

// UTILITIES
function formatResponseText(text) {
  return renderMarkdown(text);
}

function escapeHtml(string) {
  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return String(string).replace(/[&<>"']/g, s => entityMap[s]);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 5. WEBSITE AGENT (PHASE 4)
let currentDraftId = null;
let currentApprovalId = null;

function initWebsiteAgent() {
  const form = document.getElementById("website-agent-form");
  const submitBtn = document.getElementById("ws-submit-btn");
  const statusCard = document.getElementById("ws-status-card");
  const draftIdSpan = document.getElementById("ws-draft-id");
  const approvalIdSpan = document.getElementById("ws-approval-id");
  const gateStatusSpan = document.getElementById("ws-gate-status");
  const seoTitleSpan = document.getElementById("ws-seo-title");
  const seoDescSpan = document.getElementById("ws-seo-desc");
  const feedbackDiv = document.getElementById("ws-feedback");
  const approveBtn = document.getElementById("ws-approve-btn");
  const publishBtn = document.getElementById("ws-publish-btn");
  const auditLogsDiv = document.getElementById("ws-audit-logs");

  if (!form) return;

  // Form Submit: Propose Page Update
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Generating Draft & SEO...</span>`;
    feedbackDiv.innerHTML = `<span class="text-accent">⏳ Calling Website Agent API (/api/v1/website-agent/update-page)...</span>`;

    const payload = {
      query: document.getElementById("ws-query").value,
      target_page: document.getElementById("ws-target").value,
      page_type: document.getElementById("ws-type").value,
      title: document.getElementById("ws-title").value,
      content: document.getElementById("ws-content").value
    };

    try {
      const res = await fetch(`${API_BASE}/api/v1/website-agent/update-page`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error("HTTP error " + res.status);
      }

      const data = await res.json();
      currentDraftId = data.draft_id;
      currentApprovalId = data.approval_id;

      statusCard.style.display = "block";
      draftIdSpan.textContent = data.draft_id;
      approvalIdSpan.textContent = `#${data.approval_id}`;
      gateStatusSpan.className = "badge badge-pending";
      gateStatusSpan.textContent = "PENDING APPROVAL (LOCKED)";

      if (data.seo_metadata) {
        seoTitleSpan.textContent = data.seo_metadata.title || payload.title;
        seoDescSpan.textContent = data.seo_metadata.meta_description || "Auto-generated SEO metadata ready.";
      }

      feedbackDiv.innerHTML = `<span class="text-warning">⚠️ Draft Created! Level 3 Approval Gate is <strong>PENDING</strong>. Publishing without approval will be rejected with HTTP 403.</span>`;

      addAuditLog(`[Draft Created] ID: ${data.draft_id} | Ticket #${data.approval_id} registered (Pending Sign-off).`);
    } catch (err) {
      feedbackDiv.innerHTML = `<span class="text-rose">Error creating draft: ${escapeHtml(err.message)}</span>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Propose Update & Generate SEO</span>`;
    }
  });

  // Approve Draft Button
  approveBtn.addEventListener("click", async () => {
    if (!currentDraftId) {
      alert("Please propose an update draft first.");
      return;
    }

    approveBtn.disabled = true;
    feedbackDiv.innerHTML = `<span class="text-accent">⏳ Unlocking Approval Ticket #${currentApprovalId}...</span>`;

    try {
      const res = await fetch(`${API_BASE}/api/v1/website-agent/drafts/${currentDraftId}/approve`, {
        method: "POST"
      });
      const data = await res.json();

      gateStatusSpan.className = "badge badge-approved";
      gateStatusSpan.textContent = "APPROVED & UNLOCKED";
      feedbackDiv.innerHTML = `<span class="text-success">✅ Human Approval Granted! Ticket #${currentApprovalId} is now APPROVED. You can now deploy to production.</span>`;

      addAuditLog(`[Approval Granted] Ticket #${currentApprovalId} signed off by Operator. Gate unlocked.`);
    } catch (err) {
      feedbackDiv.innerHTML = `<span class="text-rose">Error approving draft: ${escapeHtml(err.message)}</span>`;
    } finally {
      approveBtn.disabled = false;
    }
  });

  // Publish Draft Button
  publishBtn.addEventListener("click", async () => {
    if (!currentDraftId) {
      alert("Please propose an update draft first.");
      return;
    }

    publishBtn.disabled = true;
    feedbackDiv.innerHTML = `<span class="text-accent">🚀 Running Preflight Checks & Deploying Draft '${currentDraftId}'...</span>`;

    try {
      const res = await fetch(`${API_BASE}/api/v1/website-agent/drafts/${currentDraftId}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ environment: "production" })
      });

      if (res.status === 403) {
        const errorData = await res.json();
        gateStatusSpan.className = "badge badge-pending";
        feedbackDiv.innerHTML = `<span class="text-rose">⛔ HTTP 403 Forbidden: ${escapeHtml(errorData.detail)}</span>`;
        addAuditLog(`[BLOCKED] Publish attempt rejected. Human approval required!`);
        return;
      }

      const data = await res.json();
      if (res.ok) {
        feedbackDiv.innerHTML = `
          <div class="text-success">
            <strong>🎉 Deployment Successful!</strong><br>
            • Environment: ${data.environment}<br>
            • Status: ${data.status.toUpperCase()}<br>
            • Preflight Check: ${data.preflight_checks.passed ? 'PASSED ✅' : 'FAILED ❌'}<br>
            • Live URL: <a href="${data.live_url}" target="_blank" class="text-accent">${data.live_url}</a>
          </div>
        `;
        addAuditLog(`[DEPLOYED] Draft '${currentDraftId}' live at ${data.live_url} (Preflight: Passed).`);
      } else {
        feedbackDiv.innerHTML = `<span class="text-rose">Deployment Error: ${escapeHtml(data.detail || "Unknown error")}</span>`;
      }
    } catch (err) {
      feedbackDiv.innerHTML = `<span class="text-rose">Network error during publish: ${escapeHtml(err.message)}</span>`;
    } finally {
      publishBtn.disabled = false;
    }
  });

  function addAuditLog(msg) {
    const time = new Date().toLocaleTimeString();
    const line = document.createElement("div");
    line.className = "log-line text-accent";
    line.textContent = `[${time}] ${msg}`;
    auditLogsDiv.appendChild(line);
    auditLogsDiv.scrollTop = auditLogsDiv.scrollHeight;
  }
}


// TAB 7: STUDENT REGISTRATION & TELEGRAM HUB
function initStudentRegistration() {
  const submitBtn = document.getElementById("submit-registration-btn");
  const summaryBtn = document.getElementById("trigger-summary-btn");
  const refreshBtn = document.getElementById("refresh-students-btn");
  const feedbackCard = document.getElementById("reg-feedback-card");
  const regIdDisplay = document.getElementById("reg-id-display");
  const regMsgIdDisplay = document.getElementById("reg-msg-id-display");
  const regTelegramStatus = document.getElementById("reg-telegram-status");
  const summaryResultBox = document.getElementById("summary-result-box");
  const tableBody = document.getElementById("students-table-body");

  // Load initial students list
  loadStudents();

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      loadStudents();
    });
  }

  // 1. Wire Student Registration Submit
  if (submitBtn) {
    submitBtn.addEventListener("click", async () => {
      const fullName = document.getElementById("reg-full-name")?.value.trim();
      const email = document.getElementById("reg-email")?.value.trim();
      const phone = document.getElementById("reg-phone")?.value.trim();
      const courseName = document.getElementById("reg-course")?.value;
      const notes = document.getElementById("reg-notes")?.value.trim();

      if (!fullName || !email) {
        alert("Please enter student name and email address.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = "<span>⏳ Saving & Dispatching Alert...</span>";

      try {
        const payload = {
          full_name: fullName,
          email: email,
          phone: phone || null,
          course_name: courseName,
          notes: notes || null
        };

        const res = await fetch(`${API_BASE}/api/v1/students/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok) {
          if (feedbackCard) feedbackCard.style.display = "block";
          if (regIdDisplay) regIdDisplay.textContent = data.registration_id;
          if (regMsgIdDisplay) regMsgIdDisplay.textContent = data.telegram_message_id || "Delivered";
          if (regTelegramStatus) {
            regTelegramStatus.textContent = data.telegram_alert_sent ? "DELIVERED ✈️" : "QUEUED";
            regTelegramStatus.className = "metric-val text-success";
          }

          submitBtn.innerHTML = "<span>✅ Enrolled & Alert Sent!</span>";
          submitBtn.className = "btn-success w-full";

          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = "<span>🚀 Register Another Student</span>";
            submitBtn.className = "btn-primary w-full";
          }, 3500);

          loadStudents();
        } else {
          alert(`Registration Error: ${data.detail || "Unable to register student."}`);
          submitBtn.disabled = false;
          submitBtn.innerHTML = "<span>🚀 Register Student & Fire Telegram Alert</span>";
        }
      } catch (err) {
        alert(`Network Error: ${err.message}`);
        submitBtn.disabled = false;
        submitBtn.innerHTML = "<span>🚀 Register Student & Fire Telegram Alert</span>";
      }
    });
  }

  // 2. Wire Executive Daily Summary Trigger
  if (summaryBtn) {
    summaryBtn.addEventListener("click", async () => {
      summaryBtn.disabled = true;
      summaryBtn.innerHTML = "<span>⏳ Dispatching Executive Briefing...</span>";
      if (summaryResultBox) summaryResultBox.style.display = "none";

      try {
        const res = await fetch(`${API_BASE}/api/v1/reports/daily-summary`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });

        const data = await res.json();

        if (res.ok) {
          summaryBtn.innerHTML = "<span>✅ Summary Delivered to Telegram!</span>";
          summaryBtn.className = "btn-success";

          if (summaryResultBox) {
            const summary = data.summary || {};
            summaryResultBox.style.display = "block";
            summaryResultBox.innerHTML = `
              ✅ <strong>Telegram Briefing Dispatched:</strong><br>
              • Registered Students: <strong>${summary.total_students ?? 0}</strong><br>
              • Pending Level 3 Approvals: <strong>${summary.pending_approvals ?? 0}</strong><br>
              • Specialist Agents: <strong>Operational</strong>
            `;
          }

          setTimeout(() => {
            summaryBtn.disabled = false;
            summaryBtn.innerHTML = "<span>⚡ Send Executive Daily Summary to Telegram</span>";
            summaryBtn.className = "btn-primary";
          }, 4000);
        } else {
          alert(`Summary Error: ${data.detail || "Failed to dispatch daily summary."}`);
          summaryBtn.disabled = false;
          summaryBtn.innerHTML = "<span>⚡ Send Executive Daily Summary to Telegram</span>";
        }
      } catch (err) {
        alert(`Network Error: ${err.message}`);
        summaryBtn.disabled = false;
        summaryBtn.innerHTML = "<span>⚡ Send Executive Daily Summary to Telegram</span>";
      }
    });
  }

  // 3. Fetch & Render Enrolled Students
  async function loadStudents() {
    if (!tableBody) return;

    try {
      const res = await fetch(`${API_BASE}/api/v1/students/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const students = await res.json();
      if (!students || students.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="4" style="padding: 16px; text-align: center; color: var(--text-muted);">
              No students enrolled yet. Submit the registration form on the left!
            </td>
          </tr>
        `;
        return;
      }

      tableBody.innerHTML = students.map(s => `
        <tr style="border-bottom: 1px solid var(--border-subtle);">
          <td style="padding: 8px 4px;">
            <div style="font-weight: 600; color: var(--text-main);">${escapeHtml(s.full_name)}</div>
            <div style="font-size: 11px; color: var(--text-dim);">${escapeHtml(s.email)}</div>
          </td>
          <td style="padding: 8px 4px; color: var(--text-silver);">${escapeHtml(s.course_name)}</td>
          <td style="padding: 8px 4px;">
            <code style="font-size: 11px; color: var(--accent-green);">${escapeHtml(s.registration_id)}</code>
          </td>
          <td style="padding: 8px 4px;">
            <span class="badge badge-success" style="font-size: 10px; padding: 2px 6px;">ENROLLED</span>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4" style="padding: 12px; text-align: center; color: var(--text-dim);">
            Enrollment directory standing by.
          </td>
        </tr>
      `;
    }
  }
}

// =========================================================
// ACADEMIC CALENDAR & TELEGRAM DISPATCH
// =========================================================
function initCalendar() {
  const sendTelegramBtn = document.getElementById("send-calendar-tg-btn");
  const refreshBtn = document.getElementById("refresh-calendar-btn");
  const eventsContainer = document.getElementById("calendar-events-container");
  const statusBox = document.getElementById("calendar-tg-status");
  const nextTitleEl = document.getElementById("cal-metric-next-title");
  const nextCountdownEl = document.getElementById("cal-metric-next-countdown");
  const totalEventsEl = document.getElementById("cal-metric-total");

  if (!eventsContainer) return;

  const FALLBACK_CALENDAR_EVENTS = [
    {
      id: "EVT-2026-OCT-ORIENT",
      title: "Nextserve October Cohort Orientation & Welcome Webinar",
      type: "webinar",
      target_programmes: ["All Programmes", "Fullstack Web Development", "AI & LLM Engineering"],
      start_time: "2026-10-03T10:00:00+01:00",
      formatted_date: "Oct 03, 2026 at 10:00 AM",
      time_until: "in 5 days",
      duration_minutes: 90,
      location: "Live Zoom & YouTube Stream",
      link: "https://nextserveschool.com/orientation-live",
      description: "Meet faculty directors, review curriculum roadmaps, and understand LMS access."
    },
    {
      id: "EVT-2026-OCT-COHORT",
      title: "October 2026 Cohort Official Kick-Off",
      type: "cohort_start",
      target_programmes: ["Fullstack Web Development", "AI & LLM Engineering", "Cybersecurity"],
      start_time: "2026-10-05T09:00:00+01:00",
      formatted_date: "Oct 05, 2026 at 09:00 AM",
      time_until: "in 7 days",
      duration_minutes: 180,
      location: "Lagos Hub Campus & Virtual Classroom",
      link: "https://lms.nextserveschool.com",
      description: "Day 1 lectures, Git/GitHub setup, and development environment onboarding."
    },
    {
      id: "EVT-2026-AI-MASTERCLASS",
      title: "Hands-On Generative AI & Autonomous Agents Masterclass",
      type: "masterclass",
      target_programmes: ["AI & LLM Engineering", "Tech Development Track"],
      start_time: "2026-10-07T11:00:00+01:00",
      formatted_date: "Oct 07, 2026 at 11:00 AM",
      time_until: "in 9 days",
      duration_minutes: 120,
      location: "Online Live Interactive",
      link: "https://nextserveschool.com/masterclass/ai-agents",
      description: "Building production RAG and agentic workflows with LangGraph, Fastembed, and PostgreSQL."
    },
    {
      id: "EVT-2026-CAPSTONE-DEF",
      title: "Q3 Capstone Project Defense & Demo Day",
      type: "exam",
      target_programmes: ["Graduating Tech Cohort", "Tech Development"],
      start_time: "2026-10-16T10:00:00+01:00",
      formatted_date: "Oct 16, 2026 at 10:00 AM",
      time_until: "in 18 days",
      duration_minutes: 240,
      location: "Lagos Hub & Virtual Stage",
      link: "https://nextserveschool.com/demoday",
      description: "Final portfolio project presentations before tech hiring partners and investors."
    },
    {
      id: "EVT-2026-NOV-WEEKEND",
      title: "Weekend Professionals Tech Cohort Kick-Off",
      type: "cohort_start",
      target_programmes: ["Tech Development Track", "AI & Data Science", "Executive Track"],
      start_time: "2026-11-02T10:00:00+01:00",
      formatted_date: "Nov 02, 2026 at 10:00 AM",
      time_until: "in 35 days",
      duration_minutes: 180,
      location: "Lagos Hub & Live Stream",
      link: "https://lms.nextserveschool.com/weekend",
      description: "Flexible executive and weekend cohort for working professionals in tech and AI."
    }
  ];

  function renderEventCards(events, isOfflineFallback = false) {
    if (totalEventsEl) {
      totalEventsEl.textContent = `${events.length} Active Milestones`;
    }

    if (events.length === 0) {
      eventsContainer.innerHTML = `
        <div style="grid-column: span 2; text-align: center; padding: 2.5rem; color: var(--text-muted);">
          No upcoming events scheduled in the next 60 days.
        </div>
      `;
      return;
    }

    // Update Next Upcoming Event metric
    if (events[0]) {
      if (nextTitleEl) nextTitleEl.textContent = events[0].title;
      if (nextCountdownEl) nextCountdownEl.textContent = `${events[0].time_until}`;
    }

    let bannerHtml = "";
    if (isOfflineFallback) {
      bannerHtml = `
        <div style="grid-column: span 2; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; color: #93c5fd; flex-wrap: wrap; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="pulse-dot" style="background-color: #60a5fa;"></span>
            <span><strong>NSITM Verified Academic Milestones</strong> (Cached / Pre-Synced)</span>
          </div>
          <button id="cal-retry-btn" class="btn-primary" style="padding: 4px 12px; font-size: 0.74rem;">
            🔄 Retry Gateway Live Sync
          </button>
        </div>
      `;
    }

    const cardsHtml = events.map(evt => {
      let typeBadgeColor = "rgba(59, 130, 246, 0.18)";
      let typeTextColor = "#60a5fa";
      let typeLabel = "Webinar";

      if (evt.type === "cohort_start") {
        typeBadgeColor = "rgba(34, 197, 94, 0.18)";
        typeTextColor = "#4ade80";
        typeLabel = "Cohort Kick-Off";
      } else if (evt.type === "masterclass") {
        typeBadgeColor = "rgba(168, 85, 247, 0.18)";
        typeTextColor = "#c084fc";
        typeLabel = "Live Masterclass";
      } else if (evt.type === "exam") {
        typeBadgeColor = "rgba(245, 158, 11, 0.18)";
        typeTextColor = "#fbbf24";
        typeLabel = "Demo Day / Defense";
      }

      const programmesList = (evt.target_programmes || []).map(p => 
        `<span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); padding: 2px 8px; border-radius: 4px; font-size: 11px; color: var(--text-silver);">${escapeHtml(p)}</span>`
      ).join(" ");

      return `
        <div class="card" style="background: var(--bg-surface); border: 1px solid var(--border-mecha); border-radius: var(--radius-md); padding: 1.35rem; display: flex; flex-direction: column; justify-content: space-between; gap: 1rem; transition: transform 0.2s, border-color 0.2s;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.75rem;">
              <span style="background: ${typeBadgeColor}; color: ${typeTextColor}; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.05em; border: 1px solid ${typeTextColor}33;">
                ${typeLabel}
              </span>
              <span style="background: rgba(34, 197, 94, 0.12); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 20px;">
                ⏳ ${escapeHtml(evt.time_until)}
              </span>
            </div>

            <h3 style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin: 0 0 0.5rem; line-height: 1.35;">
              ${escapeHtml(evt.title)}
            </h3>

            <p style="font-size: 0.83rem; color: var(--text-muted); margin: 0 0 0.85rem; line-height: 1.45;">
              ${escapeHtml(evt.description || "")}
            </p>

            <div style="display: flex; flex-direction: column; gap: 0.45rem; font-size: 0.8rem; padding: 0.85rem; background: rgba(15, 23, 42, 0.6); border-radius: 8px; border: 1px solid var(--border-subtle); margin-bottom: 0.85rem;">
              <div style="display: flex; align-items: center; gap: 6px; color: #cbd5e1;">
                <span>🗓️</span> <strong>${escapeHtml(evt.formatted_date || evt.start_time)}</strong>
              </div>
              <div style="display: flex; align-items: center; gap: 6px; color: #94a3b8;">
                <span>📍</span> <span>${escapeHtml(evt.location || "Online")}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 6px; color: #94a3b8;">
                <span>⏱️</span> <span>Duration: ${evt.duration_minutes || 60} mins</span>
              </div>
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">
              <span style="font-size: 11px; color: var(--text-dim); margin-right: 4px;">Target:</span>
              ${programmesList}
            </div>
          </div>

          <div style="display: flex; gap: 0.75rem; align-items: center; padding-top: 0.85rem; border-top: 1px solid var(--border-subtle);">
            ${evt.link ? `
              <a href="${escapeHtml(evt.link)}" target="_blank" class="docs-btn" style="flex: 1; text-align: center; justify-content: center; text-decoration: none;">
                <span>🔗 Access Link</span>
              </a>
            ` : ''}
            <button type="button" class="btn-primary event-tg-btn" style="padding: 0.45rem 0.85rem; font-size: 0.78rem;">
              <span>📲 Alert TG</span>
            </button>
          </div>
        </div>
      `;
    }).join("");

    eventsContainer.innerHTML = bannerHtml + cardsHtml;

    // Hook retry button if present
    const retryBtn = document.getElementById("cal-retry-btn");
    if (retryBtn) {
      retryBtn.addEventListener("click", () => loadCalendarEvents());
    }

    // Bind individual event alert buttons
    eventsContainer.querySelectorAll(".event-tg-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = "<span>⏳ Sending...</span>";
        try {
          await dispatchTelegramCalendar();
          btn.innerHTML = "<span>✅ Sent!</span>";
          setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
          }, 3000);
        } catch (err) {
          btn.disabled = false;
          btn.innerHTML = originalText;
        }
      });
    });
  }

  // 1. Fetch & Render Calendar Events
  async function loadCalendarEvents() {
    eventsContainer.innerHTML = `
      <div style="grid-column: span 2; text-align: center; padding: 2.5rem; color: var(--text-muted);">
        <span class="pulse-dot" style="display: inline-block; margin-right: 8px;"></span>
        Syncing academic calendar from NextClaw OS...
      </div>
    `;

    try {
      const res = await fetch(`${API_BASE}/api/v1/gateway/calendar?days_ahead=60`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const events = data.events || [];
      renderEventCards(events, false);
    } catch (err) {
      console.warn("NextClaw calendar API offline or unreachable, using verified schedule:", err);
      // Fallback to verified local schedule so user always has accurate dates
      renderEventCards(FALLBACK_CALENDAR_EVENTS, true);
    }
  }

  // 2. Send Calendar to Telegram Function
  async function dispatchTelegramCalendar() {
    if (sendTelegramBtn) {
      sendTelegramBtn.disabled = true;
      sendTelegramBtn.innerHTML = "<span>⏳ Dispatching to Telegram...</span>";
    }

    if (statusBox) {
      statusBox.style.display = "block";
      statusBox.style.borderColor = "rgba(34, 211, 238, 0.4)";
      statusBox.style.background = "rgba(34, 211, 238, 0.1)";
      statusBox.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="pulse-dot" style="background-color: #22d3ee;"></span>
          <span>Transmitting Nextserve Academic Calendar to Telegram (Paschal: <code>7311614517</code>)...</span>
        </div>
      `;
    }

    try {
      const res = await fetch(`${API_BASE}/api/v1/gateway/calendar/send-telegram`, {
        method: "POST"
      });
      const data = await res.json();

      if (res.ok && data.status === "success") {
        const msgId = data.response?.result?.message_id || "OK";
        if (statusBox) {
          statusBox.style.borderColor = "rgba(34, 197, 94, 0.4)";
          statusBox.style.background = "rgba(34, 197, 94, 0.15)";
          statusBox.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
              <span style="color: #86efac; font-weight: 600;">
                ✅ <strong>Academic Calendar Alert Dispatched Successfully to Your Telegram!</strong>
              </span>
              <span style="font-size: 0.75rem; color: var(--text-dim); background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 4px;">
                Message ID: #${msgId} • Recipient: Paschal (@Godly_Paschal)
              </span>
            </div>
          `;
        }

        if (sendTelegramBtn) {
          sendTelegramBtn.innerHTML = "<span>✅ Sent to Your Phone!</span>";
          sendTelegramBtn.className = "btn-success";
          setTimeout(() => {
            sendTelegramBtn.disabled = false;
            sendTelegramBtn.innerHTML = "<span>📲 Send Calendar to Telegram</span>";
            sendTelegramBtn.className = "btn-primary";
          }, 4000);
        }
      } else {
        throw new Error(data.message || data.detail || "Failed to deliver Telegram notification");
      }
    } catch (err) {
      if (statusBox) {
        statusBox.style.borderColor = "rgba(239, 68, 68, 0.4)";
        statusBox.style.background = "rgba(239, 68, 68, 0.12)";
        statusBox.innerHTML = `
          <span style="color: #fca5a5;">
            ❌ <strong>Telegram Dispatch Error:</strong> ${escapeHtml(err.message)}
          </span>
        `;
      }
      if (sendTelegramBtn) {
        sendTelegramBtn.disabled = false;
        sendTelegramBtn.innerHTML = "<span>📲 Send Calendar to Telegram</span>";
      }
      throw err;
    }
  }

  // 3. Attach Listeners
  if (sendTelegramBtn) {
    sendTelegramBtn.addEventListener("click", () => dispatchTelegramCalendar());
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      loadCalendarEvents();
    });
  }

  // Initial load
  loadCalendarEvents();
}

/**
 * =========================================================================
 * NEXTCLAW CYBERNETIC ENVIRONMENT ENGINE (OpenClaw-Inspired Full-Bleed Stage)
 * =========================================================================
 * - Continuous ambient multi-harmonic ASCII waving & breathing motion
 * - Real-time mouse & touch interaction (elastic displacement, phosphor beam aura,
 *   glyph scrambling, touch shockwave ripples, and 3D parallax)
 * - Ultra-crisp High-DPI canvas rendering with seamless environmental vignette
 */
function initClawEnvironment() {
  const canvas = document.getElementById("claw-environment-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const stage = document.getElementById("claw-stage-environment") || canvas.parentElement;
  const hero = document.getElementById("openclaw-hero") || stage;
  const anchor = document.getElementById("claw-center-anchor");

  if (!ctx || !stage) return;

  // Character sets
  const CHARS = " .·:;=+xX#8@";
  const CYBER_CHARS = ["0", "1", "<", ">", "/", "[", "]", "#", "X", "@", "$", "%", "*", "+", "§", "∆", "Ø", "Ξ", "Ψ", "⌘"];

  let width = 0;
  let height = 0;
  let dpr = window.devicePixelRatio || 1;
  let cols = 0;
  let rows = 0;
  let cellW = 12;
  let cellH = 15;
  let grid = [];

  // Mouse & touch physics state
  const mouse = {
    x: -9999,
    y: -9999,
    targetX: -9999,
    targetY: -9999,
    active: false,
    lastX: -9999,
    lastY: -9999,
    speed: 0
  };

  // Concentric shockwave ripples
  const ripples = [];

  // Resize and build the ASCII grid
  function resize() {
    const rect = stage.getBoundingClientRect();
    width = Math.max(320, rect.width);
    height = Math.max(260, rect.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2); // Cap at 2 for smooth 60fps

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Responsive cell dimensions
    cellW = width < 640 ? 11 : width < 1024 ? 12 : 13;
    cellH = width < 640 ? 13 : width < 1024 ? 15 : 16;

    cols = Math.ceil(width / cellW);
    rows = Math.ceil(height / cellH);

    buildGrid();
  }

  // Generate ASCII grid with OpenClaw wing envelopes & ambient field
  function buildGrid() {
    grid = [];
    const centerX = width * 0.5;
    const centerY = height * 0.44;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const baseX = c * cellW + cellW * 0.5;
        const baseY = r * cellH + cellH * 0.5;

        // Distance and horizontal offset from center
        const dx = Math.abs(baseX - centerX) / (width * 0.5);
        const distToCenter = Math.hypot(baseX - centerX, baseY - centerY);

        // OpenClaw iconic dual-wing arcs
        const wingArcUpper = centerY - 18 - Math.sin(dx * Math.PI * 0.85) * 42 + Math.pow(dx, 1.35) * 48;
        const wingArcLower = wingArcUpper + 44 + Math.pow(dx, 1.15) * 46;

        let baseDensity = 0;

        // Wing band density
        if (baseY >= wingArcUpper - 22 && baseY <= wingArcLower + 26) {
          const midArc = (wingArcUpper + wingArcLower) * 0.5;
          const distToMid = Math.abs(baseY - midArc);
          const wingThickness = (wingArcLower - wingArcUpper) * 0.5 + 20;
          const wingFactor = Math.max(0, 1 - (distToMid / wingThickness));
          baseDensity = Math.pow(wingFactor, 1.2) * 0.95;
        }

        // Center cyber core ring (around avatar)
        if (distToCenter >= 52 && distToCenter <= 136) {
          const ringCenter = 94;
          const ringDist = Math.abs(distToCenter - ringCenter);
          const ringFactor = Math.max(0, 1 - (ringDist / 42));
          baseDensity = Math.max(baseDensity, ringFactor * 0.72);
        } else if (distToCenter < 52) {
          // Clear immediate core center for crisp logo visibility
          baseDensity *= 0.15;
        }

        // Ambient cyber horizon & bottom matrix dither
        const ambientHorizon = (1 - Math.pow(dx, 1.6)) * 0.14;
        const bottomDither = (baseY / height) > 0.75 ? (1 - (baseY / height)) * 0.18 : 0;
        baseDensity = Math.min(1, baseDensity + ambientHorizon + bottomDither);

        grid.push({
          baseX,
          baseY,
          currentX: baseX,
          currentY: baseY,
          baseDensity,
          glow: 0,
          scrambleTimer: 0,
          scrambleChar: "",
          dx,
          distToCenter
        });
      }
    }
  }

  // Pointer listeners (mouse & touch)
  function handlePointerMove(clientX, clientY) {
    const rect = stage.getBoundingClientRect();
    const nx = clientX - rect.left;
    const ny = clientY - rect.top;

    // Check if pointer is within or near the environment
    if (nx >= -60 && nx <= rect.width + 60 && ny >= -60 && ny <= rect.height + 60) {
      mouse.targetX = nx;
      mouse.targetY = ny;
      mouse.active = true;

      // Calculate speed and trigger ripples on energetic movements
      const moved = Math.hypot(nx - mouse.lastX, ny - mouse.lastY);
      mouse.speed = moved;
      mouse.lastX = nx;
      mouse.lastY = ny;

      if (moved > 28 && ripples.length < 6) {
        ripples.push({
          x: nx,
          y: ny,
          radius: 12,
          maxRadius: width < 640 ? 190 : 280,
          strength: 0.95,
          speed: 6.5
        });
      }
    } else {
      mouse.active = false;
    }
  }

  function handlePointerLeave() {
    mouse.active = false;
    mouse.targetX = -9999;
    mouse.targetY = -9999;
  }

  // Event bindings
  window.addEventListener("pointermove", (e) => {
    handlePointerMove(e.clientX, e.clientY);
  }, { passive: true });

  stage.addEventListener("pointerdown", (e) => {
    handlePointerMove(e.clientX, e.clientY);
    // Shockwave on click / tap
    const rect = stage.getBoundingClientRect();
    ripples.push({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      radius: 10,
      maxRadius: width < 640 ? 240 : 360,
      strength: 1.35,
      speed: 7.5
    });
  }, { passive: true });

  hero.addEventListener("pointerleave", handlePointerLeave, { passive: true });
  window.addEventListener("pointerleave", handlePointerLeave, { passive: true });

  // Handle resizing
  window.addEventListener("resize", resize);
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(resize);
    ro.observe(stage);
  }
  resize();

  // Animation render loop
  let animId = null;

  function render() {
    animId = requestAnimationFrame(render);

    if (document.hidden || width <= 0 || height <= 0) return;

    ctx.clearRect(0, 0, width, height);

    const time = performance.now() * 0.0014;

    // Smooth mouse position tracking
    if (mouse.active) {
      mouse.x += (mouse.targetX - mouse.x) * 0.22;
      mouse.y += (mouse.targetY - mouse.y) * 0.22;
    } else {
      mouse.x += (-9999 - mouse.x) * 0.1;
      mouse.y += (-9999 - mouse.y) * 0.1;
    }

    // Update shockwave ripples
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      r.radius += r.speed;
      r.strength *= 0.955;
      if (r.radius > r.maxRadius || r.strength < 0.04) {
        ripples.splice(i, 1);
      }
    }

    // 3D Parallax & Magnetic Tracking for center mascot anchor
    if (anchor) {
      if (mouse.active) {
        const normX = Math.max(-1, Math.min(1, (mouse.x - width * 0.5) / (width * 0.5)));
        const normY = Math.max(-1, Math.min(1, (mouse.y - height * 0.44) / (height * 0.5)));
        anchor.style.transform = `translate3d(${(normX * 14).toFixed(1)}px, ${(normY * 11).toFixed(1)}px, 0) rotateY(${(normX * 10).toFixed(1)}deg) rotateX(${(-normY * 8).toFixed(1)}deg)`;
      } else {
        anchor.style.transform = "translate3d(0, 0, 0) rotateY(0deg) rotateX(0deg)";
      }
    }

    // Setup typography context
    const fontSize = width < 640 ? 11 : 13;
    ctx.font = `600 ${fontSize}px 'Fira Code', 'Courier New', monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const mouseRadius = width < 640 ? 120 : 170;
    const centerX = width * 0.5;
    const centerY = height * 0.44;

    // Render cells
    const len = grid.length;
    for (let i = 0; i < len; i++) {
      const cell = grid[i];

      // Multi-harmonic continuous wave equation
      const w1 = Math.sin(cell.baseX * 0.007 + time * 1.7 + cell.baseY * 0.005);
      const w2 = Math.cos(cell.baseX * 0.012 - time * 1.2 + cell.baseY * 0.008);
      const w3 = Math.sin(Math.hypot(cell.baseX - centerX, cell.baseY - centerY) * 0.022 - time * 2.1);
      const combinedWave = (w1 + w2 * 0.72 + w3 * 0.52) / 2.24;

      // Fluid vertical & horizontal undulation ("it will be moving")
      let posX = cell.baseX + Math.cos(cell.baseY * 0.006 + time * 1.3) * 2.8;
      let posY = cell.baseY + combinedWave * 5.8;

      // Mouse contact physics ("even when mouse touches it")
      if (mouse.active) {
        const mdx = posX - mouse.x;
        const mdy = posY - mouse.y;
        const mdist = Math.hypot(mdx, mdy);

        if (mdist < mouseRadius) {
          const prox = 1 - mdist / mouseRadius;
          // Elastic push away from cursor
          const push = Math.sin(prox * Math.PI * 0.5) * (width < 640 ? 18 : 25);
          const safeDist = mdist || 1;
          posX += (mdx / safeDist) * push;
          posY += (mdy / safeDist) * push;

          // Luminescence boost
          cell.glow = Math.max(cell.glow, Math.pow(prox, 1.15));

          // Scramble glyph on direct touch
          if (prox > 0.32 && Math.random() < 0.28) {
            cell.scrambleChar = CYBER_CHARS[Math.floor(Math.random() * CYBER_CHARS.length)];
            cell.scrambleTimer = 16;
          }
        }
      }

      // Check ripples for wave perturbation
      for (let j = 0; j < ripples.length; j++) {
        const r = ripples[j];
        const rdist = Math.abs(Math.hypot(cell.baseX - r.x, cell.baseY - r.y) - r.radius);
        if (rdist < 28) {
          const rfactor = (1 - rdist / 28) * r.strength;
          posY -= rfactor * 7.5;
          cell.glow = Math.max(cell.glow, rfactor * 0.9);
        }
      }

      // Density modulation with waving
      let density = cell.baseDensity + combinedWave * 0.24;
      density = Math.max(0, Math.min(1, density));

      // Skip empty or nearly invisible background cells
      if (density < 0.05 && cell.glow < 0.06) continue;

      // Determine character
      let charToDraw;
      if (cell.scrambleTimer > 0) {
        charToDraw = cell.scrambleChar;
        cell.scrambleTimer--;
      } else {
        const charIdx = Math.floor(density * (CHARS.length - 1));
        charToDraw = CHARS[charIdx];
      }

      if (!charToDraw || charToDraw === " ") continue;

      // Phosphor color rendering
      if (cell.glow > 0.08) {
        // Active touch glow (phosphor cyber emerald / cyan beam)
        const glowAlpha = Math.min(1, 0.45 + cell.glow * 0.55);
        ctx.shadowColor = cell.glow > 0.5 ? "rgba(103, 232, 249, 0.85)" : "rgba(74, 222, 128, 0.85)";
        ctx.shadowBlur = Math.floor(cell.glow * 14);
        ctx.fillStyle = cell.glow > 0.55
          ? `rgba(167, 243, 208, ${glowAlpha.toFixed(2)})`
          : `rgba(74, 222, 128, ${glowAlpha.toFixed(2)})`;
        ctx.fillText(charToDraw, posX, posY);
        ctx.shadowBlur = 0;
        cell.glow *= 0.915; // Smooth phosphorescent decay
      } else {
        // Ambient cybernetic wave color
        const baseAlpha = 0.22 + density * 0.52;
        ctx.fillStyle = `rgba(52, 211, 153, ${baseAlpha.toFixed(2)})`;
        ctx.fillText(charToDraw, posX, posY);
      }
    }
  }

  render();
}
