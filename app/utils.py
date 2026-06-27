
import os
import uuid
import base64
import requests
from flask import current_app
from werkzeug.utils import secure_filename

def init_cloudinary(app):
    # Deprecated: Kept for compatibility if imported somewhere
    pass

def upload_image(file_obj, folder="uploads"):
    """
    Uploads an image to ImgBB (if configured) or Local Storage.
    Returns the filename (local) or public_url (ImgBB).
    """
    if not file_obj or file_obj.filename == '':
        return None

    # Check safe extension
    filename = secure_filename(file_obj.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext[1:] not in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp'}):
        return None

    api_key = current_app.config.get('IMGBB_API_KEY')
    if api_key:
        try:
            print("DEBUG: Attempting ImgBB upload...")
            url = f"https://api.imgbb.com/1/upload?key={api_key}"
            image_b64 = base64.b64encode(file_obj.read()).decode('utf-8')
            payload = {'image': image_b64}
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                res_data = response.json()
                print("DEBUG: ImgBB upload success. URL:", res_data['data']['url'])
                return res_data['data']['url']
            else:
                print(f"ImgBB Upload Error: {response.text}")
                return None
        except Exception as e:
            print(f"ImgBB Upload Exception: {e}")
            return None
            
    else:
        # Fallback to Local Storage
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        file_obj.seek(0)
        file_obj.save(save_path)
        return unique_filename

def delete_image(filename_or_url):
    """
    Deletes image from Local Storage. (ImgBB delete requires delete_url which we don't store)
    """
    if not filename_or_url: return

    if filename_or_url.startswith('http'):
        # Usually external hosted images (like ImgBB or Cloudinary). 
        # Without delete_url we just let it be.
        pass
    else:
        # Local file
        try:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename_or_url)
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
