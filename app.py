from flask import Flask, request, render_template, jsonify, redirect, url_for,session
from db import db
import re
import os
from passlib.hash import pbkdf2_sha256   
import uuid
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

USERS_FILE = "users_data.json"  # File to store user data

# Load users data from the JSON file
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error decoding JSON. Returning an empty users dictionary.")
            return {}
    return {}

# Save users data to the JSON file
def save_users(users_data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=4)


# Load product data from the JSON file
# Load product data from the JSON file with UTF-8 encoding
def load_products():
    with open('products.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def loadAll_products():
    try:
        with open("galla_products.json", "r", encoding="utf-8") as galla_file:
            galla_products = json.load(galla_file)
    except (FileNotFoundError, json.JSONDecodeError):
        galla_products = []

    try:
        with open("azzafahmy_products.json", "r", encoding="utf-8") as azza_file:
            azza_products = json.load(azza_file)
    except (FileNotFoundError, json.JSONDecodeError):
        azza_products = []

    return galla_products + azza_products

def load_favorite_links():
    if 'user_id' not in session:
        return []
    users_data = load_users()
    user_id = session['user_id']
    return users_data.get(user_id, {}).get("favorites", [])

def save_favorite_links(fav_links):
    if 'user_id' not in session:
        return
    user_id = session['user_id']
    users_data = load_users()
    if user_id not in users_data:
        users_data[user_id] = {"favorites": []}
    users_data[user_id]["favorites"] = fav_links
    save_users(users_data)


def validate_password(password):
    pattern= r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern,password)

def get_user_by_email(email):
    for user in db.values():
        if user['email'] == email:
            return user
    return None


@app.route('/')
def index():
    # Render the HTML template
    return render_template('index.html')

@app.route('/api/products')
def products():
    # Return the product data as JSON
    products = load_products()
    return jsonify(products)


with open("reviews.json", 'r') as jsonfile:
    reviews = json.load(jsonfile)
@app.route('/about', methods=["GET", "POST"])
def about():
    global reviews
    if request.method == "POST":
        name = request.form["name"]
        review = request.form["review"]
        reviews.append({"name": name, "review": review})
        with open("reviews.json", 'w') as file:
            json.dump(reviews, file, indent=4)
        return redirect(url_for("about"))
    return render_template("about.html", reviews=reviews)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/jewellery')
def jewellery():
    return render_template('jewellery.html')

@app.route('/review')
def review_page():
    return render_template('review.html')

@app.route('/shop')
def shop():
    if 'user_id' in session:
        favorite_links = load_favorite_links()
        return render_template("shop.html", logged_in=True, favorite_links=favorite_links)
    return render_template("shop.html", logged_in=False, favorite_links=[])


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    combined_products = loadAll_products()

    # Filter products based on the search query
    filtered_products = [
        product for product in combined_products
        if query in product["Title"].lower() or query in ' '.join(product["Description"].lower().split()[:6])
    ]

    # Return the filtered products as a JSON response
    return jsonify(filtered_products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users_data = load_users()

        if email in users_data and pbkdf2_sha256.verify(password, users_data[email]["password"]):
            session['user_id'] = email
            session['user_name'] = users_data[email]["name"]
            return redirect(url_for("index"))

        return render_template("login.html", error_username_password="Invalid email or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password_confirmation = request.form["password_confirmation"]
        address = request.form["address"]
        year_of_birth = request.form["DOB"]

        users_data = load_users()

        if email in users_data:
            return render_template("signup.html", error_email_exist="Email already exists")

        if not validate_password(password):
            return render_template("signup.html", error_passwords_validation="Password must be at least 8 characters long, include at least one lowercase letter, one uppercase letter, one number, and one special character")

        if password != password_confirmation:
            return render_template("signup.html", error_passwords_confirmation="Passwords do not match")

        hashed_password = pbkdf2_sha256.hash(password)
        user_id = uuid.uuid4().hex
        users_data[email] = {
            "name": name,
            "password": hashed_password,
            "address": address,
            "year_of_birth": year_of_birth,
            "favorites": []
        }

        save_users(users_data)
        session['user_id'] = email
        return redirect(url_for("index"))

    return render_template("signup.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.pop('user_id', None)
        return redirect(url_for("index"))  # Redirect to home page after logout
    return render_template("logout.html")



@app.route("/favPage")
def fav_page():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    
    fav_links = load_favorite_links()
    combined_products = loadAll_products()

    favorite_products = [product for product in combined_products if product["Product Link"] in fav_links]
    return render_template("favPage.html", favorites=favorite_products)


@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    product_url = request.json.get("product_url")
    
    if not product_url:
        return jsonify({"success": False, "error": "Product URL is missing"}), 400
    
    # Load current favorites of the logged-in user
    fav_links = load_favorite_links()

    if product_url in fav_links:
        # If the product is already in favorites, remove it
        fav_links.remove(product_url)
        action = "removed"
    else:
        # If the product is not in favorites, add it
        fav_links.append(product_url)
        action = "added"

    # Save the updated favorites list
    save_favorite_links(fav_links)

    return jsonify({"success": True, "action": action, "favorites": fav_links})


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    product_url = request.json.get("product_url")
    
    if not product_url:
        return jsonify({"success": False, "error": "Product URL is missing"}), 400
    
    # Load current favorites of the logged-in user
    fav_links = load_favorite_links()

    if product_url not in fav_links:
        return jsonify({"success": False, "error": "Product URL not found in favorites"}), 400

    # Remove the product URL from favorites
    fav_links.remove(product_url)

    # Save the updated favorites list
    save_favorite_links(fav_links)

    return jsonify({"success": True, "favorites": fav_links})

if __name__ == '__main__':
    app.run(debug=True)