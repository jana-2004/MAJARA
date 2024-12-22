from flask import Flask, request, render_template, jsonify, redirect, url_for,session,flash, get_flashed_messages
import re
import os
from passlib.hash import pbkdf2_sha256   
import uuid
import json
from mail import *
import sqlite3
from datetime import datetime
import random
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)
app.secret_key = os.urandom(24) 

DATABASE_FILE = "users_data.db"  # SQLite database file
serializer = URLSafeTimedSerializer(app.secret_key)


# Load users data from the SQLite database
def load_users():
    users = {}
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Fetch all user data
        cursor.execute("SELECT id, email, name, password, address, year_of_birth FROM users")
        user_rows = cursor.fetchall()

        user_id_map = {}  
        for row in user_rows:
            user_id, email, name, password, address, year_of_birth = row
            users[email] = {
                "name": name,
                "password": password,
                "address": address,
                "year_of_birth": year_of_birth,
                "favorites": [],
                "notifications": []
            }
            user_id_map[user_id] = email

        cursor.execute("SELECT user_id, favorite_url FROM favorites")
        favorite_rows = cursor.fetchall()
        for user_id, favorite_url in favorite_rows:
            email = user_id_map.get(user_id)
            if email:
                users[email]["favorites"].append(favorite_url)

        cursor.execute("SELECT user_id, message, is_read FROM notifications")
        notification_rows = cursor.fetchall()
        for user_id, message, is_read in notification_rows:
            email = user_id_map.get(user_id)
            if email:
                users[email]["notifications"].append({
                    "message": message,
                    "read": bool(is_read)
                })

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

    return users


# Save users data to the JSON file
def save_users(users_data):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Clear existing data
        cursor.executescript("""
        DELETE FROM favorites;
        DELETE FROM notifications;
        DELETE FROM users;
        """)

        # Save new data
        for email, details in users_data.items():
            # Insert user data
            cursor.execute("""
            INSERT INTO users (email, name, password, address, year_of_birth)
            VALUES (?, ?, ?, ?, ?)
            """, (email, details["name"], details["password"], details["address"], details["year_of_birth"]))
            
            # Get the user ID for the inserted record
            user_id = cursor.lastrowid

            # Insert favorites
            for favorite in details.get("favorites", []):
                cursor.execute("""
                INSERT INTO favorites (user_id, favorite_url)
                VALUES (?, ?)
                """, (user_id, favorite))

            # Insert notifications
            for notification in details.get("notifications", []):
                cursor.execute("""
                INSERT INTO notifications (user_id, message, is_read)
                VALUES (?, ?, ?)
                """, (user_id, notification["message"], int(notification["read"])))

        # Commit changes
        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()





def load_Products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()  
    conn.close()
    return products


def load_GallaProducts():
    conn = sqlite3.connect('galla_products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()  
    conn.close()
    return products

def load_AzzaProducts():
    conn = sqlite3.connect('azzafahmy_products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()  
    conn.close()
    return products

def loadAll_products():
    # Use the existing functions to load data
    galla_products = load_GallaProducts()
    azza_products = load_AzzaProducts()

    # Combine the results
    combined_products = galla_products + azza_products

    # Print or log the result to confirm
    print(f"Combined products count: {len(combined_products)}")

    return combined_products

def load_favorite_links(user_id):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Fetch favorite links for the logged-in user
        cursor.execute("SELECT favorite_url FROM favorites WHERE user_id = ? ORDER BY rowid", (user_id,))
        favorite_rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Return a list of favorite URLs
        return [favorite_url for (favorite_url,) in favorite_rows]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def load_notifications(email):
    notifications = []
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Fetch user_id from the email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_row = cursor.fetchone()
        
        if user_row:
            user_id = user_row[0]

            # Fetch notifications for the user
            cursor.execute("SELECT message, is_read FROM notifications WHERE user_id = ?", (user_id,))
            notification_rows = cursor.fetchall()

            for message, is_read in notification_rows:
                notifications.append({
                    "message": message,
                    "read": bool(is_read)
                })
        else:
            print(f"No user found with email {email}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

    return notifications



def save_favorite_links(fav_links):
    if 'user_id' not in session:
        return

    user_id = session['user_id']

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))

        for index, favorite in enumerate(fav_links):
            cursor.execute("""
            INSERT INTO favorites (user_id, favorite_url, favorite_order)
            VALUES (?, ?, ?)
            """, (user_id, favorite, index))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
        



def add_is_admin_column():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;")
        conn.commit()
        print("Column 'is_admin' added successfully.")
    except sqlite3.Error as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

add_is_admin_column()


def update_user_to_admin(email):
    DATABASE_FILE = "users_data.db"
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
        conn.commit()
        print(f"User {email} updated to admin.")
    except sqlite3.Error as e:
        print(f"Error updating user: {e}")
    finally:
        conn.close()

update_user_to_admin("jana.ahmed24@gmail.com")


@app.route('/update_favorites_order', methods=['POST'])
def update_favorites_order():
    try:
        data = request.get_json()
        print("Received data:", data)

        if not data or 'reorderedLinks' not in data:
            return jsonify({"success": False, "error": "Invalid data format"}), 400

        reordered_links = data['reorderedLinks']
        print("Reordered Links:", reordered_links)

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "User not found"}), 404

        save_favorite_links(reordered_links)
        return jsonify({"success": True})

    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    


def save_users(users_data):
    with open('users_data.json', 'w') as file:
        json.dump(users_data, file, indent=4)



def validate_password(password):
    pattern= r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern,password)


@app.route('/')
def index():
    # Load products from database
    products = load_Products()

    # Load notifications if the user is logged in
    notifications = []
    if 'user_id' in session:
        user_id = session['user_id']  # Use user_id (integer) stored in session
        notifications = load_notifications(user_id)

    return render_template('index.html', notifications=notifications, products=products)


@app.route('/about')
def about():
    return render_template("about.html")





def load_reviews():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews")  
    reviews = cursor.fetchall()  
    conn.close()
    return reviews

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        review = request.form["review"]

        # Insert the new review into the database
        conn = sqlite3.connect('reviews.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (name, review) VALUES (?, ?)", (name, review))
        conn.commit()
        conn.close()

        return redirect(url_for("contact"))

    # Load reviews from the database using the load_reviews function
    reviews = load_reviews()
    return render_template("contact.html", reviews=reviews)


@app.route('/review/<path:product_link>', methods=["GET", "POST"])
def review_page(product_link):
    # Retrieve the product data from the database using the product_link
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute('''SELECT * FROM products WHERE Product_Link = ?''', (product_link,))
    product = cursor.fetchone()

    if not product:
        return "Product not found", 404

    # Get reviews for this product
    reviews = get_reviews_for_product(product_link)

    if request.method == "POST":
        # Handle form submission for a new review
        user_name = request.form.get("name")
        user_review = request.form.get("review")
        rating = request.form.get("rating")

        # Insert review into the database
        insert_review(product_link, user_name, user_review, rating)
        return redirect(f'/review/{product_link}')  # Redirect to the review page to show the new review

    conn.close()

    # Pass product data to the template
    return render_template("review.html", product=product, reviews=reviews, product_link=product_link)

def insert_review(product_link, user_name, user_review, rating):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # Find the product id from the products table using the product link
    cursor.execute('''SELECT id FROM products WHERE Product_Link = ?''', (product_link,))
    product_id = cursor.fetchone()

    if not product_id:
        conn.close()
        return None  # Product not found

    product_id = product_id[0]

    # Insert the review into the reviews table
    cursor.execute('''
    INSERT INTO reviews (product_id, user_name, review_text, rating)
    VALUES (?, ?, ?, ?)
    ''', (product_id, user_name, user_review, rating))

    conn.commit()
    conn.close()

def get_reviews_for_product(product_link):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    # Get the product ID from the products table using the product link
    cursor.execute('''SELECT id FROM products WHERE Product_Link = ?''', (product_link,))
    product_id = cursor.fetchone()

    if not product_id:
        conn.close()
        return None  # Product not found

    product_id = product_id[0]

    # Retrieve all reviews for the product from the reviews table
    cursor.execute('''SELECT user_name, review_text, rating FROM reviews WHERE product_id = ?''', (product_id,))
    reviews = cursor.fetchall()

    conn.close()
    return reviews

@app.route("/filter_products", methods=["POST"])
def filter_products():
    filters = request.json
    query = filters.get("query", "").lower()
    min_price = filters.get("minPrice", 0)
    max_price = filters.get("maxPrice", float('inf'))

    selected_brands = [brand.strip().lower() for brand in filters.get("brands", [])]
    selected_product_types = [ptype.lower() for ptype in filters.get("productTypes", [])]
    selected_stone_types = [stone.lower() for stone in filters.get("stoneTypes", [])]

    # Function to load products from a single database
    def load_products_from_database(database):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        return [
            {
                "id": product[0],
                "Title": product[1],
                "Image URL": product[2],
                "Product Link": product[3],
                "Price (EGP)": product[4],
                "Description": product[5],
                "Source": product[6],
            }
            for product in products
        ]

    # Load products from both databases
    galla_products = load_products_from_database('galla_products.db')
    azza_products = load_products_from_database('azzafahmy_products.db')
    combined_products = galla_products + azza_products

    # Filter products based on filters
    filtered_products = []
    for product in combined_products:
        try:
            product_source = product.get("Source", "").strip().lower()
            price_str = product["Price (EGP)"].replace('LE', '').replace(',', '').strip()
            product_price = float(price_str)

            matches_query = query in product["Title"].lower() or query in ' '.join(product["Description"].lower().split()[:10])
            matches_price = min_price <= product_price <= max_price
            matches_brand = any(brand == product_source for brand in selected_brands) if selected_brands else True
            matches_product_type = any(ptype in product["Title"].lower() or ptype in product["Description"].lower() for ptype in selected_product_types) if selected_product_types else True
            matches_stone_type = any(stone in product["Description"].lower().split()[:10] for stone in selected_stone_types) if selected_stone_types else True

            if matches_query and matches_price and matches_brand and matches_product_type and matches_stone_type:
                filtered_products.append(product)
        except ValueError as e:
            print(f"Skipping product due to invalid data: {product}. Error: {e}")

    return jsonify(filtered_products)


@app.route('/shop')
def shop():
    if 'user_id' in session:
        user_id = session['user_id']
        favorite_links = load_favorite_links(user_id)
        return render_template("shop.html", logged_in=True, favorite_links=favorite_links)
    return render_template("shop.html", logged_in=False, favorite_links=[])


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    combined_products = loadAll_products()

    # Adjust the index based on your database schema:
    # Assuming the `products` table has columns: id, title, image_url, product_link, price_egp, description, source
    filtered_products = [
        {
            "id": product[0],
            "Title": product[1],
            "Image URL": product[2],
            "Product Link": product[3],
            "Price (EGP)": product[4],
            "Description": product[5],
            "Source": product[6],
        }
        for product in combined_products
        if query in product[1].lower() or query in ' '.join(product[5].lower().split()[:6])
    ]

    # Return the filtered products as a JSON response
    return jsonify(filtered_products)




def save_session_duration(email, duration):
    try:
        conn = sqlite3.connect("users_data.db")
        cursor = conn.cursor()
        print(f"Updating session duration for user with email: {email} by {duration} seconds.")

        # Get the user_id from email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            print(f"User ID found: {user_id}")

            # Update the session duration for the user
            cursor.execute("""
                UPDATE users
                SET session_duration = COALESCE(session_duration, 0) + ?
                WHERE id = ?
            """, (duration, user_id))

            # Commit the changes
            conn.commit()

            # Check if the session duration was updated
            cursor.execute("SELECT session_duration FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                print(f"Session duration after update: {result[0]} seconds")
            else:
                print(f"Error: User ID {user_id} not found in the database.")
        else:
            print(f"User with email {email} not found in the database.")

        conn.close()
    except sqlite3.Error as e:
        print(f"Error saving session duration: {e}")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()

            # Fetch user data from SQLite database
            cursor.execute("SELECT id, email, name, password, is_admin FROM users WHERE email = ?", (email,))
            user_row = cursor.fetchone()

            if user_row:
                user_id, stored_email, stored_name, stored_password, is_admin = user_row

                # Verify password
                if pbkdf2_sha256.verify(password, stored_password):
                    # Store user information in the session
                    session['user_id'] = user_id
                    session['user_email'] = stored_email
                    session['user_name'] = stored_name
                    session['is_admin'] = is_admin
                    session['login_time'] = datetime.now().isoformat()

                    # Redirect admins to admin page
                    if is_admin:
                        return redirect(url_for("admin_page"))

                    # Redirect regular users to the index page
                    return redirect(url_for("index"))

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

        return render_template("login.html", error_username_password="Invalid email or password")

    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['password_confirmation']
        address = request.form['address']
        year_of_birth = request.form['DOB']
        
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('signup.html', error_email_exist='Email already exists')

            # Validate password format (optional: uncomment if function exists)
            # if not validate_password(password):
            #     return render_template('signup.html', error_passwords_validation='Password must be at least 8 characters long, include at least one lowercase letter, one uppercase letter, one number, and one special character')

            # Check if passwords match
            if password != password_confirmation:
                return render_template('signup.html', error_passwords_confirmation='Passwords do not match')

            # Hash the password using pbkdf2_sha256
            hashed_password = pbkdf2_sha256.hash(password)

            # Generate verification code
            verification_code = ''.join(random.sample(uuid.uuid4().hex, 6))

            # Temporary storage for unverified user data
            unverified_user_data = {
                'name': name,
                'password': hashed_password,
                'address': address,
                'email': email,
                'DOB': year_of_birth,
                'verification_code': verification_code
            }

            # Send verification email
            mail_content = create_mail_verify_message(verification_code)
            send_email('majara.jewelry@gmail.com', email, mail_content)

            # Flash unverified user data to session
            flash(json.dumps(unverified_user_data))
            return redirect('/verify_email')

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return render_template('signup.html', error_general='An error occurred. Please try again.')
        finally:
            conn.close()

    return render_template('signup.html')


@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        # Retrieve the flashed unverified user data
        try:
            unverified_user_data = json.loads(get_flashed_messages()[0])
        except IndexError:
            return render_template('verify_email.html', error='Session expired. Please sign up again.')

        # Extract the verification code and remove it from the user data
        verification_code = unverified_user_data.pop('verification_code', None)

        # Check if the submitted code matches the verification code
        if request.form['code'] == verification_code:
            try:
                # Connect to the SQLite database
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()

                # Insert the verified user data into the `users` table
                cursor.execute("""
                    INSERT INTO users (email, name, password, address, year_of_birth)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    unverified_user_data['email'],
                    unverified_user_data['name'],
                    unverified_user_data['password'],
                    unverified_user_data['address'],
                    unverified_user_data['DOB']
                ))
                conn.commit()

                # Fetch the new user's ID
                user_id = cursor.lastrowid

                # Store user information in the session
                session['user_id'] = user_id
                session['user_name'] = unverified_user_data['name']

                return redirect('/')
            
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return render_template('verify_email.html', error='An error occurred. Please try again.')

            finally:
                conn.close()

        # Return an error if the verification code does not match
        return render_template('verify_email.html', error='Invalid verification code')

    # Render the verification page for GET requests
    return render_template('verify_email.html')

@app.route("/admin")
def admin_page():
    if 'is_admin' in session and session['is_admin']:
        return render_template("admin.html", user_name=session['user_name'])
    return redirect(url_for("login"))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        if 'login_time' in session and 'user_id' in session:
            # Calculate session duration
            login_time = datetime.fromisoformat(session['login_time'])
            session_duration = datetime.now() - login_time
            duration_in_seconds = session_duration.total_seconds()

            # Log the session duration for debugging
            print(f"Saving duration for user {session['user_id']}: {duration_in_seconds} seconds")
            
            # Save the session duration to the database
            save_session_duration(session['user_id'], duration_in_seconds)
        
        # Clear session and redirect
        session.clear()
        return redirect(url_for('index'))
    
    return render_template('logout.html')


@app.route("/favPage")
def fav_page():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    
    user_id = session['user_id']
    fav_links = load_favorite_links(user_id)  # Load favorite links from the database
    
    # Load products from both databases
    galla_products = load_GallaProducts()  # Function to load products from Galla database
    azza_products = load_AzzaProducts()  # Function to load products from Azza database
    
    # Combine the results from both databases
    combined_products = galla_products + azza_products
    
    favorite_products = [
        {
            "id": product[0],
            "Title": product[1],
            "Image URL": product[2],
            "Product Link": product[3],
            "Price (EGP)": product[4],
            "Description": product[5],
            "Source": product[6],
        }
        for product in combined_products
        if product[3] in fav_links  # Checking if the Product Link is in the user's favorites
    ]
    
    return render_template("favPage.html", favorites=favorite_products)


@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    product_url = request.json.get("product_url")
    
    if not product_url:
        return jsonify({"success": False, "error": "Product URL is missing"}), 400
    
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    user_id = session['user_id']

    # Check if the product is already in the user's favorites
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Check if the product URL is already in the favorites
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND favorite_url = ?", (user_id, product_url))
    existing_favorite = cursor.fetchone()

    if existing_favorite:
        # If the product is already in favorites, remove it
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND favorite_url = ?", (user_id, product_url))
        action = "removed"
    else:

        cursor.execute("INSERT INTO favorites (user_id, favorite_url) VALUES (?, ?)", (user_id, product_url))
        action = "added"

    conn.commit()
    conn.close()

    fav_links = load_favorite_links(user_id)  # Load updated favorites from the database
    return jsonify({"success": True, "action": action, "favorites": fav_links})


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    product_url = request.json.get("product_url")
    
    if not product_url:
        return jsonify({"success": False, "error": "Product URL is missing"}), 400

    if 'user_id' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    user_id = session['user_id']

    # Check if the product is in the user's favorites
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Check if the product URL exists in the favorites table
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND favorite_url = ?", (user_id, product_url))
    existing_favorite = cursor.fetchone()

    if not existing_favorite:
        return jsonify({"success": False, "error": "Product URL not found in favorites"}), 400

    # If the product is in favorites, remove it
    cursor.execute("DELETE FROM favorites WHERE user_id = ? AND favorite_url = ?", (user_id, product_url))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Return the updated list of favorite URLs
    fav_links = load_favorite_links(user_id)  # Load updated favorites from the database
    return jsonify({"success": True, "favorites": fav_links})



@app.route('/notifications', methods=['GET'])
def get_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    
    user_id = session['user_id']

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Fetch notifications for the logged-in user
        cursor.execute("SELECT message, is_read FROM notifications WHERE user_id = ?", (user_id,))
        notification_rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Prepare notifications as a list of dictionaries
        notifications = [{"message": message, "read": bool(is_read)} for message, is_read in notification_rows]
        
        # Pass notifications to the template
        return render_template('notifications.html', notifications=notifications)

    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# 

@app.route('/get-barchart', methods=['GET'])
def get_bar_chart():
    top_count = request.args.get('topCount', default=10, type=int)  # Get the value of topCount (default to 10)

    conn_users = sqlite3.connect('users_data.db')
    conn_galla = sqlite3.connect('galla_products.db')
    conn_azza = sqlite3.connect('azzafahmy_products.db')

    try:
        cursor_users = conn_users.cursor()
        cursor_galla = conn_galla.cursor()
        cursor_azza = conn_azza.cursor()

        # Fetch all favorite URLs and count how many times each URL is favorited
        cursor_users.execute("""
            SELECT favorite_url, COUNT(*) as favorite_count
            FROM favorites
            GROUP BY favorite_url
            ORDER BY favorite_count DESC
            LIMIT ?
        """, (top_count,))
        favorite_urls = cursor_users.fetchall()

        print(f"Favorite URLs: {favorite_urls}")  # Debug: Show the URLs returned

        favorite_products = []
        for url, count in favorite_urls:
            product = None

            # Check in Galla database
            cursor_galla.execute("""SELECT title FROM products WHERE product_link = ?""", (url,))
            product = cursor_galla.fetchone()

            # Check in Azza database if not found in Galla
            if not product:
                cursor_azza.execute("""SELECT title FROM products WHERE product_link = ?""", (url,))
                product = cursor_azza.fetchone()

            if product:
                favorite_products.append({
                    'categories': product[0],  # Product title as category
                    'values': count  # Number of times this product was favorited
                })

        print(f"Favorite Products: {favorite_products}")  # Debug: Show the resulting products

        if not favorite_products:
            return jsonify({"error": "No favorite products found."}), 404

        return jsonify(favorite_products)

    except Exception as e:
        print(f"Error: {str(e)}")  # More detailed error logging
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn_users.close()
        conn_galla.close()
        conn_azza.close()
        

# ///////////////////////////

# Clean price string and convert to float
def clean_price(price_str):
    if not price_str:
        return 0.0
    price_str = price_str.replace("LE", "").replace(",", "").strip()
    try:
        return float(price_str)
    except ValueError:
        return 0.0

# Fetch price ranges from both databases
def get_price_ranges():
    conn_galla = sqlite3.connect('galla_products.db')
    conn_azza = sqlite3.connect('azzafahmy_products.db')

    cursor_galla = conn_galla.cursor()
    cursor_azza = conn_azza.cursor()

    price_ranges = {"<10K": 0, "10K–30K": 0, "30K+": 0}

    cursor_galla.execute("SELECT price_egp FROM products")
    galla_prices = cursor_galla.fetchall()

    cursor_azza.execute("SELECT price_egp FROM products")
    azza_prices = cursor_azza.fetchall()

    all_prices = galla_prices + azza_prices

    for price_tuple in all_prices:
        price = clean_price(price_tuple[0]) if price_tuple[0] else 0.0
        if price < 10000:
            price_ranges["<10K"] += 1
        elif 10000 <= price <= 30000:
            price_ranges["10K–30K"] += 1
        else:
            price_ranges["30K+"] += 1

    conn_galla.close()
    conn_azza.close()

    return price_ranges

# Route for price range data
@app.route('/get-datapiechart')
def get_datapiechart():
    try:
        price_ranges = get_price_ranges()
        pie_data = [{"categories": key, "values": value} for key, value in price_ranges.items()]
        return jsonify(pie_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ///////////////////////////////////////



def get_product_type(title, description):
    # Define product types based on title or description
    types = ['bracelet', 'ring', 'necklace', 'earrings']
    
    # Combine title and description into one string and check for product types
    combined_text = (title + " " + description).lower()
    
    # Search for exact matches of product types as whole words
    for type_ in types:
        # Use word boundaries to ensure we match whole words only
        if re.search(r'\b' + re.escape(type_) + r'\b', combined_text):
            return type_
    
    return 'other'



def fetch_chart_data(source=None):
    # Initialize product counts
    product_counts = {
        'bracelet': 0,
        'ring': 0,
        'necklace': 0,
        'earrings': 0
    }

    try:
        # Connect to databases
        if source in ['Jewelry by Galla', None]:
            galla_conn = sqlite3.connect('galla_products.db')
            galla_cursor = galla_conn.cursor()
            galla_cursor.execute("SELECT title, description FROM products WHERE source = 'Jewelry by Galla'")
            products = galla_cursor.fetchall()
            galla_conn.close()

            for title, description in products:
                product_type = get_product_type(title, description)
                if product_type != 'other':
                    product_counts[product_type] += 1

        if source in ['Azza Fahmy', None]:
            azza_conn = sqlite3.connect('azzafahmy_products.db')
            azza_cursor = azza_conn.cursor()
            azza_cursor.execute("SELECT title, description FROM products WHERE source = 'Azza Fahmy'")
            products = azza_cursor.fetchall()
            azza_conn.close()

            for title, description in products:
                product_type = get_product_type(title, description)
                if product_type != 'other':
                    product_counts[product_type] += 1

    except Exception as e:
        return {'error': str(e)}

    return product_counts

@app.route('/get-product-type-counts', methods=['GET'])
def get_product_type_counts():
    source = request.args.get('source', None)  # Get source parameter

    if source not in [None, 'Jewelry by Galla', 'Azza Fahmy']:
        return jsonify({'error': 'Invalid source'}), 400

    data = fetch_chart_data(source)

    if 'error' in data:
        return jsonify({'error': data['error']}), 500

    chart_data = [
        {'category': product_type, 'value': count, 'source': source or 'All'}
        for product_type, count in data.items()
    ]

    return jsonify(chart_data)





@app.route('/get-session-duration-histogram')
def get_session_duration_histogram():
    connection = sqlite3.connect('users_data.db')
    cursor = connection.cursor()
    
    # Fetch user session durations
    cursor.execute('SELECT session_duration FROM users')
    data = cursor.fetchall()
    connection.close()
    
    # Convert seconds to minutes and group into ranges
    session_durations = [round(row[0] / 60, 2) for row in data if row[0] is not None]
    bins = {
        '0-5 min': 0,
        '5-10 min': 0,
        '10-20 min': 0,
        '20-30 min': 0,
        '30-60 min': 0,
        '60+ min': 0
    }
    
    for duration in session_durations:
        if duration <= 5:
            bins['0-5 min'] += 1
        elif duration <= 10:
            bins['5-10 min'] += 1
        elif duration <= 20:
            bins['10-20 min'] += 1
        elif duration <= 30:
            bins['20-30 min'] += 1
        elif duration <= 60:
            bins['30-60 min'] += 1
        else:
            bins['60+ min'] += 1
    
    histogram_data = [{"range": key, "count": value} for key, value in bins.items()]
    
    return jsonify(histogram_data)






  
@app.route('/admin')
def admin():
      return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True,port=5000)