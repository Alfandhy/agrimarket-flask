
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Product, Category, Banner, User
from app import extensions
from app.routes.auth import validate_password_strength, format_whatsapp # Reuse helpers
from app.utils import upload_image, delete_image

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    search_query = request.args.get('search')
    category_id = request.args.get('category')
    
    all_banners = Banner.get_all()
    banners = [b for b in all_banners if b.is_active]
    
    all_products = Product.get_all()
    
    current_category = None
    if search_query:
        search_query = search_query.lower()
        products = [p for p in all_products if search_query in p.name.lower() or search_query in p.description.lower()]
    elif category_id:
        products = [p for p in all_products if p.category_id == category_id]
        current_category = Category.get_by_id(category_id)
    else:
        products = all_products
        
    for p in products:
        p.main_image = p.images[0].image_filename if p.images else None
        
    return render_template('index.html', 
                         products=products, 
                         categories=Category.get_all(), 
                         current_category=current_category, 
                         search_query=search_query,
                         banners=banners)

@bp.route('/dashboard')
@login_required
def dashboard():
    all_products = Product.get_all()
    
    if current_user.role == 'admin':
        products = all_products
    else:
        products = [p for p in all_products if p.seller_id == current_user.id]
        
    for p in products:
        p.main_image = p.images[0].image_filename if p.images else None
        
    return render_template('dashboard.html', products=products)

@bp.route('/seller/<string:user_id>')
def seller_profile(user_id):
    user = User.get_by_id(user_id)
    if not user: abort(404)
    all_products = Product.get_all()
    user.products = [p for p in all_products if p.seller_id == user.id]
    return render_template('seller_profile.html', user=user)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_my_profile():
    user = current_user
    if request.method == 'POST':
        user.whatsapp_number = format_whatsapp(request.form.get('whatsapp_number'))
        user.bio = request.form.get('bio')
        
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                new_filename = upload_image(file, folder="profiles")
                if new_filename:
                     # Delete old image if exists
                     if user.profile_image:
                         delete_image(user.profile_image)
                         
                     user.profile_image = new_filename
        
        new_pass = request.form.get('password')
        if new_pass:
            is_valid, msg = validate_password_strength(new_pass)
            if not is_valid:
                flash(msg, 'warning')
                return redirect(url_for('main.edit_my_profile'))
            user.set_password(new_pass)
            flash('Password diperbarui.', 'success')

        user.save()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('edit_user.html', user=user, is_self=True)

@bp.route('/about')
def about(): return render_template('about.html')

@bp.route('/contact')
def contact(): return render_template('contact.html')
