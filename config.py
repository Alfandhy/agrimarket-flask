
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_very_secret_replace_in_prod')
    # Railway/Heroku provides 'postgres://' which is deprecated in SQLAlchemy 1.4+
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Fallback to SQLite if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = db_url or ('sqlite:///' + os.path.join(basedir, 'instance', 'marketplace.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URI = "memory://"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Cloudinary Config
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
