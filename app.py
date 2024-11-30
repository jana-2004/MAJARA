from flask import Flask, request, render_template, jsonify, redirect, url_for,session
from db import db
import re
from passlib.hash import pbkdf2_sha256   
import uuid
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 

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
    try:
        with open("favID.json", "r", encoding="utf-8") as fav_file:
            fav_links = json.load(fav_file)
    except (FileNotFoundError, json.JSONDecodeError):
        fav_links = []
    return fav_links

def validate_password(password):
    pattern= r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(pattern,password)

def get_user_by_email(email):
    for user in db.values():
        if user['email'] == email:
            return user
    return None

def save_favorite_links(fav_links):
    with open("favID.json", "w", encoding="utf-8") as fav_file:
        json.dump(fav_links, fav_file, ensure_ascii=False, indent=4)


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
    return render_template('shop.html')


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


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user=get_user_by_email(email)
        if user and pbkdf2_sha256.verify(password,user['password']):
            print(session.get('user_name'))
            session['user_name'] = user['name']

            return redirect('/')
        else:
            return render_template('login.html',error_username_password='invalid username or password')    

    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['password_confirmation']
        address = request.form['address']
        year=request.form['DOB']
        



        for user in db.values():
            if user['email']==email:
                return render_template('signup.html', error_email_exist='Email already exists')


        if not validate_password(password):
            return render_template('signup.html',error_passwords_validation='Password must be at least 8 characters long, include at least one lowercase letter,one uppercase letter, one number, and one special character')        

        if password != password_confirmation:
            return render_template('signup.html', error_passwords_confirmation='Passwords do not match')    
        hashed_password = pbkdf2_sha256.hash(password)
        id = uuid.uuid4().hex
        db[id]= {
            'name': name,
            'password': hashed_password,
            'address': address,
            'email':email,
            'DOB':year
        }
        print(db)
        return redirect('/')  
    return render_template('signup.html')


@app.route("/favorites")
def favorites():
    fav_links = load_favorite_links()
    combined_products = loadAll_products()

    # Filter products that are in the favorite links list
    favorite_products = [product for product in combined_products if product["Product Link"] in fav_links]
    return jsonify(favorite_products)

@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    product_url = request.json.get("product_url")
    fav_links = load_favorite_links()

    # Add or remove product link from favorites
    if product_url in fav_links:
        fav_links.remove(product_url)  # Remove from favorites
    else:
        fav_links.append(product_url)  # Add to favorites

    # Save updated favorite links
    save_favorite_links(fav_links)

    return jsonify({"success": True})


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    product_url = request.json.get("product_url")
    fav_links = load_favorite_links()

    # Remove the product link from favorites
    if product_url in fav_links:
        fav_links.remove(product_url)

    # Save updated favorite links
    save_favorite_links(fav_links)

    return jsonify({"success": True})

@app.route("/favPage")
def fav_page():
    fav_links = load_favorite_links()
    combined_products = loadAll_products()

    # Filter products that are in the favorite links list
    favorite_products = [product for product in combined_products if product["Product Link"] in fav_links]
    return render_template("favPage.html", favorites=favorite_products)

if __name__ == '__main__':
    app.run(debug=True)