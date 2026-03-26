# main.py
import csv
from tqdm import tqdm
from config import INPUT_FILE, OUTPUT_FILE, PRIORITY_KEYWORDS
from data_pipeline import (
    load_resume,
    get_processed_ids,
    parse_payload,
    extract_recruiter_name,
    clean_title,
    parse_contact_email,
    filter_job,
    deduplicate_positions,
    append_to_csv,
)
from llm_engine import generate_email

def main():
    resume = load_resume()
    if not resume:
        return

    # ── Load CSV ──
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_positions = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_FILE}'. Please ensure the file exists.")
        return

    print(f"Total rows in CSV: {len(all_positions)}")

    # ── Deduplicate ──
    positions = deduplicate_positions(all_positions)
    print(f"After deduplication: {len(positions)}")

    # ── Crash Recovery ──
    processed_ids = get_processed_ids()
    remaining = [p for p in positions if str(p.get("id", "")) not in processed_ids]
    print(f"Already processed: {len(processed_ids)}")
    print(f"Remaining to process: {len(remaining)}")

    generated = 0
    skipped = 0
    filtered = 0
    failed = 0

    for row in tqdm(remaining, desc="Generating emails"):
        position_id = row.get("id", "")
        
        # ── Extract & Clean Data ──
        payload = parse_payload(row.get("payload", ""))
        
        raw_title = (row.get("title") or "").strip()
        job_title = clean_title(raw_title, payload.get("job_title", ""))
        
        description = (row.get("description") or payload.get("post_text_preview") or "").strip()
        company = (row.get("company") or "Unknown").strip()
        location = (row.get("location") or "").strip()
        contact_info = (row.get("contact_info") or "").strip()
        contract_type = payload.get("contract_type", "")
        
        # ── Skip empty or too short (likely junk) ──
        if not description or len(description) < 40:
            skipped += 1
            continue

        # ── Domain filter (and Junk validation) ──
        if not filter_job(job_title, description):
            filtered += 1
            continue

        # ── Extract recruiter info ──
        recruiter_email, recruiter_phone = parse_contact_email(contact_info)
        # Prefer payload email if available
        if not recruiter_email and payload.get("contact_email"):
            recruiter_email = payload["contact_email"]
        
        recruiter_name = payload.get("author_name", "").strip()
        if not recruiter_name:
            recruiter_name = extract_recruiter_name(description, contact_info)
        if not recruiter_name:
            recruiter_name = "Not Provided"

        # ── Priority check ──
        full_text = f"{job_title} {description}".lower()
        is_priority = any(p in full_text for p in PRIORITY_KEYWORDS)

        # ── Generate Email ──
        result = generate_email(resume, {
            "company": company,
            "job_title": job_title,
            "job_description": description,
            "location": location,
            "contract_type": contract_type,
            "recruiter_name": recruiter_name,
        })

        # ── Save Immediately ──
        output_row = {
            "position_id": position_id,
            "recruiter_name": recruiter_name,
            "recruiter_email": recruiter_email,
            "recruiter_phone": recruiter_phone,
            "company": company,
            "job_title": job_title,
            "location": location,
            "contract_type": contract_type,
            "subject": result.get("subject", ""),
            "body": result.get("email_body", ""),
            "status": result.get("status", "unknown"),
            "reason": result.get("reason", ""),
            "is_priority": is_priority,
        }

        append_to_csv(output_row)

        if result.get("status") == "generated":
            generated += 1
        elif result.get("status") == "skip":
            skipped += 1
        elif result.get("status") == "error":
            failed += 1

    # ── Summary ──
    print(f"\n{'=' * 50}")
    print(f"  ✅ Generated:  {generated}")
    print(f"  ⏭️  Filtered:   {filtered}")
    print(f"  ⏭️  Skipped:    {skipped}")
    print(f"  ❌ Failed:     {failed}")
    print(f"  📄 Output:     {OUTPUT_FILE}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()