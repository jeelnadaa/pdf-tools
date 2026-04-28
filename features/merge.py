from flask import Blueprint, render_template, request, jsonify
import fitz # PyMuPDF
import os
import uuid
from .utils import save_upload, get_processed_path

merge_bp = Blueprint('merge', __name__)

@merge_bp.route('/', methods=['GET', 'POST'])
def merge():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='merge', title='Merge PDF', 
                               desc='Combine multiple PDFs into one unified document.',
                               multiple=True, accept='.pdf')
    
    files = request.files.getlist('files')
    if not files or not files[0].filename:
        return jsonify({"error": "No files uploaded"}), 400
    
    job_id = str(uuid.uuid4())
    filename = 'merged.pdf'
    
    try:
        merged_pdf = fitz.open()
        for file in files:
            file_path = save_upload(file, job_id)
            doc = fitz.open(file_path)
            merged_pdf.insert_pdf(doc)
            doc.close()
            
        output_path = get_processed_path(filename, job_id)
        merged_pdf.save(output_path)
        merged_pdf.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
