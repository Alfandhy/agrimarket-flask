
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_very_secret_replace_in_prod')
    # Default to SQLite if not set, but prefer Postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:1q2w3e@localhost/marketplace')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URI = "memory://"
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
