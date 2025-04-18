import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from agents.parser import parse_resume
from agents.matcher import get_text_from_file, calculate_jd_cv_match
from agents.scorer import evaluate_resume
from agents.db import append_to_db
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch the email credentials
sender_email = os.getenv("GMAIL_EMAIL")  # Replace with your email
sender_password = os.getenv("GMAIL_PASSWORD")  # Replace with your email password


# Load environment variables from .env
load_dotenv()

# Fetch the email credentials
sender_email = os.getenv("GMAIL_EMAIL")
sender_password = os.getenv("GMAIL_PASSWORD")

# ✅ Add this function to generate the feedback email body
# ✅ Add this function to generate the feedback email body
def generate_feedback_email(candidate_name, jd_cv_score, batch_year=None, ai_exp=None):
    subject = "Resume Feedback from Elint AI"
    match_score_percent = round(jd_cv_score * 1, 2)

    if jd_cv_score < 40:
        eligibility_message = "You are not eligible for the next round."
    else:
        eligibility_message = "Congratulations! You are eligible for the next round."

    body = f"""
Dear {candidate_name},

Thank you for applying.

Based on our evaluation:
- JD Match Score: {match_score_percent}%

Batch Year: {batch_year}
AI Experience: {ai_exp}

 {eligibility_message}

We appreciate your interest and will get back to you soon.

Regards,  
Elint AI Team
"""
    return subject, body

# ✅ Add this function to send the feedback email
def send_feedback_email(sender_email, sender_password, recipient_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"✅ Feedback email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def process_resume(resume_path, jd_path):
    print(f"Processing resume: {resume_path}")

    # Step 1: Parse Resume
    resume_data = parse_resume(resume_path)
    print(f"Parsed Resume Data: {resume_data}")

    # Step 2: Get JD Text
    jd_text = get_text_from_file(jd_path)
    print(f"Job Description Text: {jd_text[:100]}...")

    # Step 3: Calculate JD-CV Match Score
    match_score = calculate_jd_cv_match(jd_text, resume_data["raw_text"])
    print(f"JD-CV Match Score: {match_score}%")

    # Step 4: Score the Resume
    evaluation = evaluate_resume(resume_data["raw_text"], match_score)
    print(f"Evaluation: {evaluation}")

    # Step 5: Log Data into Excel (or your database)
    final_record = {
        "name": resume_data["name"],
        "email": resume_data["email"],
        "phone_number": evaluation["phone_number"],
        "jd_cv_score": match_score,
        "batch_year": evaluation["batch_year"],
        "ai_experience": evaluation["ai_experience"],
    }

    # Append the final record to your database (Excel file)
    print(f"Appending to DB: {final_record}")
    append_to_db(final_record)

    # After confirming the data is appended to the database, you can send the feedback email
    if resume_data["email"]:
        # Step 6: Generate and Send Feedback Email
        subject, body = generate_feedback_email(
            candidate_name=resume_data["name"],
            jd_cv_score=match_score,
            batch_year=evaluation["batch_year"],
            ai_exp=evaluation["ai_experience"]
        )

        send_feedback_email(sender_email, sender_password, resume_data["email"], subject, body)
    else:
        print("⚠️ No email found for this candidate. Skipping feedback email.")
