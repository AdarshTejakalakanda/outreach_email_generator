# data_pipeline.py
import csv
import json
import os
import re
from config import *

def load_resume():
    if not os.path.exists(RESUME_FILE):
        print(f"Error: {RESUME_FILE} not found.")
        return ""
    with open(RESUME_FILE, "r") as f:
        return f.read()

def get_processed_ids():
    """Load already processed position IDs for crash recovery."""
    if not os.path.exists(OUTPUT_FILE):
        return set()
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row.get("position_id") for row in reader if row.get("position_id")}
    except Exception:
        return set()

def parse_payload(payload_str):
    """Extract useful fields from payload JSON column."""
    defaults = {
        "contact_email": "",
        "contact_phone": "",
        "author_name": "",
        "job_title": "",
        "contract_type": "",
        "post_text_preview": "",
    }
    if not payload_str:
        return defaults
    try:
        data = json.loads(payload_str)
        return {
            "contact_email": data.get("contact_email", ""),
            "contact_phone": data.get("contact_phone", ""),
            "author_name": data.get("author_name", ""),
            "job_title": data.get("job_title", ""),
            "contract_type": data.get("contract_type", ""),
            "post_text_preview": data.get("post_text_preview", ""),
        }
    except (json.JSONDecodeError, TypeError):
        return defaults

def extract_recruiter_name(description, contact_info):
    """Try to extract recruiter name from description or contact_info."""
    patterns = [
        r'(?:recruiter|contact|reach out to|share .* at)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+)\s+Technical Recruiter',
        r'([A-Z][a-z]+)\s+(?:Sr\.?|Senior)\s+Recruiter',
        r'(?:Thanks|Regards|Best)[,\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    ]
    
    full_text = f"{description} {contact_info}"
    for pattern in patterns:
        match = re.search(pattern, full_text)
        if match:
            name = match.group(1).strip()
            # Filter out common false positives
            if name.lower() not in ["email", "phone", "location", "job", "role", "note", "hello"]:
                return name
    return ""

def clean_title(title, payload_title):
    """Pick the better title between main column and payload."""
    garbage_patterns = [
        r'^(?:job type|for #|different technologies|hiring post|involves)',
        r'^(?:an experienced|we are)',
        r'w2|c2c|marketing',
    ]
    
    title_is_garbage = False
    if title:
        for pattern in garbage_patterns:
            if re.search(pattern, title.lower()):
                title_is_garbage = True
                break
    
    if (not title or title_is_garbage) and payload_title:
        clean = payload_title.strip()
        if len(clean) > 80:
            clean = clean[:80].rsplit(' ', 1)[0]
        return clean
    
    return title or "Position Not Specified"

def parse_contact_email(contact_info_str):
    """Parse 'EMAIL: xxx@yyy.com | Phone: ...' format."""
    email = ""
    phone = ""
    
    if not contact_info_str:
        return email, phone
    
    email_match = re.search(r'EMAIL:\s*([\w.+-]+@[\w.-]+)', contact_info_str, re.I)
    if email_match:
        email = email_match.group(1)
    else:
        email_match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', contact_info_str)
        if email_match:
            email = email_match.group(0)
    
    phone_match = re.search(r'Phone:\s*([\d\-\+\(\)\s]+)', contact_info_str, re.I)
    if phone_match:
        phone = phone_match.group(1).strip()
    
    return email, phone

def filter_job(title, description):
    """Check if job is relevant to AI/ML domain and not a junk/hotlist post."""
    full_text = f"{title} {description}".lower()
    
    if any(junk in full_text for junk in JUNK_KEYWORDS):
        return False
    
    for exc in EXCLUSION_KEYWORDS:
        if exc in full_text:
            if "ai" not in full_text and "machine learning" not in full_text:
                return False
    
    return any(inc in full_text for inc in INCLUSION_KEYWORDS)

def deduplicate_positions(positions):
    """Remove duplicate positions based on company + contact_email combo."""
    seen = set() 
    unique = []
    
    for pos in positions:
        payload = parse_payload(pos.get("payload", ""))
        email = payload.get("contact_email", "").lower()
        company = (pos.get("company") or "").lower().strip()
        title = (pos.get("title") or "").lower().strip()
        
        dedup_key = f"{company}|{title}|{email}"
        
        if dedup_key not in seen:
            seen.add(dedup_key)
            unique.append(pos)
    
    return unique

def append_to_csv(row_dict):
    """Append single row to output CSV (crash-safe)."""
    file_exists = os.path.exists(OUTPUT_FILE)
    fieldnames = [
        "position_id", "recruiter_name", "recruiter_email", "recruiter_phone",
        "company", "job_title", "location", "contract_type",
        "subject", "body", "status", "reason", "is_priority",
    ]
    with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)
