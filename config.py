
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application. Please configure it in .env file.")
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Secure Session Cookies Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URI = "memory://"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Firebase Config
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', os.path.join(basedir, 'firebase-credentials.json'))

    # ImgBB Config
    IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')
