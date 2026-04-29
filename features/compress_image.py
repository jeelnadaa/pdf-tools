from flask import Blueprint, render_template, request, jsonify, current_app
import os
import uuid
import io
from .utils import save_upload, get_processed_path
from PIL import Image

compress_image_bp = Blueprint('compress_image', __name__)

def get_quality_value(preset, custom_val):
    if preset == 'low': return 85
    elif preset == 'medium': return 60
    elif preset == 'high': return 30
    elif preset == 'custom':
        try:
            return int(custom_val)
        except:
            return 50
    return 60

@compress_image_bp.route('/', methods=['GET'])
def compress_image():
    return render_template('tool.html', tool_id='compress-image', title='Compress Image', 
                           desc='Reduce image file size with exact quality control.',
                           multiple=False, accept='image/*')

@compress_image_bp.route('/draft', methods=['POST'])
def draft():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded"}), 400
        
    job_id = str(uuid.uuid4())
    try:
        save_upload(file, job_id)
        return jsonify({"status": "success", "job_id": job_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@compress_image_bp.route('/estimate/<job_id>', methods=['GET'])
def estimate(job_id):
    preset = request.args.get('preset', 'medium')
    custom_val = request.args.get('quality', 50)
    quality = get_quality_value(preset, custom_val)
    
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], job_id)
    if not os.path.exists(upload_dir):
        return jsonify({"error": "Draft not found"}), 404
        
    files = os.listdir(upload_dir)
    if not files:
        return jsonify({"error": "File not found"}), 404
        
    file_path = os.path.join(upload_dir, files[0])
    
    try:
        img = Image.open(file_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
        size_bytes = img_byte_arr.tell()
        
        return jsonify({
            "status": "success",
            "estimated_size": size_bytes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@compress_image_bp.route('/process/<job_id>', methods=['POST'])
def process(job_id):
    preset = request.form.get('quality_preset', 'medium')
    custom_val = request.form.get('quality_slider', 50)
    quality = get_quality_value(preset, custom_val)
    
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], job_id)
    if not os.path.exists(upload_dir):
        return jsonify({"error": "Draft not found"}), 404
        
    files = os.listdir(upload_dir)
    if not files:
        return jsonify({"error": "File not found"}), 404
        
    file_path = os.path.join(upload_dir, files[0])
    filename = 'compressed_' + os.path.splitext(files[0])[0] + '.jpg'
    output_path = get_processed_path(filename, job_id)
    
    try:
        img = Image.open(file_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(output_path, format='JPEG', quality=quality, optimize=True)
        
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
