import os
from dotenv import load_dotenv
from agents.emailer import send_feedback_email, generate_feedback_email
from agents.db import load_db  # This should return the database as a list of dicts

# Load environment variables
load_dotenv()

sender_email = os.getenv("GMAIL_EMAIL")
sender_password = os.getenv("GMAIL_PASSWORD")

def send_feedback_to_candidate(candidate):
    subject, body = generate_feedback_email(
        candidate_name=candidate["Masked Name"],  # Adjusted to the correct key
        breakdown=candidate["breakdown"],  # Assuming breakdown exists
        batch_year=candidate["Batch Year"],  # Adjusted to the correct key
        ai_exp=candidate["AI Experience"]  # Assuming this exists as well
    )
    
    send_feedback_email(
        sender_email,
        sender_password,
        candidate["Masked Email"],  # Adjusted to the correct key
        subject,
        body
    )

def main():
    """
    Main function that loads the database, lists the candidates, 
    and sends feedback to the selected candidates.
    """
    # Load the data from your database (scored_resumes.xlsx or similar)
    records = load_db()

    # Display candidate list
    print("\nAvailable Candidates:")
    for idx, record in enumerate(records):
        # Ensure you are using the correct keys from your DB
        print(f"{idx+1}. {record['Masked Name']} - {record['Masked Email']}")  # Change keys here as well

    # Ask user which one(s) to send feedback to
    choices = input("\nEnter the number(s) of candidates to send feedback to (comma-separated): ")
    selected_indexes = [int(i.strip()) - 1 for i in choices.split(",")]

    for idx in selected_indexes:
        candidate = records[idx]
        # Log the candidate being processed
        print(f"\n📤 Sending feedback to {candidate['Masked Name']} ({candidate['Masked Email']})...")
        send_feedback_to_candidate(candidate)

if __name__ == "__main__":
    main()
