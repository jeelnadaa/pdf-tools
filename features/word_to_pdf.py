from flask import Blueprint, render_template, request, jsonify
import os
import uuid
from .utils import save_upload, get_processed_path
from docx2pdf import convert

word_to_pdf_bp = Blueprint('word_to_pdf', __name__)

@word_to_pdf_bp.route('/', methods=['GET', 'POST'])
def word_to_pdf():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='word-to-pdf', title='Word to PDF', 
                               desc='Make DOC and DOCX files easy to read by converting them to PDF.',
                               multiple=False, accept='.docx,.doc')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'converted.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        output_path = get_processed_path(filename, job_id)
        
        convert(file_path, output_path)
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e) + " (Note: This feature requires Microsoft Word to be installed on the server.)"}), 500
