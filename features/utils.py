import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

def save_upload(file, job_id):
    if not file: return None
    filename = secure_filename(file.filename)
    job_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], job_id)
    os.makedirs(job_folder, exist_ok=True)
    save_path = os.path.join(job_folder, filename)
    file.save(save_path)
    return save_path

def get_processed_path(filename, job_id):
    job_folder = os.path.join(current_app.config['PROCESSED_FOLDER'], job_id)
    os.makedirs(job_folder, exist_ok=True)
    return os.path.join(job_folder, filename)
