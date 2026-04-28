from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import uuid
from .utils import save_upload, get_processed_path

flatten_bp = Blueprint('flatten', __name__)

@flatten_bp.route('/', methods=['GET', 'POST'])
def flatten():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='flatten', title='Flatten PDF', 
                               desc='Render pages as images, making text unselectable.',
                               multiple=False, accept='.pdf')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'flattened.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        new_doc = fitz.open()
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=150)
            
            img_doc = fitz.open("jpeg", pix.tobytes("jpeg"))
            pdfbytes = img_doc.convert_to_pdf()
            img_doc.close()
            
            img_pdf = fitz.open("pdf", pdfbytes)
            new_doc.insert_pdf(img_pdf)
            img_pdf.close()
            
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
