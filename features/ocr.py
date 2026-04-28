from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
from .utils import save_upload, get_processed_path
import pytesseract
from pdf2image import convert_from_path

ocr_bp = Blueprint('ocr', __name__)

@ocr_bp.route('/', methods=['GET', 'POST'])
def ocr():
    if request.method == 'GET':
        return render_template('tool.html', tool_id='ocr', title='OCR PDF', 
                               desc='Make a scanned PDF searchable by creating a text layer.',
                               multiple=False, accept='.pdf', needs_ocr=True)
    
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    filename = 'ocr_searchable.pdf'
    
    try:
        file_path = save_upload(file, job_id)
        
        try:
            images = convert_from_path(file_path, dpi=300)
        except Exception as e:
            return jsonify({"error": "Failed to extract images from PDF. Ensure 'poppler' is installed on your system. " + str(e)}), 500

        output_path = get_processed_path(filename, job_id)
        
        pdf_pages = []
        for img in images:
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
            pdf_pages.append(pdf_bytes)
            
        import fitz
        merged_pdf = fitz.open()
        for pdf_bytes in pdf_pages:
            doc = fitz.open("pdf", pdf_bytes)
            merged_pdf.insert_pdf(doc)
            doc.close()
            
        merged_pdf.save(output_path)
        merged_pdf.close()
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
