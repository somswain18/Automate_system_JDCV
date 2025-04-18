# utils.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Mailgun credentials
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_FROM_EMAIL = f"Elint AI <mailgun@{MAILGUN_DOMAIN}>"

# Generate feedback email body
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

# Send feedback email via Mailgun API
def send_feedback_email(recipient_email, subject, body):
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": MAILGUN_FROM_EMAIL,
                "to": recipient_email,
                "subject": subject,
                "text": body
            }
        )

        if response.status_code == 200:
            print(f"✅ Feedback email sent to {recipient_email}")
        else:
            print(f"❌ Failed to send email to {recipient_email}. Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception occurred while sending email: {e}")
