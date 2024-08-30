from flask import Flask, request, jsonify, session, g
import sqlite3
import flask_cors

app = Flask(__name__)
app.secret_key = 'super_secure_secret_key'

DATABASE = ':memory:'

# def process_credit_card(card_number, amount):
#     print(f"Processing payment:\nCard Number: {card_number}\nAmount: {amount}")
#     return {"status": "success", "message": "Payment processed successfully"}

# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(DATABASE)
#         g.db.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
#         g.db.execute('''CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)''')
#         g.db.execute('''CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER)''')
#         g.db.execute('''INSERT INTO users (username, password, role) VALUES ('admin', 'adminpass', 'admin')''')
#         g.db.execute('''INSERT INTO users (username, password, role) VALUES ('user1', 'user1pass', 'user')''')
#         g.db.execute('''INSERT INTO products (name, price) VALUES ('Product1', 10.0)''')
#         g.db.execute('''INSERT INTO products (name, price) VALUES ('Product2', 20.0)''')
#         g.db.commit()
#     return g.db

# @app.teardown_appcontext
# def close_db(exception):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()           

# @app.route('/signup', methods=['POST'])
# def signup():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     db = get_db()
#     db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'user'))
#     db.commit()
#     return jsonify({"message": "User created successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    if user:
        session['user_id'] = user[0]
        session['role'] = user[3]
        return jsonify({"message": "Logged in successfully!"})
    else:
        return jsonify({"error": "Invalid credentials!"}), 401

@app.route('/products', methods=['GET'])
def products():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return jsonify([{'id': row[0], 'name': row[1], 'price': row[2]} for row in products])

@app.route('/order', methods=['POST'])
def order():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated!"}), 401
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    db = get_db()
    db.execute('INSERT INTO orders (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
    db.commit()
    return jsonify({"message": "Order placed successfully!"}), 201

# @app.route('/admin', methods=['GET'])
# def admin():
#     db = get_db()
#     orders = db.execute('''SELECT o.id, u.username, p.name 
#                            FROM orders om
#                            JOIN users u ON o.user_id = u.id 
#                            JOIN products p ON o.product_id = p.id''').fetchall()
#     return jsonify([{'order_id': row[0], 'username': row[1], 'product_name': row[2]} for row in orders])


# @app.route('/data_admin', methods=['GET'])
# def admin():
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return jsonify({"error": "Unauthorized access!"}), 403
    
#     db = get_db()
#     orders = db.execute('''SELECT o.id, u.username, p.name 
#                            FROM orders o
#                            JOIN users u ON o.user_id = u.id 
#                            JOIN products p ON o.product_id = p.id''').fetchall()
#     return jsonify([{'order_id': row[0], 'username': row[1], 'product_name': row[2]} for row in orders])


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    db = get_db()
    cursor = db.cursor()

    # Vulnerable code: directly injecting the user input into the SQL query
    sql_query = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
    cursor.execute(sql_query)

    results = cursor.fetchall()
    return jsonify(results)


# @app.route('/checkout', methods=['POST'])
# def checkout():
#     if 'user_id' not in session:
#         return jsonify({"error": "Not authenticated!"}), 401
#     user_id = session['user_id']
#     total = 0
#     db = get_db()
#     orders = db.execute('SELECT p.price FROM orders o JOIN products p ON o.product_id = p.id WHERE o.user_id = ?', (user_id,)).fetchall()
#     for _ in range(1000000):
#         for order in orders:
#             total += order[0]
#     return jsonify({"total": total}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully!"})

@app.route('/user/details', methods=['GET'])
def user_details():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated!"}), 401
    db = get_db()
    user = db.execute('SELECT username, role, last_login, social_security_number FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return jsonify({'username': user[0], 'role': user[1], 'last_login': user[2], 'SSN': user[3]})

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated!"}), 401
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    db = get_db()
    user = db.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user and user[0] == old_password:
        db.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, session['user_id']))
        db.commit()
        return jsonify({"message": "Password changed successfully"})
    else:
        return jsonify({"error": "Incorrect old password!"}), 403

@app.route('/delete-order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated!"}), 401
    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    db.commit()
    return jsonify({"message": "Order deleted"})

@app.route('/api/all-endpoints', methods=['GET'])
def all_endpoints():
    endpoints = [e.rule for e in app.url_map.iter_rules() if not e.rule.startswith('/admin')]
    admin_endpoints = [e.rule for e in app.url_map.iter_rules() if e.rule.startswith('/admin')]
    return jsonify({"public_endpoints": endpoints, "admin_endpoints": admin_endpoints})

from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

import pickle
@app.route('/unsafe-load', methods=['POST'])
def unsafe_load():
    content = request.get_data()
    obj = pickle.loads(content)
    return jsonify({"message": "Object loaded successfully!", "object_details": str(obj)})

@app.route('/process-payment', methods=['POST'])
def process_payment():
    card_number = request.json.get('card_number')
    amount = request.json.get('amount')
    result = process_credit_card(card_number, amount)
    return jsonify(result)

import requests

@app.route('/')
def ssrf_demo():
    return 'SSRF Demo'

@app.route('/fetch', methods=['GET', 'POST'])
def fetch_url():
    if request.method == 'GET':
        url = request.args.get('url')
    elif request.method == 'POST':
        url = request.form.get('url')
    if not url:
        return 'Please provide a URL'
    try:
        response = requests.get(url)
        return response.text
    except:
        return 'Unable to fetch URL'

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    external_api_url = request.json.get('url')
    sensitive_data = request.json.get('sensitive_data')
    try:
        response = requests.post(external_api_url, json={"data": sensitive_data})
        return response.text
    except Exception as e:
        return str(e), 500

@app.route('/redirect', methods=['POST'])
def redirect_to_external_api():
    external_api_url = request.json.get('url')
    try:
        response = requests.get(external_api_url)
        return response.text
    except Exception as e:
        return str(e), 500
    
@app.route('/dummy', methods=['POST'])
def dummy():
    session.clear()
    return jsonify({"message": "Logged out successfully!"})

if __name__ == '__main__':
    app.run(debug=True, port=5002)





