from app import app, db
import os

if __name__ == '__main__':
    # Ensure upload folder exists (relative to where run.py is)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    app.run(debug=True)
