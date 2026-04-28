import os
import shutil
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import time
from dotenv import load_dotenv

load_dotenv()

# Import blueprints
from features.merge import merge_bp
from features.split import split_bp
from features.extract import extract_bp
from features.protect import protect_bp
from features.pdf_to_image import pdf_to_image_bp
from features.image_to_pdf import image_to_pdf_bp
from features.pdf_to_word import pdf_to_word_bp
from features.word_to_pdf import word_to_pdf_bp
from features.flatten import flatten_bp
from features.ocr import ocr_bp

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.abspath('uploads')
app.config['PROCESSED_FOLDER'] = os.path.abspath('processed')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Check if Tesseract is installed
def is_tesseract_installed():
    try:
        subprocess.run(['tesseract', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True
    except FileNotFoundError:
        return False

# Pass to all templates
@app.context_processor
def inject_tesseract_status():
    return dict(tesseract_installed=is_tesseract_installed())

# Register blueprints
app.register_blueprint(merge_bp, url_prefix='/merge')
app.register_blueprint(split_bp, url_prefix='/split')
app.register_blueprint(extract_bp, url_prefix='/extract')
app.register_blueprint(protect_bp, url_prefix='/protect')
app.register_blueprint(pdf_to_image_bp, url_prefix='/pdf-to-image')
app.register_blueprint(image_to_pdf_bp, url_prefix='/image-to-pdf')
app.register_blueprint(pdf_to_word_bp, url_prefix='/pdf-to-word')
app.register_blueprint(word_to_pdf_bp, url_prefix='/word-to-pdf')
app.register_blueprint(flatten_bp, url_prefix='/flatten')
app.register_blueprint(ocr_bp, url_prefix='/ocr')

# Tools definitions
TOOLS = [
    {'id': 'merge', 'name': 'Merge PDF', 'desc': 'Combine multiple PDFs into one unified document.', 'icon': 'merge-icon', 'route': '/merge'},
    {'id': 'split', 'name': 'Split PDF', 'desc': 'Separate one page or a whole set for easy conversion.', 'icon': 'split-icon', 'route': '/split'},
    {'id': 'extract', 'name': 'Extract Pages', 'desc': 'Get a new document containing only the desired pages.', 'icon': 'extract-icon', 'route': '/extract'},
    {'id': 'protect', 'name': 'Protect PDF', 'desc': 'Encrypt your PDF with a password to keep sensitive data safe.', 'icon': 'protect-icon', 'route': '/protect'},
    {'id': 'pdf-to-image', 'name': 'PDF to Image', 'desc': 'Convert each PDF page into a JPG or extract all images.', 'icon': 'pdf-to-image-icon', 'route': '/pdf-to-image'},
    {'id': 'image-to-pdf', 'name': 'Image to PDF', 'desc': 'Convert JPG, PNG or TIFF images to PDF documents.', 'icon': 'image-to-pdf-icon', 'route': '/image-to-pdf'},
    {'id': 'pdf-to-word', 'name': 'PDF to Word', 'desc': 'Convert your PDF to WORD documents with incredible accuracy.', 'icon': 'pdf-to-word-icon', 'route': '/pdf-to-word'},
    {'id': 'word-to-pdf', 'name': 'Word to PDF', 'desc': 'Make DOC and DOCX files easy to read by converting them to PDF.', 'icon': 'word-to-pdf-icon', 'route': '/word-to-pdf'},
    {'id': 'flatten', 'name': 'Flatten PDF', 'desc': 'Render pages as images, making text unselectable.', 'icon': 'flatten-icon', 'route': '/flatten'},
    {'id': 'ocr', 'name': 'OCR PDF', 'desc': 'Make a scanned PDF searchable by creating a text layer.', 'icon': 'ocr-icon', 'route': '/ocr'},
]

@app.route('/')
def index():
    return render_template('index.html', tools=TOOLS)

# File Management Routes
@app.route('/download/<job_id>/<filename>')
def download_file(job_id, filename):
    safe_job_id = secure_filename(job_id)
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], safe_job_id, safe_filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=safe_filename)
    return "File not found", 404

@app.route('/delete/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    safe_job_id = secure_filename(job_id)
    up_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_job_id)
    proc_path = os.path.join(app.config['PROCESSED_FOLDER'], safe_job_id)
    
    deleted = False
    if os.path.exists(up_path):
        shutil.rmtree(up_path)
        deleted = True
    if os.path.exists(proc_path):
        shutil.rmtree(proc_path)
        deleted = True
        
    if deleted:
        return jsonify({"status": "success", "message": "Cache deleted"})
    return jsonify({"status": "error", "message": "Job not found"}), 404

@app.route('/admin/clear-all', methods=['POST'])
def clear_all():
    data = request.get_json()
    if not data or data.get('password') != os.getenv('ADMIN_PASSWORD'):
        return jsonify({"status": "error", "message": "Invalid admin password"}), 403

    for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (item_path, e))
    return jsonify({"status": "success", "message": "All cache cleared"})

if __name__ == '__main__':
    app.run(debug=True)
