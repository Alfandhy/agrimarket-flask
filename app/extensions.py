
import firebase_admin
from firebase_admin import credentials, firestore
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

firebase_db = None
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def init_firebase(app):
    global firebase_db
    try:
        # Check if already initialized to avoid errors during reloads
        if not firebase_admin._apps:
            cred_path = app.config.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            import os
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                print(f"Warning: Firebase credentials not found at {cred_path}")
                return
        firebase_db = firestore.client()
    except Exception as e:
        print(f"Failed to initialize Firebase: {e}")
