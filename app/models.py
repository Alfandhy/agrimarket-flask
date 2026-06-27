
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import extensions
import uuid

class User(UserMixin):
    def __init__(self, id=None, username="", password_hash="", role='penjual', whatsapp_number='62', is_verified=False, bio=None, profile_image=None, join_date=None, **kwargs):
        self.id = str(id) if id else None
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.whatsapp_number = whatsapp_number
        self.is_verified = is_verified
        self.bio = bio
        self.profile_image = profile_image
        self.join_date = join_date if join_date else datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id
        
    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'whatsapp_number': self.whatsapp_number,
            'is_verified': self.is_verified,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'join_date': self.join_date
        }

    @staticmethod
    def get_by_id(user_id):
        if not extensions.firebase_db or not user_id: return None
        doc = extensions.firebase_db.collection('users').document(str(user_id)).get()
        if doc.exists:
            data = doc.to_dict()
            return User(id=doc.id, **data)
        return None

    @staticmethod
    def get_by_username(username):
        if not extensions.firebase_db: return None
        users = extensions.firebase_db.collection('users').where('username', '==', username).limit(1).stream()
        for doc in users:
            data = doc.to_dict()
            return User(id=doc.id, **data)
        return None
        
    def save(self):
        if not extensions.firebase_db: return
        data = self.to_dict()
        if self.id:
            extensions.firebase_db.collection('users').document(self.id).set(data)
        else:
            _, ref = extensions.firebase_db.collection('users').add(data)
            self.id = ref.id
            
    def delete(self):
        if not extensions.firebase_db or not self.id: return
        extensions.firebase_db.collection('users').document(self.id).delete()


class Category:
    def __init__(self, id=None, name="", **kwargs):
        self.id = str(id) if id else None
        self.name = name
        
    def to_dict(self):
        return {'name': self.name}
        
    def save(self):
        if not extensions.firebase_db: return
        data = self.to_dict()
        if self.id:
            extensions.firebase_db.collection('categories').document(self.id).set(data)
        else:
            _, ref = extensions.firebase_db.collection('categories').add(data)
            self.id = ref.id

    def delete(self):
        if not extensions.firebase_db or not self.id: return
        extensions.firebase_db.collection('categories').document(self.id).delete()
            
    @staticmethod
    def get_all():
        if not extensions.firebase_db: return []
        docs = extensions.firebase_db.collection('categories').stream()
        return [Category(id=doc.id, **doc.to_dict()) for doc in docs]
        
    @staticmethod
    def get_by_id(cat_id):
        if not extensions.firebase_db or not cat_id: return None
        doc = extensions.firebase_db.collection('categories').document(str(cat_id)).get()
        if doc.exists:
            return Category(id=doc.id, **doc.to_dict())
        return None


class ProductImage:
    def __init__(self, id=None, image_filename="", product_id=None, **kwargs):
        self.id = str(id) if id else uuid.uuid4().hex
        self.image_filename = image_filename
        self.product_id = str(product_id) if product_id else None
        
    def to_dict(self):
        return {
            'id': self.id,
            'image_filename': self.image_filename,
            'product_id': self.product_id
        }

class Product:
    def __init__(self, id=None, name="", description="", price=0, stock=1, category_id=None, seller_id=None, images=None, **kwargs):
        self.id = str(id) if id else None
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category_id = str(category_id) if category_id else None
        self.seller_id = str(seller_id) if seller_id else None
        
        self.images = []
        if images:
            for img in images:
                if isinstance(img, dict):
                    self.images.append(ProductImage(**img))
                elif isinstance(img, ProductImage):
                    self.images.append(img)
                    
    @property
    def seller(self):
        return User.get_by_id(self.seller_id)
        
    @property
    def category(self):
        return Category.get_by_id(self.category_id)
        
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category_id': self.category_id,
            'seller_id': self.seller_id,
            'images': [img.to_dict() for img in self.images]
        }
        
    def save(self):
        if not extensions.firebase_db: return
        data = self.to_dict()
        if self.id:
            extensions.firebase_db.collection('products').document(self.id).set(data)
        else:
            _, ref = extensions.firebase_db.collection('products').add(data)
            self.id = ref.id
            
    def delete(self):
        if not extensions.firebase_db or not self.id: return
        extensions.firebase_db.collection('products').document(self.id).delete()
            
    @staticmethod
    def get_by_id(prod_id):
        if not extensions.firebase_db or not prod_id: return None
        doc = extensions.firebase_db.collection('products').document(str(prod_id)).get()
        if doc.exists:
            return Product(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def get_all():
        if not extensions.firebase_db: return []
        docs = extensions.firebase_db.collection('products').stream()
        return [Product(id=doc.id, **doc.to_dict()) for doc in docs]

class Banner:
    def __init__(self, id=None, title="", subtitle="", image_filename="", is_active=True, **kwargs):
        self.id = str(id) if id else None
        self.title = title
        self.subtitle = subtitle
        self.image_filename = image_filename
        self.is_active = is_active
        
    def to_dict(self):
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'image_filename': self.image_filename,
            'is_active': self.is_active
        }
        
    def save(self):
        if not extensions.firebase_db: return
        data = self.to_dict()
        if self.id:
            extensions.firebase_db.collection('banners').document(self.id).set(data)
        else:
            _, ref = extensions.firebase_db.collection('banners').add(data)
            self.id = ref.id

    def delete(self):
        if not extensions.firebase_db or not self.id: return
        extensions.firebase_db.collection('banners').document(self.id).delete()
            
    @staticmethod
    def get_all():
        if not extensions.firebase_db: return []
        docs = extensions.firebase_db.collection('banners').stream()
        return [Banner(id=doc.id, **doc.to_dict()) for doc in docs]

