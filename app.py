from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Stripe configuration
stripe.api_key = 'your_stripe_secret_key'

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)

# Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Sample data for products (optional)
def add_sample_products():
    sample_products = [
        Product(name="Kids T-Shirt", price=15.99, description="Comfortable cotton t-shirt for kids."),
        Product(name="Kids Shorts", price=19.99, description="Stylish shorts for summer."),
        Product(name="Kids Jacket", price=29.99, description="Warm jacket for winter."),
        Product(name="Kids Shoes", price=39.99, description="Durable shoes for active kids."),
    ]
    db.session.bulk_save_objects(sample_products)
    db.session.commit()

# Uncomment to add sample products to the database
# add_sample_products()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/orders')
def orders():
    return render_template('orders.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User  registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "User  logged in successfully"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "price": p.price, "description": p.description} for p in products]), 200

@app.route('/api/user-profile', methods=['GET', 'PUT'])
def user_profile():
    if request.method == 'GET':
        # Assuming user is logged in and we have their email
        email = request.args.get('email')  # You would typically get this from a session
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"username": user.username, "email": user.email}), 200
        return jsonify({"message": "User not found"}), 404

    if request.method == 'PUT':
        data = request.json
        email = data['email']  # Get email from request
        user = User.query.filter_by(email=email).first()
        if user:
            user.username = data['username']
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        return jsonify({"message": "User  not found"}), 404

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user:
        new_order = Order(user_id=user.id, product_id=data['product_id'], quantity=data['quantity'])
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Order created successfully"}), 201
    return jsonify({"message": "User  not found"}), 404

@app.route('/api/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": o.id, "product_id": o.product_id, "quantity": o.quantity} for o in orders]), 200

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': data['product_name'],
                    },
                    'unit_amount': data['amount'],
                },
                'quantity': data['quantity'],
            },
        ],
        mode='payment',
        success_url='http://localhost:5000/success',
        cancel_url='http://localhost:5000/cancel',
    )
    return jsonify({'id': session.id})

if __name__ == '__main__':
    app.run(debug=True)