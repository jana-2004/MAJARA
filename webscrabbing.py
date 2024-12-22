import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup

# SQLite database name
DB_NAME = "products.db"

# Function to create the SQLite table
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create a table for storing product details (if it doesn't already exist)
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
    conn.commit()
    conn.close()

# Function to insert product details into the database
def insert_product(product_details):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert product details into the database
    cursor.execute('''
    INSERT INTO products (Title, Image_URL, Product_Link, Base_Price, Price_EGP, Technical_Description, Material)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        product_details['Title'],
        product_details['Image URL'],
        product_details['Product Link'],
        product_details['Base Price'],
        product_details['Price (EGP)'],
        product_details['Technical Description'],
        product_details['Material']
    ))

    conn.commit()
    conn.close()

# Call create_table() at the beginning of the script to ensure the table is created
create_table()

# Function to scrape Lazurde product details
base_url = "https://jewelsbygalla.com/en-eg/search"
params = {
    "q": "necklace",  # Corrected the spelling of "necklace"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# Send request
response = requests.get(base_url, params=params, headers=headers)
if response.status_code != 200:
    print(f"Request failed with status code: {response.status_code}")

# Parse the HTML of the main page
soup = BeautifulSoup(response.content, "html.parser")

# List to store product details
products = []

# Extract product details
product_cards = soup.find_all("div", class_="grid__item-image-wrapper")

for card in product_cards:
    # Extract title
    title_tag = card.find("div", class_="grid-product__title")
    title = title_tag.text.strip() if title_tag else "No title available"

    # Extract image
    img_tag = card.find("img", class_="image-style--")
    image_url = "https:" + img_tag["src"] if img_tag else "No image available"

    # Extract product link
    link_tag = card.find("a", class_='grid-product__link')
    product_link = "https://jewelsbygalla.com" + link_tag["href"] if link_tag else "No link available"

    # Extract prices
    exchange_by = 13.50
    base_price_tag = card.find('span', class_='money')

    if base_price_tag:
        base_price = base_price_tag.get_text(strip=True)
        if 'Dhs.' in base_price:
            aed_price = float(base_price.replace('Dhs.', '').replace(',', '').strip())
            egp_price = aed_price * exchange_by
        else:
            egp_price = "Unavailable"
    else:
        base_price = "Sold out"
        egp_price = "Unavailable"

    # Now, for each product, send a request to get more details (description and material)
    product_details = {}
    product_details['Title'] = title
    product_details['Image URL'] = image_url
    product_details['Product Link'] = product_link
    product_details['Base Price'] = base_price
    product_details['Price (EGP)'] = f"{egp_price:.2f}" if isinstance(egp_price, float) else egp_price

    # Send a request to the product page to get additional details
    product_page_response = requests.get(product_link, headers=headers)
    if product_page_response.status_code == 200:
        product_page_soup = BeautifulSoup(product_page_response.content, "html.parser")

        # Locate the specific 'rte' div with the desired content
        description_divs = product_page_soup.find_all("div", class_="rte")
        target_div = None

        # Iterate through all 'rte' divs to find the one containing the expected keywords
        for div in description_divs:
            if div.find("p", string=lambda text: text and "Length:" in text):
                target_div = div
                break

        if target_div:
            paragraphs = target_div.find_all("p")
            tech_description = "No technical description available"
            material = "No material information available"

            if paragraphs:
                # Categorize paragraphs into description and material
                material_info = []
                description_text = ""
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text.startswith("Length:") or "Gold Color" in text or "Karats" in text or "Stones" in text or "Total Stone Carat" in text:
                        material_info.append(text)
                    else:
                        description_text = text  # Assume the last narrative-style paragraph is the description

                # Join material details
                if material_info:
                    material = " ".join(material_info)
                # Use the identified description
                if description_text:
                    tech_description = description_text

            product_details['Technical Description'] = tech_description
            product_details['Material'] = material
        else:
            product_details['Technical Description'] = "Go to the website to know more about it"
            product_details['Material'] = "Go to the website to know more about it"
    else:
        product_details['Technical Description'] = "Go to the website to know more about it"
        product_details['Material'] = "Go to the website to know more about it"

    # Append product details to the list
    products.append(product_details)

    # Insert product details into SQLite database
    insert_product(product_details)

# Optionally, create a DataFrame from the product details for further processing
df = pd.DataFrame(products)

# Print the DataFrame (if needed)
print(df)

print("Scraped data saved to SQLite database.")
