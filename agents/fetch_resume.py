import imaplib
import email
from email.header import decode_header
import os

# Credentials from environment variables
from dotenv import load_dotenv
load_dotenv()

EMAIL = os.getenv("GMAIL_EMAIL")
PASSWORD = os.getenv("GMAIL_PASSWORD")

# Folder to save resumes
SAVE_FOLDER = "resumes"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def clean_filename(name):
    return "".join(c if c.isalnum() or c in (' ', '.', '_') else "_" for c in name)

def fetch_resumes():
    try:
        # Connect to Gmail IMAP server
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
        imap.select("inbox")

        # Search unread emails
        status, messages = imap.search(None, '(ALL)')
        if status != "OK":
            print("No new emails found.")
            return

        for num in messages[0].split():
            status, msg_data = imap.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_header(msg["Subject"])[0][0]
            print(f"\n📥 Processing Email: {subject}")

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                if filename:
                    filename = decode_header(filename)[0][0]
                    filename = filename.decode() if isinstance(filename, bytes) else filename
                    filename = clean_filename(filename)

                    if filename.lower().endswith((".pdf", ".docx")):
                        filepath = os.path.join(SAVE_FOLDER, filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"✅ Saved resume: {filename}")

            # Mark email as read
            imap.store(num, '+FLAGS', '\\Seen')

        imap.logout()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_resumes()
