# llm_engine.py
import json
import re
import time
import ollama
from config import MODEL, MAX_RETRIES, SYSTEM_PROMPT

def parse_llm_response(content):
    """Clean and parse LLM JSON response."""
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    content = content.strip()
    return json.loads(content)

def generate_email(resume, job_data, retries=MAX_RETRIES):
    """Call local LLM with retry logic."""
    prompt = f"""/no_think
Candidate Resume:
{resume}

Job Details:
Company: {job_data['company']}
Title: {job_data['job_title']}
Location: {job_data['location']}
Contract Type: {job_data['contract_type']}
Description: {job_data['job_description'][:1500]}
Recruiter Name: {job_data['recruiter_name']}

Generate the outreach email JSON now."""

    for attempt in range(retries):
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                format="json",
                options={
                    "temperature": 0.7,
                    "num_predict": 1500,
                },
            )
            return parse_llm_response(response["message"]["content"])

        except json.JSONDecodeError:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            return {"status": "error", "reason": "JSON parse failed after retries"}

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return {"status": "error", "reason": str(e)}
