from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import uuid
from .utils import save_upload, get_processed_path

extract_bp = Blueprint('extract', __name__)

@extract_bp.route('/', methods=['GET', 'POST'])
def extract():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='extract', title='Extract Pages', 
                               desc='Get a new document containing only the desired pages.',
                               multiple=False, accept='.pdf', needs_pages=True)
    
    file = request.files.get('file')
    pages_str = request.form.get('pages', '')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'extracted.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        new_doc = fitz.open()
        
        page_nums = set()
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_nums.update(range(start - 1, end))
            elif part.isdigit():
                page_nums.add(int(part) - 1)
                
        for p in sorted(page_nums):
            if 0 <= p < len(doc):
                new_doc.insert_pdf(doc, from_page=p, to_page=p)
                
        output_path = get_processed_path(filename, job_id)
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
