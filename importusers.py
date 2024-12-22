import json
import sqlite3

# Path to JSON file
JSON_FILE = "users_data.json"
DB_FILE = "users_data.db"

# Load JSON data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    user_data = json.load(f)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    address TEXT NOT NULL,
    year_of_birth TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    favorite_url TEXT NOT NULL,
    favorite_order INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
""")

# Insert data into tables
for email, details in user_data.items():
    # Check if the email already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        print(f"User with email {email} already exists, skipping insertion.")
        continue  # Skip inserting this user if the email already exists
    
    # Insert user data
    cursor.execute("""
    INSERT INTO users (email, name, password, address, year_of_birth)
    VALUES (?, ?, ?, ?, ?)
    """, (email, details["name"], details["password"], details["address"], details["year_of_birth"]))
    
    # Get the user ID for the inserted record
    user_id = cursor.lastrowid
    
    # Insert favorites with order
    for order_index, favorite in enumerate(details.get("favorites", [])):
        print(f"Inserting favorite: {favorite}, order: {order_index}")  # Debugging log
        try:
            cursor.execute("""INSERT INTO favorites (user_id, favorite_url, favorite_order)
                              VALUES (?, ?, ?)""", (user_id, favorite, order_index))
        except sqlite3.Error as e:
            print(f"Error inserting favorite: {favorite}, {e}")
    
    # Insert notifications
    for notification in details.get("notifications", []):
        cursor.execute("""
        INSERT INTO notifications (user_id, message, is_read)
        VALUES (?, ?, ?)
        """, (user_id, notification["message"], int(notification["read"])))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Migration completed successfully!")
