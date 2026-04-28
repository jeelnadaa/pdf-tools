from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import zipfile
import uuid
from .utils import save_upload, get_processed_path

pdf_to_image_bp = Blueprint('pdf_to_image', __name__)

@pdf_to_image_bp.route('/', methods=['GET', 'POST'])
def pdf_to_image():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='pdf-to-image', title='PDF to Image', 
                               desc='Convert each PDF page into a JPG or extract all images.',
                               multiple=False, accept='.pdf')
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'images.zip'
    
    try:
        file_path = save_upload(file, job_id)
        doc = fitz.open(file_path)
        
        zip_path = get_processed_path(filename, job_id)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=300)
                img_path = get_processed_path(f'page_{i+1}.jpg', job_id)
                pix.save(img_path)
                zipf.write(img_path, f'page_{i+1}.jpg')
                
        doc.close()
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
