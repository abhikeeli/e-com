from db import db

class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(300), nullable=False)
    products = db.relationship('Product', backref='merchant', lazy=True)
    
    def __repr__(self):
        return f'<User {self.full_name}>'

class Product(db.Model):
    __tablename__ = 'product'
    
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)  # Changed from Integer to String
    merchant_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Correct ForeignKey reference
    description = db.Column(db.String(250), nullable=True)
    price_range = db.Column(db.String(200), nullable=False)
    comments = db.Column(db.String(200), nullable=True)
    filename = db.Column(db.Text, nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Product {self.product_name}>'

    