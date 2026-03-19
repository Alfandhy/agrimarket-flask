
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
        return User.query.get(int(user_id))

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
