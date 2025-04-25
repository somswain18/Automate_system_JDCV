import os
import imaplib
import email
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List
import pandas as pd
from dotenv import load_dotenv
from utils import generate_feedback_email, send_feedback_email
from agents.parser import parse_resume
from agents.matcher import get_text_from_file, calculate_jd_cv_match
from agents.scorer import evaluate_resume
from agents.db import append_to_db, load_db

load_dotenv()

# Directories
UPLOAD_DIR = "/home/som/Music/automated_cv_system_gp/automated_cv_system/resumes"
EMAIL_FOLDER = "/home/som/Music/automated_cv_system_gp/automated_cv_system/downloads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EMAIL_FOLDER, exist_ok=True)

app = FastAPI()

# Load email mapping
def load_email_mapping():
    mapping_df = pd.read_csv("email_mapping.csv")
    return dict(zip(mapping_df['Masked Email'], mapping_df['Real Email']))

# Resume Analyzer Endpoint
@app.post("/resume_analyzer/")
async def fetch_and_evaluate_resumes(
    gmail_id: str = Form(...),
    gmail_password: str = Form(...),
    job_description: UploadFile = File(...)
):
    try:
        # Save JD temporarily
        jd_path = f"temp_{job_description.filename}"
        with open(jd_path, "wb") as f:
            f.write(await job_description.read())
        jd_text = get_text_from_file(jd_path)

        # Connect Gmail & fetch resumes
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_id, gmail_password)
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            raise Exception("No unread messages found")

        email_ids = messages[0].split()
        saved_files = []
        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    for p in msg.walk():
                        if p.get_content_disposition() == 'attachment':
                            filename = p.get_filename()
                            if filename:
                                file_path = os.path.join(UPLOAD_DIR, filename)
                                with open(file_path, "wb") as f:
                                    f.write(p.get_payload(decode=True))
                                saved_files.append(file_path)
        mail.logout()

        if not saved_files:
            return {"message": "No resumes found in unread emails."}

        results = []
        for resume_path in saved_files:
            filename = os.path.basename(resume_path)
            resume_data = parse_resume(resume_path)
            match_score = calculate_jd_cv_match(jd_text, resume_data["raw_text"])
            evaluation = evaluate_resume(resume_data["raw_text"], match_score)

            final_record = {
                "filename": filename,
                "name": resume_data["name"],
                "email": resume_data["email"],
                "phone_number": evaluation["phone_number"],
                "jd_cv_score": match_score,
                "batch_year": evaluation["batch_year"],
                "ai_experience": evaluation["ai_experience"],
            }
            append_to_db(final_record)
            results.append(final_record)

        return {
            "message": f"Processed {len(results)} resumes.",
            "results": results
        }

    except Exception as e:
        return {"error": str(e)}

# Send Feedback to Selected Candidates Endpoint
@app.post("/send-feedback/")
async def send_feedback_email(
    background_tasks: BackgroundTasks,
    sender_email: str = Form(...),
    password: str = Form(...),
    recipients: List[str] = Form(...)  # Accept multiple emails
):
    try:
        
        db = load_db()
        db = [row for row in db if row.get("Masked Email") and row.get("Masked Email") != "Not Found"]

        if not db:
            
            return JSONResponse(content={"message": "Database is empty!"}, status_code=404)
        # mapping_df = pd.read_csv("email_mapping.csv")
        # email_mapping= dict(zip(mapping_df['Masked Email'], mapping_df['Real Email']))

        # # email_mapping = load_email_mapping()
        # print("chirag",email_mapping)
        # real_emails = [email_mapping.get(email, email) for email in recipients]

        matched_candidates = []
        skipped_candidates = []

        # for row in db:
        #     email_id = row.get("Masked Email")
        #     if not email_id:
        #         skipped_candidates.append(row)  
        #         continue
           
        #     else:
        #         matched_candidates.append(row)
        print("📥 Recipients Sent:", recipients)
        print("📄 Emails in DB:", [row.get("Masked Email") for row in db])

        if len(recipients) == 1 and "," in recipients[0]:
            recipients = [e.strip() for e in recipients[0].split(",")]

        recipients_lower = [email.strip().lower() for email in recipients]


        for row in db:
            email_id = row.get("Masked Email")
            if email_id and email_id.strip().lower() in recipients_lower:
                matched_candidates.append(row)
            else:
                skipped_candidates.append(row)

        if not matched_candidates:
            return JSONResponse(content={"message": "No matching emails found in DB!"}, status_code=404)

        for candidate in matched_candidates:
            name = candidate.get("name", "")
            email_id = candidate.get("Masked Email", "")
            jd_cv_score = candidate.get("jd_cv_score", 0)
            batch_year = candidate.get("batch_year", "")
            ai_exp = candidate.get("ai_experience", "")

            subject, body = generate_feedback_email(
                candidate_name=name,
                jd_cv_score=jd_cv_score,
                batch_year=batch_year,
                ai_exp=ai_exp
            )
            
            background_tasks.add_task(
                send_feedback_email,
                sender_email,
                password,
                email_id,
                subject,
                body
            )

        return {
            "message": f"Feedback scheduled for {len(matched_candidates)} candidate(s).",
            "emails_sent": [c["Masked Email"] for c in matched_candidates],
            "skipped_due_to_missing_email": len(skipped_candidates)
        }

    except Exception as e:
        return {"error": str(e)}
