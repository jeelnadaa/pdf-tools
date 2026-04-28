from flask import Blueprint, render_template, request, jsonify
import fitz
import os
import uuid
from .utils import save_upload, get_processed_path
from PIL import Image

image_to_pdf_bp = Blueprint('image_to_pdf', __name__)

@image_to_pdf_bp.route('/', methods=['GET', 'POST'])
def image_to_pdf():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='image-to-pdf', title='Image to PDF', 
                               desc='Convert JPG, PNG or TIFF images to PDF documents.',
                               multiple=True, accept='image/*')
    
    files = request.files.getlist('files')
    if not files or not files[0].filename:
        return jsonify({"error": "No files uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'images_converted.pdf'
    
    try:
        doc = fitz.open()
        for file in files:
            file_path = save_upload(file, job_id)
            
            img = fitz.open(file_path)
            rect = img[0].rect
            pdfbytes = img.convert_to_pdf()
            img.close()
            
            imgPDF = fitz.open("pdf", pdfbytes)
            doc.insert_pdf(imgPDF)
            imgPDF.close()
            
        output_path = get_processed_path(filename, job_id)
        doc.save(output_path)
        doc.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
