import sqlite3

# SQLite database name
DB_NAME = "products.db"

# Function to create the SQLite tables (products and reviews)
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table for products if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT,
        Image_URL TEXT,
        Product_Link TEXT,
        Base_Price TEXT,
        Price_EGP TEXT,
        Technical_Description TEXT,
        Material TEXT
    )
    ''')

    # Create table for reviews without the date column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        review_text TEXT,
        rating INTEGER,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    conn.commit()
    conn.close()

# Call create_table at the start to ensure the tables exist
create_table()
