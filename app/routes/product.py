
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from app.models import Product, Category, ProductImage, db

bp = Blueprint('product', __name__, url_prefix='/product')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_product_images(files, product_id):
    """Save images with transaction safety."""
    count_existing = ProductImage.query.filter_by(product_id=product_id).count()
    allowed_slots = 5 - count_existing
    
    if allowed_slots <= 0 or not files:
        return

    saved_images = []
    try:
        for file in files:
            if file.filename == '' or allowed_slots <= 0:
                continue
            
            if not allowed_file(file.filename):
                continue
                
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(file_path)
            saved_images.append(unique_filename)
            
            new_img = ProductImage(image_filename=unique_filename, product_id=product_id)
            db.session.add(new_img)
            allowed_slots -= 1
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        for f in saved_images:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], f))
            except:
                pass
        raise e 

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            new_product = Product(
                name=request.form.get('name'), 
                description=request.form.get('description'), 
                price=int(request.form.get('price')), 
                category_id=request.form.get('category_id') or None,
                seller_id=current_user.id 
            )
            db.session.add(new_product)
            db.session.commit()
            
            save_product_images(request.files.getlist('images'), new_product.id)
            flash('Produk berhasil ditambahkan!', 'success')
            return redirect(url_for('main.dashboard'))
        except ValueError:
            flash('Harga harus berupa angka.', 'warning')
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan produk: {e}', 'danger')
            
    return render_template('create_product.html', categories=categories)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = int(request.form.get('price'))
        product.category_id = request.form.get('category_id')
        
        save_product_images(request.files.getlist('images'), product.id)
        db.session.commit()
        flash('Produk berhasil diperbarui!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_product.html', product=product, categories=categories)

@bp.route('/image/delete/<int:img_id>', methods=['POST'])
@login_required
def delete_product_image(img_id):
    img = ProductImage.query.options(joinedload(ProductImage.product)).get_or_404(img_id)
    if current_user.role != 'admin' and img.product.seller_id != current_user.id: abort(403)
    
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_filename))
    except (FileNotFoundError, TypeError):
        pass
        
    db.session.delete(img)
    db.session.commit()
    return redirect(url_for('product.edit_product', id=img.product_id))

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    for img in product.images:
        try: os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], img.image_filename))
        except: pass
        
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus.', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/<int:id>')
def product_detail(id):
    product = Product.query.options(joinedload(Product.seller), joinedload(Product.images), joinedload(Product.category)).get_or_404(id)
    recommendations = []
    if product.category_id:
        recommendations = Product.query.filter_by(category_id=product.category_id)\
            .filter(Product.id != product.id)\
            .options(joinedload(Product.images))\
            .limit(4).all()
        for r in recommendations:
            r.main_image = r.images[0].image_filename if r.images else None
            
    return render_template('detail.html', product=product, recommendations=recommendations)
