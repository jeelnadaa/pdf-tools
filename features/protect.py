from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import uuid
from .utils import save_upload, get_processed_path

protect_bp = Blueprint('protect', __name__)

@protect_bp.route('/', methods=['GET', 'POST'])
def protect():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='protect', title='Protect PDF', 
                               desc='Encrypt your PDF with a password to keep sensitive data safe.',
                               multiple=False, accept='.pdf', needs_password=True)
    
    file = request.files.get('file')
    password = request.form.get('password', '')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'protected.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        output_path = get_processed_path(filename, job_id)
        doc.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=password, owner_pw=password)
        doc.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
