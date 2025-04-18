import os

def get_resume_files(resume_folder):
    files = []
    for file in os.listdir(resume_folder):
        if file.lower().endswith(('.pdf', '.docx')):
            files.append(os.path.join(resume_folder, file))
    return files

def get_jd_file(jd_folder):
    for file in os.listdir(jd_folder):
        if file.lower().endswith(('.pdf', '.docx', '.txt')):
            return os.path.join(jd_folder, file)
    return None
