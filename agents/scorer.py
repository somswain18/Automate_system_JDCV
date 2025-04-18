import re

def extract_phone_number(text):
    # Regex pattern to match phone numbers starting with +91
    phone_pattern = r'(\+91[\s-]?\d{10})'  # Matches +91 followed by 10 digits
    matches = re.findall(phone_pattern, text)
    if matches:
        return matches[0]  # Return the first match (if multiple matches, pick the first)
    return "Not Found"

def extract_batch_year(text):
    match = re.findall(r'(20[0-3][0-9])', text)
    if match:
        years = sorted(set(match))
        return years[-1]  # assuming earliest is batch year
    return "Not Found"

def check_ai_experience(text):
    # AI-related keywords for matching experience
    ai_keywords = ['machine learning', 'deep learning', 'neural network', 'ai', 'ml', 'nlp', 'computer vision']
    
    # Look for patterns indicating years of experience
    experience_pattern = r'(\d+)\s*(year|yr|yrs)'  # Match years or year related words

    # Search for experience in the text
    experience_match = re.search(experience_pattern, text, re.IGNORECASE)
    
    # Check for AI-related keywords
    text = text.lower()
    ai_experience = "No Experience"
    
    for kw in ai_keywords:
        if kw in text:
            # If experience is mentioned, extract years
            if experience_match:
                ai_experience = f"{experience_match.group(1)} years"
            else:
                ai_experience = "No Experience"
            break
    
    return ai_experience


def score_formatting(text):
    length = len(text.split())
    if length < 150:
        return 1
    elif length < 300:
        return 2
    elif length < 600:
        return 3
    elif length < 1000:
        return 4
    else:
        return 5

def score_keywords(text, keywords):
    count = 0
    text = text.lower()
    for kw in keywords:
        if kw in text:
            count += 1
    return min(count * 2, 10)  # max 10 points

def calculate_resume_score(resume_text, jd_match_score):
    formatting_score = score_formatting(resume_text)          # 5 points
    keyword_score = score_keywords(resume_text, ['python', 'team', 'project', 'research'])  # 10 points
    match_score = (jd_match_score / 100) * 10                 # 10 points
    total = formatting_score + keyword_score + match_score
    return round(total, 2), {
        "formatting_score": formatting_score,
        "keyword_score": keyword_score,
        "match_score": round(match_score, 2)
    }

def evaluate_resume(resume_text, jd_match_score):
    phone_number = extract_phone_number(resume_text)
    batch_year = extract_batch_year(resume_text)
    ai_exp = check_ai_experience(resume_text)
    total_score, breakdown = calculate_resume_score(resume_text, jd_match_score)
    return {
        "phone_number": phone_number,
        "batch_year": batch_year,
        "ai_experience": ai_exp,
        "resume_score": total_score,
        "breakdown": breakdown
    }
