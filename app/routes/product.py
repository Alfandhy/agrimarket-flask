
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Product, Category, ProductImage
from app import extensions
from app.utils import upload_image, delete_image

bp = Blueprint('product', __name__, url_prefix='/product')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_product_images(files, product_id):
    """Save images for a product."""
    product = Product.get_by_id(product_id)
    if not product: return
    
    count_existing = len(product.images)
    allowed_slots = 5 - count_existing
    
    if allowed_slots <= 0 or not files:
        return

    saved_images = []
    
    try:
        for file in files:
            if file.filename == '' or allowed_slots <= 0:
                continue
            
            filename = upload_image(file, folder="products")
            if not filename:
                continue
                
            saved_images.append(filename)
            
            new_img = ProductImage(image_filename=filename, product_id=product_id)
            product.images.append(new_img)
            allowed_slots -= 1
            
        product.save()
    except Exception as e:
        for f in saved_images:
            delete_image(f)
        raise e 

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    categories = Category.get_all()
    if request.method == 'POST':
        try:
            price_val = int(request.form.get('price'))
            stock_val = int(request.form.get('stock', 1))
            
            if price_val < 0 or stock_val < 0:
                flash('Harga dan stok tidak boleh bernilai negatif.', 'danger')
                return redirect(url_for('product.create_product'))
                
            new_product = Product(
                name=request.form.get('name'), 
                description=request.form.get('description'), 
                price=price_val, 
                stock=stock_val,
                category_id=request.form.get('category_id') or None,
                seller_id=current_user.id 
            )
            new_product.save()
            
            save_product_images(request.files.getlist('images'), new_product.id)
            flash('Produk berhasil ditambahkan!', 'success')
            return redirect(url_for('main.dashboard'))
        except ValueError:
            flash('Harga dan stok harus berupa angka.', 'warning')
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan produk: {e}', 'danger')
            
    return render_template('create_product.html', categories=categories)

@bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.get_by_id(id)
    if not product: abort(404)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    categories = Category.get_all()
    if request.method == 'POST':
        price_val = int(request.form.get('price'))
        stock_val = int(request.form.get('stock', product.stock))
        
        if price_val < 0 or stock_val < 0:
            flash('Harga dan stok tidak boleh bernilai negatif.', 'danger')
            return redirect(url_for('product.edit_product', id=product.id))
            
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = price_val
        product.stock = stock_val
        product.category_id = request.form.get('category_id')
        
        product.save() # save before images
        save_product_images(request.files.getlist('images'), product.id)
        flash('Produk berhasil diperbarui!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_product.html', product=product, categories=categories)

@bp.route('/<string:product_id>/image/delete/<string:img_id>', methods=['POST'])
@login_required
def delete_product_image(product_id, img_id):
    product = Product.get_by_id(product_id)
    if not product: abort(404)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    img_to_delete = next((img for img in product.images if img.id == img_id), None)
    if not img_to_delete: abort(404)
    
    try:
        delete_image(img_to_delete.image_filename)
    except (FileNotFoundError, TypeError):
        pass
        
    product.images = [img for img in product.images if img.id != img_id]
    product.save()
    return redirect(url_for('product.edit_product', id=product.id))

@bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.get_by_id(id)
    if not product: abort(404)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    for img in product.images:
        try: delete_image(img.image_filename)
        except: pass
        
    product.delete()
    flash('Produk berhasil dihapus.', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/<string:id>')
def product_detail(id):
    product = Product.get_by_id(id)
    if not product: abort(404)
    
    recommendations = []
    if product.category_id:
        # manual filter for recommendations
        all_prods = Product.get_all()
        recs = [p for p in all_prods if p.category_id == product.category_id and p.id != product.id]
        recommendations = recs[:4]
        for r in recommendations:
            r.main_image = r.images[0].image_filename if r.images else None
            
    return render_template('detail.html', product=product, recommendations=recommendations)
