def generate_feedback_email(candidate):
    candidate_name = candidate.get("name")
    jd_cv_score = candidate.get("jd_cv_score", 0)
    jd_score_percent = round(jd_cv_score * 100, 2)
    batch_year = candidate.get("batch_year", "N/A")
    ai_exp = candidate.get("ai_experience", "N/A")

    if jd_cv_score < 40:
        eligibility_message = "You are not eligible for the next round. "
    else:
        eligibility_message = "Congratulations! You are eligible for the next round."

    email_body = f"""
Dear {candidate_name},

Thank you for applying.

Based on our evaluation:
- JD Match Score: {jd_score_percent}%

Batch Year: {batch_year}
AI Experience: {ai_exp}

We appreciate your interest and will get back to you soon.

Regards,
Elint AI Team
"""
    return email_body
