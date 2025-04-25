import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Load environment variables from .env
load_dotenv()

# Configuration for FastAPI-Mail
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS") == "True",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS") == "True"
)

# ✅ Function to generate feedback content
def generate_feedback_email(candidate_name, jd_cv_score, batch_year=None, ai_exp=None):
    subject = "Resume Feedback from Elint AI"
    match_score_percent = round(jd_cv_score * 1, 2)

    if jd_cv_score < 40:
        eligibility_message = "You are not eligible for the next round."
    else:
        eligibility_message = "Congratulations! You are eligible for the next round."

    body = f"""
    Dear {candidate_name},<br><br>

    Thank you for applying.<br><br>

    Based on our evaluation:<br>
    - JD Match Score: {match_score_percent}%<br>
    - Batch Year: {batch_year}<br>
    - AI Experience: {ai_exp}<br><br>

    <b>{eligibility_message}</b><br><br>

    We appreciate your interest and will get back to you soon.<br><br>

    Regards,<br>
    Elint AI Team
    """
    return subject, body

# ✅ Function to send the email asynchronously
async def send_feedback_email(recipient_email, subject, body):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        body=body,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    print(f"✅ Email sent to {recipient_email}")
