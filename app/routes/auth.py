
import os
import re
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User
from app.extensions import limiter

bp = Blueprint('auth', __name__)

def validate_password_strength(password):
    if len(password) < 8: return False, "Password minimal 8 karakter."
    if not re.search(r"[a-zA-Z]", password): return False, "Password harus mengandung huruf."
    if not re.search(r"\d", password): return False, "Password harus mengandung angka."
    return True, ""

def format_whatsapp(number):
    """Normalize WhatsApp number to 62xxx format."""
    clean = re.sub(r'\D', '', number) 
    if clean.startswith('0'): return '62' + clean[1:]
    if not clean.startswith('62'): return '62' + clean
    return clean

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") 
def login():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Username atau password salah.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST']) 
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated: return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        wa = request.form.get('whatsapp_number')
        
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            flash(msg, 'warning')
            return render_template('register.html')
            
        if User.get_by_username(username):
            flash('Username sudah digunakan.', 'danger')
        else:
            new_user = User(username=username, role='penjual', whatsapp_number=format_whatsapp(wa))
            new_user.set_password(password)
            new_user.save()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('register.html')
