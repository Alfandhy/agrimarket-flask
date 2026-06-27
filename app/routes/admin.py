import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import User, Category, Banner, Product
from app import extensions
from app.routes.auth import validate_password_strength, format_whatsapp # Reuse helpers
from app.utils import upload_image, delete_image

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users')
@login_required
def manage_users():
    if current_user.role != 'admin': abort(403)
    
    users = []
    if extensions.firebase_db:
        docs = extensions.firebase_db.collection('users').stream()
        users = [User(id=doc.id, **doc.to_dict()) for doc in docs]
    
    # Normally we load products here, but for simple admin view, maybe we don't need them all or we fetch on demand.
    # The template might use user.products length, so let's attach them if needed.
    products = Product.get_all()
    for u in users:
        u.products = [p for p in products if p.seller_id == u.id]
        
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
            
        if User.get_by_username(username):
            flash('Username sudah digunakan.', 'danger')
        else:
            new_user = User(username=username, role=role, whatsapp_number=format_whatsapp(wa))
            new_user.set_password(password)
            new_user.save()
            flash(f'Akun {role} "{username}" berhasil dibuat!', 'success')
            return redirect(url_for('admin.manage_users'))
    return render_template('create_user.html')

@bp.route('/users/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin' and current_user.id != id: abort(403)
    user = User.get_by_id(id)
    if not user: abort(404)
    
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
            
        user.save()
        flash('Data user diperbarui.', 'success')
        return redirect(url_for('admin.manage_users') if current_user.role == 'admin' else url_for('main.dashboard'))
    return render_template('edit_user.html', user=user)

@bp.route('/users/verify/<string:id>', methods=['POST'])
@login_required
def toggle_verification(id):
    if current_user.role != 'admin': abort(403)
    user = User.get_by_id(id)
    if not user: abort(404)
    user.is_verified = not user.is_verified
    user.save()
    status = "terverifikasi" if user.is_verified else "belum terverifikasi"
    flash(f'Status user {user.username} diubah menjadi {status}.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/users/delete/<string:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin': abort(403)
    user = User.get_by_id(id)
    if not user: abort(404)
    if user.id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user.delete()
    flash('User berhasil dihapus.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if current_user.role != 'admin': abort(403)
    categories = Category.get_all()
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not any(c.name == name for c in categories):
            new_cat = Category(name=name)
            new_cat.save()
            flash('Kategori berhasil ditambahkan!', 'success')
        else:
            flash('Kategori tidak valid atau sudah ada.', 'warning')
        return redirect(url_for('admin.manage_categories'))
    return render_template('manage_categories.html', categories=categories)

@bp.route('/category/delete/<string:id>', methods=['POST'])
@login_required
def delete_category(id):
    if current_user.role != 'admin': abort(403)
    cat = Category.get_by_id(id)
    if not cat: abort(404)
    
    # Update products using this category
    if extensions.firebase_db:
        prods = extensions.firebase_db.collection('products').where('category_id', '==', id).stream()
        for doc in prods:
            extensions.firebase_db.collection('products').document(doc.id).update({'category_id': None})
            
    cat.delete()
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
                unique_filename = upload_image(file, folder="banners")
                if not unique_filename:
                     flash('Gagal mengupload gambar atau format salah.', 'danger')
                     return redirect(url_for('admin.manage_banners'))
                
                new_banner = Banner(title=title, subtitle=subtitle, image_filename=unique_filename)
                new_banner.save()
                flash('Banner berhasil ditambahkan!', 'success')
                
        return redirect(url_for('admin.manage_banners'))
        
    banners = Banner.get_all()
    return render_template('manage_banners.html', banners=banners)

@bp.route('/banners/delete/<string:id>', methods=['POST'])
@login_required
def delete_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.get_by_id(id)
    if not banner: abort(404)
    try:
        delete_image(banner.image_filename)
    except:
        pass
    banner.delete()
    flash('Banner dihapus.', 'success')
    return redirect(url_for('admin.manage_banners'))

@bp.route('/banners/toggle/<string:id>', methods=['POST'])
@login_required
def toggle_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.get_by_id(id)
    if not banner: abort(404)
    banner.is_active = not banner.is_active
    banner.save()
    return redirect(url_for('admin.manage_banners'))
