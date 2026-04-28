from flask import Blueprint, render_template, request, jsonify
import os
import uuid
from .utils import save_upload, get_processed_path
from pdf2docx import Converter

pdf_to_word_bp = Blueprint('pdf_to_word', __name__)

@pdf_to_word_bp.route('/', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='pdf-to-word', title='PDF to Word', 
                               desc='Convert your PDF to WORD documents with incredible accuracy.',
                               multiple=False, accept='.pdf')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'converted.docx'
    
    try:
        file_path = save_upload(file, job_id)
        output_path = get_processed_path(filename, job_id)
        
        cv = Converter(file_path)
        cv.convert(output_path)
        cv.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
