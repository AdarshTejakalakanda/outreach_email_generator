# config.py

INPUT_FILE = "email_positions.csv"
RESUME_FILE = "resume.txt"
OUTPUT_FILE = "outreach_queue.csv"
MODEL = "qwen3:8b"
MAX_RETRIES = 3

INCLUSION_KEYWORDS = [
    "ai/ml", "data engineering", "generative ai", "machine learning",
    "data scientist", "llm", "prompt engineer", "deep learning",
    "neural networks", "mlops", "genai", "computer vision", "nlp",
    "data architect", "rag", "ai research", "spark", "hadoop",
    "etl", "vector database", "reinforcement learning", "pytorch",
    "tensorflow", "agentic", "agents", "automation", "ai engineer",
    "data engineer", "ml engineer"
]

EXCLUSION_KEYWORDS = [
    "frontend", "css", "react only", "html", "ui/ux",
    "fullstack", ".net developer", "dotnet", "lab technician",
    "scanning operator"
]

PRIORITY_KEYWORDS = ["vertex ai", "langchain", "ollama", "agents", "rag", "agentic"]

JUNK_KEYWORDS = [
    "hotlist", "available consultant", "bench sales", "available candidates",
    "w2 marketing", "marketing on our w2", "candidatessearching", "c2crequirements",
    "available talent", "pool of consultants", "bench consultant", "available on corp to corp",
    "on our w2 for marketing", "available for immediate"
]

SYSTEM_PROMPT = """You are a specialized AI Talent Agent. Generate high-conversion, hyper-personalized outreach emails.

CANDIDATE CORE COMPETENCIES:
- Agentic AI Frameworks & RAG Systems
- LLMs & Prompt Engineering
- MLOps: Google Cloud Run / Vertex AI
- Data Engineering: SQL, Python, ETL, Vector Databases

RULES:
1. If job is purely Frontend/Fullstack with no AI component, output: {"status": "skip", "reason": "Non-AI/ML role"}
2. If job mentions Agents/Automation/LLMs, prioritize candidate's autonomous workflow experience
3. Professional peer-to-peer tone. If Recruiter Name is 'Not Provided', start with "Hi there," or "Hi Hiring Team,". DO NOT write "Hi Recruiter".
4. Subject: Catchy, include a relevant AI keyword from job title, under 60 chars
5. Body: Max 3 short paragraphs. Match a specific job requirement to a candidate skill
6. Mention contract type (W2/C2C) naturally if provided
7. End with a clear call-to-action
8. Sign off the email using the candidate's actual name found in the resume. NEVER use placeholders like "[Your Name]".

OUTPUT FORMAT - ONLY valid JSON, nothing else:
{"subject": "...", "email_body": "...", "status": "generated"}"""
