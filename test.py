import os
import imaplib
import email
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from typing import List
from utils import generate_feedback_email, send_feedback_email
from agents.parser import parse_resume
from agents.matcher import get_text_from_file, calculate_jd_cv_match
from agents.scorer import evaluate_resume
from agents.db import append_to_db, load_db
from dotenv import load_dotenv
load_dotenv()

UPLOAD_DIR = "/home/som/Music/automated_cv_system_gp/automated_cv_system/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)
EMAIL_FOLDER = "/home/som/Music/automated_cv_system_gp/automated_cv_system/downloads"
os.makedirs(EMAIL_FOLDER, exist_ok=True)

app = FastAPI()

@app.post("/auto-process/")
async def fetch_and_evaluate_resumes(
    gmail_id: str = Form(...),
    gmail_password: str = Form(...),
    job_description: UploadFile = File(...)
):
    try:
        # Read JD
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

                    # for p in msg.walk():
                    #     if p.get_content_type() == 'application/octet-stream':
                    #         filename = p.get_filename()
                    #         if filename:
                    #             file_path = os.path.join(UPLOAD_DIR, filename)
                    #             with open(file_path, "wb") as f:
                    #                 f.write(p.get_payload(decode=True))
                    #             saved_files.append(file_path)
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

@app.post("/send-feedback/")
def send_feedback_to_candidates(
    background_tasks: BackgroundTasks,
    gmail_id: str = Form(...),
    gmail_password: str = Form(...)
):
    try:
        db = load_db()
        if not db:
            return {"message": "No candidates found in DB."}

        for row in db:
            name = row.get("name")
            email_id = row.get("email")
            jd_cv_score = row.get("jd_cv_score")
            batch_year = row.get("batch_year")
            ai_exp = row.get("ai_experience")

            subject, body = generate_feedback_email(
                candidate_name=name,
                jd_cv_score=jd_cv_score,
                batch_year=batch_year,
                ai_exp=ai_exp
            )
            background_tasks.add_task(
                send_feedback_email,
                gmail_id,
                gmail_password,
                email_id,
                subject,
                body
            )

        return {"message": f"Feedback emails scheduled for {len(db)} candidates."}

    except Exception as e:
        return {"error": str(e)}
