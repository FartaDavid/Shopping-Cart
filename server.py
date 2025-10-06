from flask import Flask, render_template, request, redirect, session, url_for
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load product data
with open('data/products.json') as f:
    PRODUCTS = {str(p["id"]): p for p in json.load(f)}

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS.values())

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = PRODUCTS.get(pid)
        if product:
            subtotal = qty * product['price']
            total += subtotal
            cart_items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add-item')
def add_item():
    pid = request.args.get('id')
    if pid and pid in PRODUCTS:
        cart = session.get('cart', {})
        cart[pid] = cart.get(pid, 0) + 1
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove-item')
def remove_item():
    pid = request.args.get('id')
    cart = session.get('cart', {})
    if pid in cart:
        del cart[pid]
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if request.method == 'POST':
        order = {
            "full_name": request.form['full_name'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "address": request.form['address'],
            "payment_method": request.form['payment_method'],
            "items": cart,
            "submitted_at": datetime.now().isoformat()
        }
        print("Order received:", json.dumps(order, indent=2))
        os.makedirs('submitted-data', exist_ok=True)
        with open(f'submitted-data/order_{datetime.now().isoformat()}.json', 'w') as f:
            json.dump(order, f, indent=2)
        session['cart'] = {}  # clear cart after order
        return "感谢您的订购 (Thank you for your order!)"
    else:
        cart_items = []
        total = 0
        for pid, qty in cart.items():
            product = PRODUCTS.get(pid)
            if product:
                subtotal = qty * product['price']
                total += subtotal
                cart_items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
        return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
