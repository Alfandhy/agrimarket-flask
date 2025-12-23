
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from app.models import User, Category, Banner, Product, db
from app.routes.auth import validate_password_strength, format_whatsapp # Reuse helpers

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin': abort(403)
    users = User.query.options(joinedload(User.products)).all()
    return render_template('manage_users.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin': abort(403)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'penjual')
        wa = request.form.get('whatsapp_number')
        
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            flash(msg, 'warning')
            return render_template('create_user.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.', 'danger')
        else:
            new_user = User(username=username, role=role, whatsapp_number=format_whatsapp(wa))
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Akun {role} "{username}" berhasil dibuat!', 'success')
            return redirect(url_for('admin.manage_users'))
    return render_template('create_user.html')

@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin' and current_user.id != id: abort(403)
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        if current_user.role == 'admin':
            user.username = request.form.get('username')
        
        user.whatsapp_number = format_whatsapp(request.form.get('whatsapp_number'))
        
        new_pass = request.form.get('password')
        if new_pass:
            is_valid, msg = validate_password_strength(new_pass)
            if not is_valid:
                flash(msg, 'warning')
                return redirect(url_for('admin.edit_user', id=id))
            user.set_password(new_pass)
            flash('Password diperbarui.', 'success')
            
        db.session.commit()
        flash('Data user diperbarui.', 'success')
        return redirect(url_for('admin.manage_users') if current_user.role == 'admin' else url_for('main.dashboard'))
    return render_template('edit_user.html', user=user)

@bp.route('/users/verify/<int:id>', methods=['POST'])
@login_required
def toggle_verification(id):
    if current_user.role != 'admin': abort(403)
    user = User.query.get_or_404(id)
    user.is_verified = not user.is_verified
    db.session.commit()
    status = "terverifikasi" if user.is_verified else "belum terverifikasi"
    flash(f'Status user {user.username} diubah menjadi {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin': abort(403)
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri.', 'danger')
        return redirect(url_for('admin.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if current_user.role != 'admin': abort(403)
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Kategori berhasil ditambahkan!', 'success')
        else:
            flash('Kategori tidak valid atau sudah ada.', 'warning')
        return redirect(url_for('admin.manage_categories'))
    return render_template('manage_categories.html', categories=Category.query.all())

@bp.route('/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if current_user.role != 'admin': abort(403)
    cat = Category.query.get_or_404(id)
    Product.query.filter_by(category_id=id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('admin.manage_categories'))

@bp.route('/banners', methods=['GET', 'POST'])
@login_required
def manage_banners():
    if current_user.role != 'admin': abort(403)
    
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                if ext.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
                     flash('Format file tidak didukung', 'danger')
                     return redirect(url_for('admin.manage_banners'))

                unique_filename = f"banner_{uuid.uuid4().hex}{ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                new_banner = Banner(title=title, subtitle=subtitle, image_filename=unique_filename)
                db.session.add(new_banner)
                db.session.commit()
                flash('Banner berhasil ditambahkan!', 'success')
                
        return redirect(url_for('admin.manage_banners'))
        
    banners = Banner.query.all()
    return render_template('manage_banners.html', banners=banners)

@bp.route('/banners/delete/<int:id>', methods=['POST'])
@login_required
def delete_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.query.get_or_404(id)
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], banner.image_filename))
    except:
        pass
    db.session.delete(banner)
    db.session.commit()
    flash('Banner dihapus.', 'success')
    return redirect(url_for('admin.manage_banners'))

@bp.route('/banners/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.query.get_or_404(id)
    banner.is_active = not banner.is_active
    db.session.commit()
    return redirect(url_for('admin.manage_banners'))

    banner.is_active = not banner.is_active
    db.session.commit()
    return redirect(url_for('admin.manage_banners'))

