import os
import re
import uuid
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import joinedload

# --- Configuration ---
class Config:
    # SECURITY WARNING: Keep the secret key used in production secret!
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_very_secret_replace_in_prod')
    if SECRET_KEY == 'dev_key_very_secret_replace_in_prod':
        print("WARNING: You are using the default development SECRET_KEY. Change this in production!")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///marketplace_v5.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URI = "memory://"

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Extensions ---
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[app.config['RATELIMIT_DEFAULT']],
    storage_uri=app.config['RATELIMIT_STORAGE_URI']
)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='penjual')
    whatsapp_number = db.Column(db.String(20), nullable=False, default='62')
    is_verified = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(150), nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='seller', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(150), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Services / Utils ---
def format_whatsapp(number):
    """Normalize WhatsApp number to 62xxx format."""
    clean = re.sub(r'\D', '', number) 
    if clean.startswith('0'): return '62' + clean[1:]
    if not clean.startswith('62'): return '62' + clean
    return clean

def validate_password_strength(password):
    if len(password) < 8: return False, "Password minimal 8 karakter."
    if not re.search(r"[a-zA-Z]", password): return False, "Password harus mengandung huruf."
    if not re.search(r"\d", password): return False, "Password harus mengandung angka."
    return True, ""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

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
                continue # Skip invalid files silently or could raise error
                
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save file
            file.save(file_path)
            saved_images.append(unique_filename) # Track for rollback
            
            # Add to DB
            new_img = ProductImage(image_filename=unique_filename, product_id=product_id)
            db.session.add(new_img)
            allowed_slots -= 1
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Rollback: delete files that were actually saved
        for f in saved_images:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
            except:
                pass
        raise e 

def seed_data():
    """Initialize default data if not present."""
    # Seed Admin
    if not User.query.filter_by(role='admin').first():
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = User(username='admin', role='admin', whatsapp_number='6281234567890')
        admin.set_password(admin_pass)
        db.session.add(admin)
        print(">> Admin master created.")
    
    # Seed Categories
    target_cats = ['Produk Pertanian', 'Komoditas Pertanian', 'Buah-Buahan', 'Sayur-Sayuran', 'Makanan']
    for c_name in target_cats:
        if not Category.query.filter_by(name=c_name).first():
            db.session.add(Category(name=c_name))
            
    # Backfill join_date for existing users
    users_without_date = User.query.filter_by(join_date=None).all()
    for u in users_without_date:
        u.join_date = datetime.utcnow()

    db.session.commit()

def migrate_schema():
    """Manually migrate schema for SQLite (add new columns if missing)."""
    with db.engine.connect() as conn:
        # Check if columns exist (rudimentary check by trying to select or inspecting)
        # For SQLite, we can check PRAGMA table_info or just catch error on Alter.
        # We will iterate known new columns and try to add them.
        new_columns = [
            ('is_verified', 'BOOLEAN DEFAULT 0'),
            ('bio', 'TEXT'),
            ('profile_image', 'VARCHAR(150)'),
            ('join_date', 'DATETIME')
        ]
        
        for col_name, col_type in new_columns:
            try:
                # Try to add column. Will fail if exists.
                conn.execute(db.text(f'ALTER TABLE user ADD COLUMN {col_name} {col_type}'))
                print(f"Added column {col_name} to user table.")
            except Exception:
                # Column likely exists
                pass

        # Create Banner table if not exists (raw method as fallback)
        try:
             conn.execute(db.text('SELECT * FROM banner LIMIT 1'))
        except Exception:
             print("Creating banner table manually if needed...") 
             # SQLAlchemy create_all handles this usually, but good for manual checks
             pass


# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") 
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        flash('Username atau password salah.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validasi Input
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.', 'danger')
            return redirect(url_for('register'))
            
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            flash(msg, 'warning')
            return redirect(url_for('register'))
            
        # Create User (Default role: penjual)
        new_user = User(username=username, role='penjual')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silahkan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Optimization: Eager load relations to avoid N+1 queries
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

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin': abort(403)
    # Optimization: Eager load products for count
    users = User.query.options(joinedload(User.products)).all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
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
            return redirect(url_for('manage_users'))
    return render_template('create_user.html')

@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
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
                return redirect(url_for('edit_user', id=id))
            user.set_password(new_pass)
            flash('Password diperbarui.', 'success')
            
        db.session.commit()
        flash('Data user diperbarui.', 'success')
        return redirect(url_for('manage_users') if current_user.role == 'admin' else url_for('dashboard'))
    return render_template('edit_user.html', user=user)

@app.route('/seller/<int:user_id>')
def seller_profile(user_id):
    user = User.query.options(joinedload(User.products)).get_or_404(user_id)
    return render_template('seller_profile.html', user=user)

@app.route('/admin/users/verify/<int:id>', methods=['POST'])
@login_required
def toggle_verification(id):
    if current_user.role != 'admin': abort(403)
    user = User.query.get_or_404(id)
    user.is_verified = not user.is_verified
    db.session.commit()
    status = "terverifikasi" if user.is_verified else "belum terverifikasi"
    flash(f'Status user {user.username} diubah menjadi {status}.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_my_profile():
    user = current_user
    if request.method == 'POST':
        user.whatsapp_number = format_whatsapp(request.form.get('whatsapp_number'))
        user.bio = request.form.get('bio')
        
        # Profile Image
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                unique_filename = f"profile_{user.id}_{uuid.uuid4().hex}{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Delete old image if exists
                if user.profile_image:
                    try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image))
                    except: pass
                    
                user.profile_image = unique_filename
        
        new_pass = request.form.get('password')
        if new_pass:
            is_valid, msg = validate_password_strength(new_pass)
            if not is_valid:
                flash(msg, 'warning')
                return redirect(url_for('edit_my_profile'))
            user.set_password(new_pass)
            flash('Password diperbarui.', 'success')

        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_user.html', user=user, is_self=True)

@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin': abort(403)
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Tidak bisa menghapus akun sendiri.', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/product/create', methods=['GET', 'POST'])
@login_required
def create_product():
    categories = Category.query.all()
    if request.method == 'POST':
        # Basic validation
        try:
            new_product = Product(
                name=request.form.get('name'), 
                description=request.form.get('description'), 
                price=int(request.form.get('price')), 
                category_id=request.form.get('category_id') or None,
                seller_id=current_user.id 
            )
            db.session.add(new_product)
            db.session.commit() # Commit first to get ID
            
            save_product_images(request.files.getlist('images'), new_product.id)
            flash('Produk berhasil ditambahkan!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Harga harus berupa angka.', 'warning')
        except Exception as e:
            flash('Terjadi kesalahan saat menyimpan produk.', 'danger')
            
    return render_template('create_product.html', categories=categories)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('dashboard'))
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/product/image/delete/<int:img_id>', methods=['POST'])
@login_required
def delete_product_image(img_id):
    img = ProductImage.query.options(joinedload(ProductImage.product)).get_or_404(img_id)
    if current_user.role != 'admin' and img.product.seller_id != current_user.id: abort(403)
    
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.image_filename))
    except (FileNotFoundError, TypeError):
        pass # File already gone, fine to delete record
        
    db.session.delete(img)
    db.session.commit()
    return redirect(url_for('edit_product', id=img.product_id))

@app.route('/product/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    if current_user.role != 'admin' and product.seller_id != current_user.id: abort(403)
    
    # Cleanup images
    for img in product.images:
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.image_filename))
        except: pass
        
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/categories', methods=['GET', 'POST'])
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
        return redirect(url_for('manage_categories'))
    return render_template('manage_categories.html', categories=Category.query.all())

@app.route('/admin/category/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if current_user.role != 'admin': abort(403)
    cat = Category.query.get_or_404(id)
    # Unlink products
    Product.query.filter_by(category_id=id).update({'category_id': None})
    db.session.delete(cat)
    db.session.commit()
    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('manage_categories'))

    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('manage_categories'))

@app.route('/admin/banners', methods=['GET', 'POST'])
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
                unique_filename = f"banner_{uuid.uuid4().hex}{ext}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                new_banner = Banner(title=title, subtitle=subtitle, image_filename=unique_filename)
                db.session.add(new_banner)
                db.session.commit()
                flash('Banner berhasil ditambahkan!', 'success')
                
        return redirect(url_for('manage_banners'))
        
    banners = Banner.query.all()
    return render_template('manage_banners.html', banners=banners)

@app.route('/admin/banners/delete/<int:id>', methods=['POST'])
@login_required
def delete_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.query.get_or_404(id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], banner.image_filename))
    except:
        pass
    db.session.delete(banner)
    db.session.commit()
    flash('Banner dihapus.', 'success')
    return redirect(url_for('manage_banners'))

@app.route('/admin/banners/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_banner(id):
    if current_user.role != 'admin': abort(403)
    banner = Banner.query.get_or_404(id)
    banner.is_active = not banner.is_active
    db.session.commit()
    return redirect(url_for('manage_banners'))

@app.route('/')
def index():
    search_query = request.args.get('search')
    category_id = request.args.get('category')
    
    banners = Banner.query.filter_by(is_active=True).all()
    
    # Optimization: Eager load relations for homepage
    query = Product.query.options(
        joinedload(Product.category), 
        joinedload(Product.seller),
        joinedload(Product.images)
    )
    
    if search_query:
        query = query.filter(Product.name.contains(search_query) | Product.description.contains(search_query))
        current_category = None
    elif category_id:
        query = query.filter_by(category_id=category_id)
        current_category = Category.query.get(category_id)
    else:
        current_category = None
        
    products = query.all()
    
    # Process main image display logic (could be done in template, but fine here)
    for p in products:
        p.main_image = p.images[0].image_filename if p.images else None
        
    return render_template('index.html', 
                         products=products, 
                         categories=Category.query.all(), 
                         current_category=current_category, 
                         search_query=search_query,
                         banners=banners)

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/blog')
def blog(): return render_template('blog.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/product/<int:id>')
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

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="<div class='text-center py-5'><h1>404</h1><p>Halaman tidak ditemukan.</p><a href='/' class='btn btn-primary'>Ke Beranda</a></div>"), 404

@app.errorhandler(403)
def forbidden(e):
    flash('Akses ditolak.', 'danger')
    return redirect(url_for('index'))

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # migrate_schema() # Deprecated with Postgres
        seed_data()
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
