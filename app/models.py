
from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    # Changed to TEXT as per fix_schema.py
    password_hash = db.Column(db.Text, nullable=False) 
    role = db.Column(db.String(50), default='penjual')
    whatsapp_number = db.Column(db.String(20), nullable=False, default='62')
    is_verified = db.Column(db.Boolean, default=False)
    bio = db.Column(db.Text, nullable=True)
    # Changed to TEXT as per fix_schema.py
    profile_image = db.Column(db.Text, nullable=True)
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
    stock = db.Column(db.Integer, nullable=False, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        db.Index('idx_product_seller', 'seller_id'),
        db.Index('idx_product_category', 'category_id'),
        db.Index('idx_product_price', 'price'),
    )

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(150), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    __table_args__ = (
        db.Index('idx_image_product', 'product_id'),
    )

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    image_filename = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

