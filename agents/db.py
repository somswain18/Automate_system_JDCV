import os
import pandas as pd

DB_PATH = "output/resume_db.xlsx"

def init_db():
    if not os.path.exists("output"):
        os.makedirs("output")

    if not os.path.isfile(DB_PATH):
        # Create the DataFrame with an additional 'Phone Number' column
        df = pd.DataFrame(columns=[
            "Masked Name", "Masked Email", "Phone Number", "Batch Year",
            "AI Experience", "JD-CV Match Score"
        ])
        df.to_excel(DB_PATH, index=False)

def append_to_db(data):
    # Read the existing data from the Excel file
    df = pd.read_excel(DB_PATH)

    # Create a new row based on the extracted data
    new_row = {
        "Masked Name": data["name"],
        "Masked Email": data["email"],
        "Phone Number": data["phone_number"],
        "Batch Year": data["batch_year"],
        "AI Experience": data["ai_experience"],
        "JD-CV Match Score": data["jd_cv_score"]
    }

    # Append the new row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save it back
    df.to_excel(DB_PATH, index=False)

    print(f"✅ Data written to DB: {new_row}")

def load_db(filepath=DB_PATH):
    df = pd.read_excel(filepath)
    records = df.to_dict(orient="records")
    print(records)
    return records
