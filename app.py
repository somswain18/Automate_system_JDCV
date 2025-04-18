import os
import imaplib
import email
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form
from typing import List
from utils import generate_feedback_email, send_feedback_email
from agents.parser import parse_resume
from agents.matcher import get_text_from_file, calculate_jd_cv_match
from agents.scorer import evaluate_resume
from agents.db import append_to_db, load_db  # Use load_db for retrieving records

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)
EMAIL_FOLDER = "downloads/emails"
os.makedirs(EMAIL_FOLDER, exist_ok=True)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the CV Evaluation System!"}

@app.post("/evaluate/")
async def evaluate_resume_files(
    background_tasks: BackgroundTasks,
    resumes: List[UploadFile] = File(...),  # This will now receive all files within the uploaded folder
    job_description: UploadFile = File(...)
):
    try:
        # Save Job Description file
        jd_path = f"temp_{job_description.filename}"
        with open(jd_path, "wb") as f:
            f.write(await job_description.read())
        jd_text = get_text_from_file(jd_path)

        results = []

        for resume in resumes:
            save_path = os.path.join(UPLOAD_DIR, resume.filename)
            with open(save_path, "wb") as f:
                f.write(await resume.read())
            print(f"📄 Saved resume to: {save_path}")

            # Parse and evaluate each resume
            resume_data = parse_resume(save_path)
            match_score = calculate_jd_cv_match(jd_text, resume_data["raw_text"])
            evaluation = evaluate_resume(resume_data["raw_text"], match_score)

            final_record = {
                "filename": resume.filename,
                "name": resume_data["name"],
                "email": resume_data["email"],
                "phone_number": evaluation["phone_number"],
                "jd_cv_score": match_score,
                "batch_year": evaluation["batch_year"],
                "ai_experience": evaluation["ai_experience"],
            }
            append_to_db(final_record)  # Save evaluation to the DB

            results.append(final_record)

        return {
            "message": f"Evaluation complete for {len(results)} resumes.",
            "results": results  # List of resumes with JD-CV score
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/send-feedback/")
async def send_feedback_to_selected(
    background_tasks: BackgroundTasks,
    selected_resumes: List[str] = Form(...)  # List of resume filenames selected for feedback
):
    try:
        # Load all records from DB using load_db
        all_records = load_db()  
        feedback_sent = []

        # Filter selected records based on filenames
        selected_records = [record for record in all_records if record["filename"] in selected_resumes]

        for record in selected_records:
            subject, body = generate_feedback_email(
                candidate_name=record["name"],
                jd_cv_score=record["jd_cv_score"],
                batch_year=record["batch_year"],
                ai_exp=record["ai_experience"]
            )
            # Trigger feedback email asynchronously
            background_tasks.add_task(
                send_feedback_email,
                os.getenv("GMAIL_EMAIL"),
                os.getenv("GMAIL_PASSWORD"),
                record["email"],
                subject,
                body
            )
            feedback_sent.append(record["email"])

        return {
            "message": f"Feedback email triggered for {len(feedback_sent)} candidate(s).",
            "emails": feedback_sent
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/fetch-unread-emails/")
async def fetch_unread_emails(
    email_address: str = Form(...),  # Gmail email address
    password: str = Form(...),  # Gmail password
):
    try:
        # Connect to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, password)
        
        # Select the mailbox you want to read from
        mail.select("inbox")

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')

        if status != "OK":
            raise Exception("No unread messages found")

        email_ids = messages[0].split()
        fetched_emails = []

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    from_email = msg["from"]
                    print(f"📧 Fetching email from: {from_email}, Subject: {subject}")

                    # Save attachments to folder
                    for part in msg.walk():
                        if part.get_content_type() == 'application/octet-stream':  # Check for attachments
                            filename = part.get_filename()
                            if filename:
                                file_path = os.path.join(EMAIL_FOLDER, filename)
                                with open(file_path, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                fetched_emails.append(file_path)

        mail.logout()

        return {
            "message": f"Fetched {len(fetched_emails)} unread emails.",
            "files": fetched_emails  # List of saved attachment files
        }

    except Exception as e:
        return {"error": str(e)}
