// ============================================================
// OmniscientAI — Centralized Data Store
// Design: Luminous Depth — atmospheric dark UI
// ============================================================

export const BRAND = {
  name: "OmniscientAI",
  tagline: "Melbourne's vendor-neutral AI training for SMEs that actually transforms how your team works",
  abn: "12 345 678 901",
  address: "Level 10, 440 Collins Street, Melbourne VIC 3000",
  email: "hello@omniscientai.com.au",
  phone: "+61 3 9000 1234",
  website: "omniscientai.com.au",
};

export const WORKSHOPS = [
  {
    slug: "ai-for-business-leaders",
    title: "AI for Business Leaders",
    subtitle: "Strategic AI literacy for decision-makers",
    duration: "Full day (8 hours)",
    format: "In-person or Virtual",
    priceRange: "$2,500 – $4,500",
    priceNote: "per group (up to 15 participants)",
    heroImage: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/workshop-hero-RiW9CrmegCLFskYQbK79ni.webp",
    description: "Cut through the AI hype. This workshop gives business leaders a practical framework for identifying high-impact AI opportunities, evaluating vendors without bias, and building a 90-day implementation roadmap.",
    whoIsItFor: [
      "CEOs and Managing Directors of SMEs (10-200 employees)",
      "Operations Managers looking to automate workflows",
      "Department heads evaluating AI tools for their teams",
      "Board members needing AI governance literacy",
    ],
    modules: [
      { title: "The AI Landscape", description: "Understanding what AI can and cannot do today — cutting through vendor hype with real capability assessments", duration: "90 min" },
      { title: "Opportunity Mapping", description: "Identifying the 3-5 highest-ROI AI use cases specific to your business using our proprietary scoring matrix", duration: "120 min" },
      { title: "Vendor Evaluation Framework", description: "A vendor-neutral methodology for comparing AI tools, platforms, and service providers", duration: "90 min" },
      { title: "Implementation Roadmap", description: "Building your personalised 90-day AI implementation plan with quick wins and strategic bets", duration: "120 min" },
    ],
    outcomes: [
      "Leave with 5 identified AI opportunities ranked by ROI and feasibility",
      "A vendor-neutral evaluation scorecard you can use immediately",
      "A 90-day implementation roadmap with assigned owners and milestones",
      "Confidence to lead AI conversations with your board and team",
    ],
    faqs: [
      { q: "Do I need technical knowledge?", a: "No. This workshop is designed for business leaders, not engineers. We focus on strategic decision-making, not code." },
      { q: "Can this be customised for our industry?", a: "Absolutely. We tailor examples and case studies to your specific sector. Contact us to discuss." },
      { q: "What's the ideal group size?", a: "We recommend 8-15 participants for optimal interaction. Larger groups can be accommodated with adjusted pricing." },
      { q: "Is there post-workshop support?", a: "Yes. All attendees receive 30 days of email support and access to our AI implementation resource library." },
    ],
    testimonials: [
      { name: "Sarah Chen", role: "COO, Meridian Legal", quote: "Finally, an AI workshop that didn't try to sell us a specific platform. We left with a clear roadmap and have already implemented two quick wins." },
      { name: "James Okafor", role: "MD, Pacific Manufacturing", quote: "The vendor evaluation framework alone was worth the investment. We've saved thousands by avoiding the wrong tools." },
    ],
  },
  {
    slug: "microsoft-copilot-masterclass",
    title: "Microsoft Copilot Masterclass",
    subtitle: "Hands-on productivity transformation with Microsoft 365 Copilot",
    duration: "Half day (4 hours)",
    format: "In-person or Virtual",
    priceRange: "$1,500 – $2,500",
    priceNote: "per group (up to 20 participants)",
    heroImage: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/data-viz-fmdiC2Rj58qfwNQK6p6KsZ.webp",
    description: "Your team has Copilot licenses but is using 10% of its capability. This hands-on masterclass transforms passive users into power users with real workflows they can implement the same afternoon.",
    whoIsItFor: [
      "Teams already using Microsoft 365 with Copilot licenses",
      "Administrative and operations staff drowning in repetitive tasks",
      "Managers wanting to standardise AI-assisted workflows",
      "IT leads responsible for Copilot rollout and adoption",
    ],
    modules: [
      { title: "Copilot Foundations", description: "Understanding how Copilot works across Word, Excel, PowerPoint, Outlook, and Teams — and where it excels vs. falls short", duration: "60 min" },
      { title: "Prompt Engineering for Business", description: "The art of writing prompts that get useful results — templates, frameworks, and common mistakes", duration: "60 min" },
      { title: "Workflow Automation", description: "Building 5 real automated workflows: meeting summaries, email drafting, data analysis, presentation creation, and document review", duration: "90 min" },
      { title: "Advanced Techniques", description: "Copilot Studio basics, custom GPTs for your organisation, and integration with Power Automate", duration: "30 min" },
    ],
    outcomes: [
      "Your team will leave with 5 implemented AI workflows they can use immediately",
      "A prompt library customised to your business context",
      "Measurable time savings of 5-10 hours per person per week",
      "Confidence to train colleagues and expand Copilot adoption",
    ],
    faqs: [
      { q: "Do participants need Copilot licenses?", a: "Yes. Each participant needs an active Microsoft 365 Copilot license. We can help you evaluate licensing options before the workshop." },
      { q: "What skill level is required?", a: "Basic Microsoft 365 proficiency. If your team can send emails in Outlook and create documents in Word, they're ready." },
      { q: "Can we focus on specific apps?", a: "Yes. We can weight the workshop toward Excel, Teams, or any other M365 app based on your team's needs." },
      { q: "Is this a Microsoft-endorsed workshop?", a: "We are vendor-neutral trainers. This means we'll also tell you where Copilot falls short and suggest alternatives." },
    ],
    testimonials: [
      { name: "Lisa Tran", role: "Office Manager, Vertex Consulting", quote: "My team went from barely using Copilot to saving 2 hours a day each. The prompt templates alone were game-changing." },
      { name: "David Park", role: "IT Director, Coastal Health", quote: "The vendor-neutral perspective was refreshing. They showed us where Copilot shines and where we should look at other tools." },
    ],
  },
  {
    slug: "ai-governance-essentials",
    title: "AI Governance Essentials",
    subtitle: "Risk management and responsible AI for Australian businesses",
    duration: "Half day (4 hours)",
    format: "In-person or Virtual",
    priceRange: "$2,000 – $3,500",
    priceNote: "per group (up to 15 participants)",
    heroImage: "https://d2xsxph8kpxj0f.cloudfront.net/310419663026972742/it6qHcTHLu2dmqyuKKnamM/ai-brain-dmFjeh4UoufhTZyDTgkXjM.webp",
    description: "AI governance isn't optional — it's a business imperative. This workshop gives your leadership team a practical governance framework aligned with Australia's AI Ethics Principles and emerging regulatory requirements.",
    whoIsItFor: [
      "C-suite executives and board members",
      "Risk and compliance managers",
      "Legal counsel advising on AI adoption",
      "HR leaders managing AI's impact on workforce",
    ],
    modules: [
      { title: "The Regulatory Landscape", description: "Australia's AI Ethics Principles, Privacy Act implications, and what's coming in 2025-2026 — practical compliance, not legal theory", duration: "60 min" },
      { title: "Risk Assessment Framework", description: "Identifying and scoring AI risks across bias, privacy, security, and operational dimensions using our structured assessment tool", duration: "60 min" },
      { title: "Governance Policy Workshop", description: "Drafting your organisation's AI Acceptable Use Policy — a living document your team will actually follow", duration: "90 min" },
      { title: "Implementation & Monitoring", description: "Setting up governance checkpoints, audit trails, and incident response procedures", duration: "30 min" },
    ],
    outcomes: [
      "A draft AI Acceptable Use Policy tailored to your organisation",
      "A risk assessment scorecard for evaluating new AI tools",
      "Understanding of Australian regulatory requirements and timeline",
      "A governance implementation checklist with clear ownership",
    ],
    faqs: [
      { q: "Is this relevant for small businesses?", a: "Absolutely. AI governance scales with your risk profile, not your size. We tailor the framework to SME-appropriate levels." },
      { q: "Do we need a legal team present?", a: "Helpful but not required. We provide practical frameworks, not legal advice. We recommend your legal counsel reviews the output." },
      { q: "How does this relate to ISO 42001?", a: "Our framework aligns with ISO 42001 (AI Management Systems) principles while being practical enough for SMEs to implement immediately." },
      { q: "Can this be combined with other workshops?", a: "Yes. We often pair this with 'AI for Business Leaders' as a two-day intensive." },
    ],
    testimonials: [
      { name: "Michelle Wong", role: "Risk Manager, Apex Financial", quote: "We went from having no AI policy to a comprehensive governance framework in a single afternoon. Essential for any business using AI." },
      { name: "Robert Nguyen", role: "CEO, InnovateMed", quote: "The regulatory landscape overview was eye-opening. We're now ahead of compliance requirements instead of scrambling to catch up." },
    ],
  },
];

export const SERVICES = [
  // -------------------------------------------------------------------------
  // Pillar 1 — Vertical SaaS for consequential industries.
  // Seed content drafted 2026-04-22. TODO: founder to validate claims,
  // especially pricing, regulatory references, and integration specifics.
  // -------------------------------------------------------------------------
  {
    slug: "bioenergy",
    title: "Bioenergy & agribusiness intelligence",
    subtitle: "Bloomberg for bioenergy. The wedge is ABFI.",
    description: "ABFI is our applied AI platform for bioenergy and agribusiness — bankability assessment, feedstock matching, CORSIA compliance, and R&D grants. For producers raising capital, financiers underwriting deals, and regulators managing the energy transition.",
    features: [
      "Bankability reports that speak the language lenders and equity actually read",
      "Feedstock supply-and-demand matching across producers, aggregators, and offtakers",
      "CORSIA compliance monitoring and attestation workflows",
      "R&D tax incentive, CEFC, and ARENA grant fit assessment",
      "Sovereign data hosting — your yield, supply, and financial models stay in Australia",
      "White-label reporting for your own clients where applicable",
    ],
    process: [
      { step: "Data audit", description: "We connect to your existing systems — ERP, sensors, GIS, accounting — in week 1 and map your data against ABFI's domain model." },
      { step: "Pilot", description: "One reporting flow live in production in weeks 2-4, scoped to the outcome that matters most to your team right now." },
      { step: "Scale", description: "Additional flows, custom integrations, and multi-site rollout as the platform proves itself against your operating reality." },
      { step: "Operate", description: "We run the platform as a managed service — you see the output, not the plumbing. Tuning, alerts, and escalations are on us." },
    ],
  },
  {
    slug: "defence",
    title: "Sovereign defence & industrial supply chain",
    subtitle: "Speaks ASCA, DIDG, and R&DTI natively.",
    description: "For prime contractors, defence-supply SMEs, and government buyers who can't send their data to California. Sovereign by default — built, hosted, and operated in Australia. Knows the acronyms, knows the forms, knows the pace.",
    features: [
      "ASCA and DIDG programme workflows — built-in, not bolted on",
      "R&DTI capture and evidence aligned with the sovereign industrial base",
      "Supply chain mapping, supplier attestation, and compliance for defence-adjacent SMEs",
      "On-shore hosting only — no US or Azure-region fallback, no offshore data processing",
      "Procurement workflows tailored to prime contractors and government buyers",
      "Auditable agent actions — every decision leaves a trail that survives an IRAP review",
    ],
    process: [
      { step: "Security briefing", description: "A week 0 session to cover data handling, hosting posture, and the audit trail your contracts require. Free, under NDA." },
      { step: "Onboarding", description: "Sovereign tenancy provisioned on Australian-hosted infrastructure. We map one programme (ASCA, DIDG, or R&DTI) end-to-end in weeks 1-3." },
      { step: "Expand", description: "Additional programmes, supplier network, and procurement workflows added as the tenancy proves out against your compliance posture." },
      { step: "Operate", description: "Managed service with named Australian-based practitioners. Escalation paths, audit reports, and hosting attestations included." },
    ],
  },
  {
    slug: "mental-health",
    title: "Mental health & NDIS-funded care",
    subtitle: "Check-ys is the wedge.",
    description: "Check-ys is built around the realities of NDIS-funded care — not bolted onto a general-purpose tool. For NDIS providers, allied health practitioners, and participants who deserve software that respects how funded care actually works.",
    features: [
      "Session notes and plan-goal tracking built for NDIS reporting cycles",
      "Practitioner tooling — drafting, summarisation, billing-ready documentation",
      "Participant-facing experiences that respect autonomy, dignity, and consent",
      "Privacy-first architecture with Australian data residency by default",
      "Allied-health-specific workflows — occupational therapy, psychology, support coordination — not a generic EHR",
      "Per-seat billing that scales with your practice, not a platform-vendor tax",
    ],
    process: [
      { step: "Clinical fit check", description: "A 30-minute call with a practitioner from your team to confirm Check-ys maps to how you actually document and bill." },
      { step: "Seat provisioning", description: "Per-user setup with role-based access, plan-goal templates, and NDIS price-guide codes pre-loaded. Usually a single afternoon." },
      { step: "Go-live", description: "First real session notes inside week 1. We shadow the first week of billing cycles and correct anything that looks off before it hits the NDIA." },
      { step: "Operate", description: "Ongoing managed support, price-guide updates, and regulatory change tracking handled for you." },
    ],
  },
  // -------------------------------------------------------------------------
  // Pillar 2 — Business Agents as a Service (The Omniscient Workforce).
  // Single SERVICES entry for the umbrella; per-persona pages are a
  // follow-up. Seed content drafted 2026-04-22. TODO: founder to validate
  // per-agent pricing and the AI-EA onboarding specifics.
  // -------------------------------------------------------------------------
  {
    slug: "workforce",
    title: "The Omniscient Workforce",
    subtitle: "A managed workforce of AI agents.",
    description: "Not a chatbot. Not a prompt template. A managed workforce of AI agents, each specialised to a real role — executive assistant, analyst, operator, BDR, compliance officer, engineer. Hosted on sovereign infrastructure. Tuned by humans. Billed per seat, per month.",
    features: [
      "AI-EA — calendar, email, drafting, and scheduling, run in the background for founders and executives",
      "AI Associate — brief synthesis, desk research, memo writing for analyst-heavy teams",
      "AI Operator — ticketed workflow execution, status updates, reporting loops that have to happen anyway",
      "AI BDR — inbound qualification and outbound sequencing, tuned to your ICP and tone",
      "AI Compliance Officer — audit trails, grant applications, regulatory reporting",
      "AI Engineer — pair programming, code review, devops tickets",
      "Sovereign hosting — not Azure Copilot, not Google Workspace AI. Your agents run on infrastructure you can point at on a map.",
      "Human-in-the-loop operations — we monitor and tune the agents; you operate the business",
    ],
    process: [
      { step: "Persona scoping", description: "A 60-minute call to pick the one persona that gives you the fastest ROI — usually AI-EA for founders, AI BDR for revenue teams, AI Compliance for regulated businesses." },
      { step: "Onboarding", description: "For AI-EA: calendar and email connection, voice-and-tone training on 20 of your historical drafts, escalation rules defined. Usually week 1." },
      { step: "Smoke-test", description: "A week of supervised operation — the agent drafts, a human approves. We catch tone and judgement drift before it hits an external party." },
      { step: "Scale", description: "Autonomous on the tasks that are proven, supervised on the ones that aren't, and additional personas added once the first is reliable." },
    ],
  },
  // -------------------------------------------------------------------------
  // Pillar 3 — The Companion (Omni). Phone-native, voice-first,
  // persistent-memory. Seed content drafted 2026-04-22. TODO: founder
  // to validate consumer/pro pricing and the Android-only positioning.
  // -------------------------------------------------------------------------
  {
    slug: "companion",
    title: "The Companion — Omni",
    subtitle: "An AI that lives in your pocket, not in a chat window.",
    description: "Omni is phone-native. Voice-first. Remembers your life. Makes your calls, books your days, runs your errands. Integrates with your Android OS — calls, SMS, calendar, contacts, accessibility services. Yours alone — not Sam Altman's, not Sundar's.",
    features: [
      "Android-hosted agent that lives on-device, not in a tab on your laptop",
      "Voice-first interaction with text and full-UI fallbacks when you need them",
      "Persistent memory — knows your people, your habits, your recurring decisions",
      "Deep OS integrations — calls, SMS, calendar, contacts, accessibility services, shortcuts",
      "On-device inference where possible, with a sovereign Australian cloud fallback",
      "Sovereign edition for defence and government users — no data leaves Australia, ever",
      "Consumer subscription plus an enterprise perk for executives at Pillar 1 and 2 customers",
    ],
    process: [
      { step: "Device setup", description: "A one-time sideload onto your Android device. Takes about ten minutes. iOS is on the roadmap but not available yet." },
      { step: "Memory seeding", description: "A guided 20-minute session where Omni learns your people, your calendar rhythm, your recurring errands, and your do-not-disturb rules." },
      { step: "Voice training", description: "Fifteen minutes of voice samples so Omni recognises you in any room and can match your tone when it drafts on your behalf." },
      { step: "Daily use", description: "Voice commands, background automations, and proactive suggestions. Tune the memory and rules as your life changes." },
    ],
  },
  // -------------------------------------------------------------------------
  // Legacy consulting service lines — de-emphasised but retained. Exist so
  // the "we also consult" option is still linkable for folks who need it.
  // -------------------------------------------------------------------------
  {
    slug: "ai-strategy-consulting",
    title: "AI Strategy Consulting",
    subtitle: "From AI curiosity to AI capability",
    description: "We work alongside your leadership team to develop a practical AI strategy that aligns with your business goals, budget, and team capabilities. No vendor lock-in, no unnecessary complexity.",
    features: [
      "Current-state assessment of your AI readiness across people, process, data, and technology",
      "Opportunity identification and prioritisation using our ROI-weighted scoring matrix",
      "Technology stack recommendations — vendor-neutral, budget-appropriate",
      "Implementation roadmap with 30/60/90-day milestones",
      "Change management strategy for AI adoption across your organisation",
      "Ongoing advisory retainer options for implementation support",
    ],
    process: [
      { step: "Discovery", description: "Deep-dive into your business operations, pain points, and strategic goals through stakeholder interviews and process mapping" },
      { step: "Analysis", description: "AI readiness assessment, opportunity scoring, and technology landscape evaluation tailored to your industry" },
      { step: "Strategy", description: "Detailed AI strategy document with prioritised initiatives, resource requirements, and expected ROI" },
      { step: "Roadmap", description: "Actionable implementation plan with clear milestones, owners, and success metrics" },
    ],
  },
  {
    slug: "ai-readiness-assessment",
    title: "AI Readiness Assessment",
    subtitle: "Know where you stand before you invest",
    description: "A structured assessment of your organisation's readiness to adopt and benefit from AI. We evaluate your data maturity, team skills, process automation potential, and strategic alignment to give you a clear picture of where to start.",
    features: [
      "Comprehensive evaluation across 5 dimensions: Data, People, Process, Technology, Strategy",
      "Benchmarking against industry peers and best practices",
      "Gap analysis with specific, actionable recommendations",
      "Prioritised opportunity register with estimated ROI ranges",
      "Executive summary suitable for board presentation",
      "Follow-up workshop to present findings and align on next steps",
    ],
    process: [
      { step: "Intake", description: "Initial questionnaire and document review to understand your current technology landscape and business context" },
      { step: "Assessment", description: "On-site or virtual assessment sessions with key stakeholders across departments" },
      { step: "Scoring", description: "Quantitative scoring across our 5-dimension AI Readiness Framework with industry benchmarks" },
      { step: "Report", description: "Comprehensive report with findings, recommendations, and a prioritised action plan" },
    ],
  },
];

export const INDUSTRIES = [
  {
    slug: "professional-services",
    title: "Professional Services",
    subtitle: "Law firms, accounting practices, and consultancies",
    description: "Professional services firms are sitting on a goldmine of AI opportunity. From automated document review to intelligent client communication, we help firms transform billable efficiency without compromising quality.",
    useCases: [
      "Automated document drafting and review",
      "Client communication summarisation and follow-up",
      "Knowledge management and precedent search",
      "Time tracking and billing optimisation",
      "Client onboarding automation",
    ],
    stat: "40%",
    statLabel: "average time saved on document review",
  },
  {
    slug: "healthcare",
    title: "Healthcare",
    subtitle: "Clinics, allied health, and aged care providers",
    description: "Healthcare providers face unique AI challenges around privacy, regulation, and patient safety. We help navigate these complexities while unlocking practical efficiency gains in administration, scheduling, and clinical documentation.",
    useCases: [
      "Clinical documentation and note-taking automation",
      "Patient scheduling and resource optimisation",
      "Administrative workflow automation",
      "Compliance monitoring and reporting",
      "Patient communication and follow-up",
    ],
    stat: "60%",
    statLabel: "reduction in administrative burden",
  },
  {
    slug: "manufacturing",
    title: "Manufacturing",
    subtitle: "Production, logistics, and supply chain",
    description: "Manufacturing is where AI delivers the most measurable ROI. From predictive maintenance to quality control, we help manufacturers implement AI solutions that directly impact the bottom line.",
    useCases: [
      "Predictive maintenance and equipment monitoring",
      "Quality control and defect detection",
      "Supply chain optimisation and demand forecasting",
      "Production scheduling and resource allocation",
      "Safety monitoring and incident prevention",
    ],
    stat: "25%",
    statLabel: "reduction in unplanned downtime",
  },
  {
    slug: "retail",
    title: "Retail",
    subtitle: "Brick-and-mortar, e-commerce, and omnichannel",
    description: "Retail is being transformed by AI at every touchpoint. We help retailers implement practical AI solutions for inventory management, customer experience, and operational efficiency — without the enterprise price tag.",
    useCases: [
      "Inventory management and demand forecasting",
      "Personalised customer recommendations",
      "Dynamic pricing and promotion optimisation",
      "Customer service automation",
      "Visual merchandising and store layout optimisation",
    ],
    stat: "35%",
    statLabel: "improvement in inventory accuracy",
  },
];

export const INSIGHTS = [
  {
    slug: "getting-started-with-ai-for-your-sme",
    title: "Getting Started with AI for Your SME: A Practical Guide",
    category: "ai-for-business",
    categoryLabel: "AI for Business",
    author: "OmniscientAI Team",
    date: "2025-02-15",
    readTime: "8 min read",
    featured: true,
    excerpt: "Forget the hype. Here's a practical, step-by-step guide to identifying your first AI opportunity, evaluating tools, and implementing a pilot project — all within a typical SME budget.",
  },
  {
    slug: "ai-governance-australian-businesses",
    title: "AI Governance for Australian Businesses: What You Need to Know in 2025",
    category: "ai-governance",
    categoryLabel: "AI Governance",
    author: "OmniscientAI Team",
    date: "2025-02-01",
    readTime: "12 min read",
    featured: true,
    excerpt: "Australia's AI regulatory landscape is evolving fast. This guide covers the AI Ethics Principles, Privacy Act implications, and practical steps to build a governance framework that protects your business.",
  },
  {
    slug: "microsoft-copilot-vs-google-gemini",
    title: "Microsoft Copilot vs Google Gemini: An Honest Comparison for SMEs",
    category: "ai-tools",
    categoryLabel: "AI Tools",
    author: "OmniscientAI Team",
    date: "2025-01-20",
    readTime: "10 min read",
    featured: false,
    excerpt: "We tested both platforms across real business scenarios. Here's our vendor-neutral assessment of where each excels, where they fall short, and which is right for your team.",
  },
  {
    slug: "melbourne-ai-ecosystem-2025",
    title: "Melbourne's AI Ecosystem: Opportunities for Local SMEs",
    category: "melbourne-ai",
    categoryLabel: "Melbourne AI",
    author: "OmniscientAI Team",
    date: "2025-01-10",
    readTime: "6 min read",
    featured: false,
    excerpt: "Melbourne is emerging as Australia's AI hub. Discover the local resources, grants, and community networks available to help your SME leverage artificial intelligence.",
  },
  {
    slug: "ai-roi-measuring-real-business-impact",
    title: "Measuring AI ROI: A Framework for Real Business Impact",
    category: "ai-for-business",
    categoryLabel: "AI for Business",
    author: "OmniscientAI Team",
    date: "2024-12-15",
    readTime: "9 min read",
    featured: false,
    excerpt: "Most AI ROI calculations are fantasy. Here's a grounded framework for measuring the actual business impact of AI initiatives, including the hidden costs most vendors won't mention.",
  },
  {
    slug: "responsible-ai-sme-checklist",
    title: "The Responsible AI Checklist for SMEs",
    category: "ai-governance",
    categoryLabel: "AI Governance",
    author: "OmniscientAI Team",
    date: "2024-12-01",
    readTime: "7 min read",
    featured: false,
    excerpt: "You don't need a dedicated ethics board to use AI responsibly. This practical checklist helps SMEs implement responsible AI practices proportionate to their scale and risk profile.",
  },
];

export const QUIZ_QUESTIONS = [
  {
    id: 1,
    category: "Data Maturity",
    question: "How would you describe your organisation's data management practices?",
    options: [
      { label: "We mostly use spreadsheets and manual processes", score: 1 },
      { label: "We have some databases but data is siloed across departments", score: 2 },
      { label: "We have centralised data systems with some integration", score: 3 },
      { label: "We have a unified data platform with automated pipelines", score: 4 },
    ],
  },
  {
    id: 2,
    category: "Data Maturity",
    question: "How confident are you in the quality and completeness of your business data?",
    options: [
      { label: "We often find errors and gaps in our data", score: 1 },
      { label: "Data quality varies significantly across departments", score: 2 },
      { label: "We have data quality processes but they're not comprehensive", score: 3 },
      { label: "We have robust data governance with regular quality audits", score: 4 },
    ],
  },
  {
    id: 3,
    category: "Team Skills",
    question: "What is your team's current comfort level with AI tools?",
    options: [
      { label: "Most staff haven't used AI tools professionally", score: 1 },
      { label: "Some individuals use ChatGPT or similar tools informally", score: 2 },
      { label: "We've provided basic AI training to key teams", score: 3 },
      { label: "AI tools are integrated into daily workflows across the organisation", score: 4 },
    ],
  },
  {
    id: 4,
    category: "Team Skills",
    question: "Does your organisation have dedicated technical talent for AI initiatives?",
    options: [
      { label: "No technical staff — we outsource all IT", score: 1 },
      { label: "We have IT staff but no AI/ML expertise", score: 2 },
      { label: "We have some data-literate staff who could upskill", score: 3 },
      { label: "We have data analysts or engineers with AI experience", score: 4 },
    ],
  },
  {
    id: 5,
    category: "Process Automation",
    question: "How much of your business processes are currently automated?",
    options: [
      { label: "Very little — most processes are manual", score: 1 },
      { label: "We've automated some basic tasks (email, scheduling)", score: 2 },
      { label: "We use workflow automation tools for key processes", score: 3 },
      { label: "We have extensive automation with integration between systems", score: 4 },
    ],
  },
  {
    id: 6,
    category: "Process Automation",
    question: "How well-documented are your core business processes?",
    options: [
      { label: "Processes exist mainly in people's heads", score: 1 },
      { label: "Some processes are documented but many are informal", score: 2 },
      { label: "Most key processes are documented with clear steps", score: 3 },
      { label: "We have comprehensive process documentation with regular reviews", score: 4 },
    ],
  },
  {
    id: 7,
    category: "Strategic Alignment",
    question: "How does your leadership team view AI adoption?",
    options: [
      { label: "AI isn't on our strategic radar yet", score: 1 },
      { label: "There's curiosity but no formal commitment or budget", score: 2 },
      { label: "Leadership supports AI exploration with some allocated resources", score: 3 },
      { label: "AI is a strategic priority with dedicated budget and executive sponsorship", score: 4 },
    ],
  },
  {
    id: 8,
    category: "Strategic Alignment",
    question: "Have you identified specific business problems that AI could solve?",
    options: [
      { label: "We haven't thought about specific use cases", score: 1 },
      { label: "We have vague ideas but nothing concrete", score: 2 },
      { label: "We've identified 2-3 specific opportunities", score: 3 },
      { label: "We have a prioritised list of AI opportunities with business cases", score: 4 },
    ],
  },
  {
    id: 9,
    category: "Technology Infrastructure",
    question: "How would you describe your current technology infrastructure?",
    options: [
      { label: "Mostly legacy systems with limited cloud adoption", score: 1 },
      { label: "Mix of legacy and cloud with some integration challenges", score: 2 },
      { label: "Primarily cloud-based with good system integration", score: 3 },
      { label: "Modern cloud infrastructure with APIs and integration capabilities", score: 4 },
    ],
  },
  {
    id: 10,
    category: "Technology Infrastructure",
    question: "How does your organisation approach data security and privacy?",
    options: [
      { label: "Basic security measures — we know we need to improve", score: 1 },
      { label: "Standard security practices but no formal AI-specific policies", score: 2 },
      { label: "Strong security posture with privacy policies in place", score: 3 },
      { label: "Comprehensive security framework with AI-specific governance", score: 4 },
    ],
  },
];

export const NAV_LINKS = [
  {
    label: "Workshops",
    href: "/workshops",
    children: [
      { label: "AI for Business Leaders", href: "/workshops/ai-for-business-leaders" },
      { label: "Microsoft Copilot Masterclass", href: "/workshops/microsoft-copilot-masterclass" },
      { label: "AI Governance Essentials", href: "/workshops/ai-governance-essentials" },
      { label: "Custom Workshop", href: "/workshops/custom" },
    ],
  },
  {
    label: "Services",
    href: "/services",
    children: [
      { label: "AI Strategy Consulting", href: "/services/ai-strategy-consulting" },
      { label: "AI Readiness Assessment", href: "/services/ai-readiness-assessment" },
    ],
  },
  {
    label: "Industries",
    href: "/industries",
    children: [
      { label: "Professional Services", href: "/industries/professional-services" },
      { label: "Healthcare", href: "/industries/healthcare" },
      { label: "Manufacturing", href: "/industries/manufacturing" },
      { label: "Retail", href: "/industries/retail" },
    ],
  },
  {
    label: "AI Tools",
    href: "/playground",
    children: [
      { label: "Prompt Playground", href: "/playground" },
      { label: "AI Consultant", href: "/voice-consultant" },
      { label: "Document Analyser", href: "/document-analyser" },
      { label: "AI Readiness Quiz", href: "/ai-readiness-quiz" },
      { label: "ROI Calculator", href: "/roi-calculator" },
    ],
  },
  { label: "Insights", href: "/insights" },
  { label: "About", href: "/about" },
];
