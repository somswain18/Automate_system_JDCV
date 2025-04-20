# Automated CV Screening System

This FastAPI-based project automates the collection, evaluation, and feedback process of resumes received via Gmail. It parses resumes, compares them with a job description, scores them, stores results in a local DB, and optionally sends personalized feedback to candidates.

---

## 🚀 Features

- Connects to Gmail and fetches unread emails with resume attachments
- Supports resume parsing and scoring against a job description
- Stores candidate evaluations in a local JSON database
- Sends feedback emails to candidates using customizable templates

📁 Project Structure

Requirements

Install dependencies with:

```bash
pip install -r requirements.txt

Environment Variables
Use a .env file to store sensitive variables:
GMAIL_ID=your-email@gmail.com
GMAIL_PASSWORD=your-app-password

Running the App
uvicorn app1:app --reload
