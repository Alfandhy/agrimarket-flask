
from app import create_app, db
from app.models import User, Category
from datetime import datetime
import os

app = create_app()

def seed_data():
    """Initialize default data if not present."""
    with app.app_context():
        db.create_all()
        
        # Seed Admin
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', role='admin', whatsapp_number='6281234567890')
            admin.set_password('admin123')
            db.session.add(admin)
            print(">> Admin master created.")
        
        # Seed Categories
        target_cats = ['Produk Pertanian', 'Komoditas Pertanian', 'Buah-Buahan', 'Sayur-Sayuran', 'Makanan']
        for c_name in target_cats:
            if not Category.query.filter_by(name=c_name).first():
                db.session.add(Category(name=c_name))
        
        db.session.commit()

if __name__ == '__main__':
    # Ensure upload folder exists (relative to where run.py is)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    seed_data()
    app.run(debug=True)
