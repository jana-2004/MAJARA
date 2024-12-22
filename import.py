import sqlite3
import json

# Load the JSON data (you can replace this with loading from your actual JSON file)
json_data = '''[
    {"name": "Maysam", "review": "wow!!"},
    {"name": "jana", "review": "to7faa"},
    {"name": "Rana", "review": "ra2e3"},
    {"name": "Riwan", "review": "awesome"},
    {"name": "Bosy", "review": "good job!"},
    {"name": "sss", "review": "aaaa"}
]'''

# Parse JSON data
reviews = json.loads(json_data)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()

# Create the reviews table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    review TEXT NOT NULL
                  )''')

# Insert each review into the reviews table
for review in reviews:
    cursor.execute('''INSERT INTO reviews (name, review) VALUES (?, ?)''', (review['name'], review['review']))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Reviews have been successfully imported into the database!")
