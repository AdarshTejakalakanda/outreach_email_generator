# AI Outreach Generator (Qwen 2.5 Edition)

An automated recruiter outreach engine that filters and generates hyper-personalized emails for AI/ML roles using local LLMs (Ollama).

## 🚀 Features
- **Domain Lock**: Automatically skips Frontend/Fullstack roles that don't involve AI.
- **Agentic AI Focus**: Leverages a specific candidate profile focused on Agents, RAG, and MLOps.
- **Local LLM**: Powered by Qwen 2.5 via Ollama for privacy and speed.
- **Batch Processing**: Handles large CSVs (1,600+ rows) with progress tracking and auto-saving.

## 🛠️ Setup

### 1. Requirements
- **Python 3.10+**
- **Ollama** installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Ollama
Download and run the Qwen 2.5 7B model (optimal for speed/quality on local hardware):
```bash
ollama pull qwen2.5:7b
```

### 4. Prepare Your Files
- `resume.txt`: Your latest resume content.
- `email_positions.csv`: Recruiter contact list with headers: `job_title`, `company`, `job_description`, `recruiter_name`, `recruiter_email`.

## To Run the Generator
Simply run the main script:
```bash
python main.py
```

The script will:
1.  **Filter**: Skip irrelevant roles based on the `INCLUSION` and `EXCLUSION` keywords.
2.  **Generate**: Call Qwen 2.5 7B to draft a catchy subject and a 3-paragraph personalized body.
3.  **Export**: Save results to `outreach_queue.csv` in real-time (every 10 rows).

## 🧠 Why Qwen2.5 for Recruitment?
- **Dual-Mode Intelligence**: Toggles between "Thinking" (for high-quality, complex email drafting) and "Non-thinking" (for lightning-fast processing).
- **Agentic Native**: Specifically fine-tuned for tool-calling and autonomous workflows, ensuring perfect adherence to JSON output constraints.
- **40K+ Context Window**: Handles even the longest job descriptions without losing context from your resume.

## 🧠 Strategic Logic
- **Catchy Subject Lines**: Includes AI keywords from the Job Title.
- **Problem Solving**: Bridges a specific project from your resume to the job's requirements.
- **Low Friction CTA**: Requests a brief sync in a professional, peer-to-peer tone.

---

