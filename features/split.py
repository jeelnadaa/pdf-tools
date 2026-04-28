from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import zipfile
import uuid
from .utils import save_upload, get_processed_path

split_bp = Blueprint('split', __name__)

@split_bp.route('/', methods=['GET', 'POST'])
def split():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='split', title='Split PDF', 
                               desc='Separate one page or a whole set for easy conversion.',
                               multiple=False, accept='.pdf')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'split_pages.zip'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        
        zip_path = get_processed_path(filename, job_id)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i in range(len(doc)):
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                page_path = get_processed_path(f'page_{i+1}.pdf', job_id)
                new_doc.save(page_path)
                new_doc.close()
                zipf.write(page_path, f'page_{i+1}.pdf')
        
        doc.close()
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
