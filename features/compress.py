from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import uuid
from .utils import save_upload, get_processed_path

compress_bp = Blueprint('compress', __name__)

@compress_bp.route('/', methods=['GET', 'POST'])
def compress():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='compress', title='Compress PDF', 
                               desc='Reduce the file size of your PDF while maintaining quality.',
                               multiple=False, accept='.pdf')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'compressed.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        output_path = get_processed_path(filename, job_id)
        
        # Optimize the PDF to reduce size
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
