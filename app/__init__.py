
from flask import Flask, render_template, flash, redirect, url_for
from dotenv import load_dotenv

load_dotenv() # Load env vars from .env if present

from config import Config
from app.extensions import db, login_manager, csrf, limiter
from app.models import User

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        # Use session.get for SQLAlchemy 2.0 compatibility
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes import auth, admin, product, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(product.bp)
    app.register_blueprint(main.bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="<div class='text-center py-5'><h1>404</h1><p>Halaman tidak ditemukan.</p><a href='/' class='btn btn-primary'>Ke Beranda</a></div>"), 404

    @app.errorhandler(403)
    def forbidden(e):
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.index'))
        
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app

# Memberikan akses langsung untuk gunicorn jika menggunakan 'app:app'
from app.models import User, Category

def seed_data(app):
    try:
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(role='admin').first():
                admin = User(username='admin', role='admin', whatsapp_number='6281234567890')
                admin.set_password('admin123')
                db.session.add(admin)
            target_cats = ['Produk Pertanian', 'Komoditas Pertanian', 'Buah-Buahan', 'Sayur-Sayuran', 'Makanan']
            for c_name in target_cats:
                if not Category.query.filter_by(name=c_name).first():
                    db.session.add(Category(name=c_name))
            db.session.commit()
    except Exception as e:
        print(f"Warning: Seed data failed or already handled by another worker: {e}")
        # Dont crash the app/worker just because seed/create_all failed
        # Usually it means the DB is already set up or being set up by another worker.

app = create_app()
seed_data(app)
