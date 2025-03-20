from flask import Flask, jsonify, request
import json

app = Flask(__name__)

def load_db():
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=2)

# Products Routes
@app.route('/products', methods=['GET'])
def get_products():
    db = load_db()
    category = request.args.get('category')
    in_stock = request.args.get('inStock', type=bool)
    products = db['products']
    if category:
        products = [p for p in products if p['category'] == category]
    if in_stock is not None:
        products = [p for p in products if p['inStock'] == in_stock]
    return jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    db = load_db()
    product = next((p for p in db['products'] if p['id'] == id), None)
    return jsonify(product) if product else ("Product not found", 404)

@app.route('/products', methods=['POST'])
def add_product():
    db = load_db()
    data = request.get_json()
    if not all(k in data for k in ['name', 'description', 'price', 'category', 'inStock']):
        return "Missing fields", 400
    new_id = max((p['id'] for p in db['products']), default=0) + 1
    product = {**data, "id": new_id}
    db['products'].append(product)
    save_db(db)
    return jsonify(product), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    db = load_db()
    product = next((p for p in db['products'] if p['id'] == id), None)
    if not product:
        return "Product not found", 404
    data = request.get_json()
    product.update(data)
    save_db(db)
    return jsonify(product)

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    db = load_db()
    product = next((p for p in db['products'] if p['id'] == id), None)
    if not product:
        return "Product not found", 404
    db['products'] = [p for p in db['products'] if p['id'] != id]
    save_db(db)
    return jsonify({"message": "Product deleted"})

# Orders Routes
@app.route('/orders', methods=['POST'])
def create_order():
    db = load_db()
    data = request.get_json()
    if not 'items' in data or not isinstance(data['items'], list):
        return "Invalid items", 400
    order_id = max((int(k) for k in db['orders'].keys()), default=0) + 1
    total = 0
    for item in data['items']:
        product = next((p for p in db['products'] if p['id'] == item['productId']), None)
        if not product or not product['inStock']:
            return f"Product {item['productId']} unavailable", 400
        total += product['price'] * item['quantity']
    order = {"id": order_id, "items": data['items'], "total": total, "status": "pending"}
    user_id = data.get('userId', 'guest')
    if user_id not in db['orders']:
        db['orders'][user_id] = []
    db['orders'][user_id].append(order)
    save_db(db)
    return jsonify(order), 201

@app.route('/orders/<user_id>', methods=['GET'])
def get_orders(user_id):
    db = load_db()
    orders = db['orders'].get(user_id, [])
    return jsonify(orders)

# Cart Routes
@app.route('/cart/<user_id>', methods=['POST'])
def add_to_cart(user_id):
    db = load_db()
    data = request.get_json()
    if not all(k in data for k in ['productId', 'quantity']):
        return "Missing fields", 400
    product = next((p for p in db['products'] if p['id'] == data['productId']), None)
    if not product or not product['inStock']:
        return "Product unavailable", 400
    if user_id not in db['carts']:
        db['carts'][user_id] = []
    cart_item = {"productId": data['productId'], "quantity": data['quantity'], "price": product['price']}
    db['carts'][user_id].append(cart_item)
    save_db(db)
    return jsonify(db['carts'][user_id])

@app.route('/cart/<user_id>', methods=['GET'])
def get_cart(user_id):
    db = load_db()
    cart = db['carts'].get(user_id, [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return jsonify({"items": cart, "total": total})

@app.route('/cart/<user_id>/item/<int:product_id>', methods=['DELETE'])
def remove_from_cart(user_id, product_id):
    db = load_db()
    if user_id not in db['carts']:
        return "Cart not found", 404
    db['carts'][user_id] = [item for item in db['carts'][user_id] if item['productId'] != product_id]
    save_db(db)
    return jsonify(db['carts'][user_id])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)