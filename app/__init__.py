
from flask import Flask, render_template, flash, redirect, url_for
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv() # Load env vars from .env if present

from config import Config
from app.extensions import login_manager, csrf, limiter, init_firebase
from app.models import User

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Trust reverse proxy for correct client IP parsing
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    app.config.from_object(config_class)
    
    # Register global functions for templates
    @app.context_processor
    def utility_processor():
        def get_image_url(filename):
            if not filename:
                return None
            if filename.startswith('http'):
                # Trik: Bypass blokir ISP (Internet Positif) menggunakan proxy gambar WordPress (Photon)
                if 'i.ibb.co' in filename:
                    return filename.replace('https://', 'https://i0.wp.com/')
                return filename
            return url_for('static', filename='uploads/' + filename)
        return dict(get_image_url=get_image_url)

    # Initialize extensions
    init_firebase(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

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

app = create_app()
