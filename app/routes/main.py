
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from app.models import Product, Category, Banner, User, db
from app.routes.auth import validate_password_strength, format_whatsapp # Reuse helpers
from app.utils import upload_image, delete_image

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    search_query = request.args.get('search')
    category_id = request.args.get('category')
    
    banners = Banner.query.filter_by(is_active=True).all()
    
    query = Product.query.options(
        joinedload(Product.category), 
        joinedload(Product.seller),
        joinedload(Product.images)
    )
    
    current_category = None
    if search_query:
        query = query.filter(Product.name.contains(search_query) | Product.description.contains(search_query))
    elif category_id:
        query = query.filter_by(category_id=category_id)
        current_category = db.session.get(Category, category_id)
        
    products = query.all()
    
    for p in products:
        p.main_image = p.images[0].image_filename if p.images else None
        
    return render_template('index.html', 
                         products=products, 
                         categories=Category.query.all(), 
                         current_category=current_category, 
                         search_query=search_query,
                         banners=banners)

@bp.route('/dashboard')
@login_required
def dashboard():
    query = Product.query.options(
        joinedload(Product.category), 
        joinedload(Product.seller),
        joinedload(Product.images)
    )
    
    if current_user.role == 'admin':
        products = query.all()
    else:
        products = query.filter_by(seller_id=current_user.id).all()
        
    for p in products:
        p.main_image = p.images[0].image_filename if p.images else None
        
    return render_template('dashboard.html', products=products)

@bp.route('/seller/<int:user_id>')
def seller_profile(user_id):
    user = User.query.options(joinedload(User.products)).get_or_404(user_id)
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
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                
                # Use helper for upload
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

        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('edit_user.html', user=user, is_self=True)

@bp.route('/about')
def about(): return render_template('about.html')

@bp.route('/contact')
def contact(): return render_template('contact.html')
