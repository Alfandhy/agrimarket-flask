
import os
import uuid
import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename

def init_cloudinary(app):
    if app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET']
        )

def upload_image(file_obj, folder="uploads"):
    """
    Uploads an image to Cloudinary (if configured) or Local Storage.
    Returns the filename (local) or public_url (cloudinary).
    """
    if not file_obj or file_obj.filename == '':
        return None

    # Check safe extension
    filename = secure_filename(file_obj.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext[1:] not in current_app.config['ALLOWED_EXTENSIONS']:
        return None

    # Use Cloudinary if configured
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file_obj, 
                folder=f"agrimarket/{folder}",
                public_id=f"{uuid.uuid4().hex}" # Avoid collision
            )
            return result.get('secure_url')
        except Exception as e:
            print(f"Cloudinary Upload Error: {e}")
            return None # Fail safely
            
    else:
        # Fallback to Local Storage
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure dir exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        file_obj.save(save_path)
        return unique_filename

def delete_image(filename_or_url):
    """
    Deletes image from Cloudinary or Local Storage.
    """
    if not filename_or_url: return

    if "cloudinary.com" in filename_or_url:
        # Cloudinary URL format: .../ver123/agrimarket/uploads/public_id.jpg
        # We need to extract public_id
        try:
            # Very basic extraction logic
            parts = filename_or_url.split('/')
            
            # Find the part after version number (usually starts with v1...) or just the end
            # Assuming standard structure: .../upload/v12345/agrimarket/folder/id.ext
            # We need 'agrimarket/folder/id' without extension
            
            # Simplified: take last 2 parts if folder is used
            public_id_with_ext = "/".join(parts[-2:]) 
            public_id = os.path.splitext(public_id_with_ext)[0]
            
            # Correct logic: split by 'upload/' and take the right side, remove version if present
            # This is complex, so for MVP we just attempt deletion if we can guess the ID
            # Better architecture stores the public_id separately. 
            
            # REVISION: Let's store the full URL. deleting by URL via API is tricky without ID.
            # Ideally we store public_id. But our DB schema has 'image_filename'.
            # If we store URL there, we can't easily guess ID.
            # Strategy: Extract everything after 'agrimarket/'
            
            if 'agrimarket/' in filename_or_url:
                start_idx = filename_or_url.find('agrimarket/')
                public_id = os.path.splitext(filename_or_url[start_idx:])[0]
                cloudinary.uploader.destroy(public_id)
                
        except Exception as e:
            print(f"Cloudinary Delete Error: {e}")
            
    else:
        # Local file
        try:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename_or_url)
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
