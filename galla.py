import requests
import sqlite3
from bs4 import BeautifulSoup

# Base URL and headers
base_url = "https://jewelsbygalla.com/en-eg/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# List to store all products
existing_titles = set()  # To track titles that are already saved

# Connect to SQLite database (or create it if not exists)
def connect_db():
    conn = sqlite3.connect("galla_products.db")
    return conn

# Create products table if it doesn't exist
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            image_url TEXT,
            product_link TEXT,
            price_egp TEXT,
            description TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to insert product into the database
def insert_product(product):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO products (title, image_url, product_link, price_egp, description, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product["Title"], product["Image URL"], product["Product Link"], product["Price (EGP)"], product["Description"], product["Source"]))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Skip if product with the same title already exists (unique constraint)
    conn.close()

# Function to scrape products for a given keyword
def scrape_products(keyword):
    global existing_titles
    page = 1

    while True:
        print(f"Scraping '{keyword}' - Page {page}...")

        # Update query parameter with the current keyword and page
        params = {"q": keyword, "page": page}
        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page {page} for '{keyword}', stopping.")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        product_cards = soup.find_all("div", class_="grid__item-image-wrapper")
        if not product_cards:
            print(f"No products found on page {page} for '{keyword}', stopping.")
            break

        for card in product_cards:
            # Extract product details
            title_tag = card.find("div", class_="grid-product__title")
            title = title_tag.text.strip() if title_tag else "No title available"

            # Skip product if the title already exists in the set
            if title in existing_titles:
                continue

            link_tag = card.find("a", class_="grid-product__link")
            product_link = "https://jewelsbygalla.com" + link_tag["href"] if link_tag else "No link available"

            img_tag = card.find("img", class_="image-style--")
            image_url = "https:" + img_tag["src"] if img_tag else "No image available"

            base_price_tag = card.find('span', class_='money')
            if base_price_tag:
                base_price = base_price_tag.get_text(strip=True)
                egp_price = float(base_price.replace('Dhs.', '').replace(',', '').strip()) * 13.5
            else:
                egp_price = "Unavailable"

            # Fetch product description from the product page
            product_page_response = requests.get(product_link, headers=headers)
            if product_page_response.status_code == 200:
                product_page_soup = BeautifulSoup(product_page_response.content, "html.parser")
                description_divs = product_page_soup.find_all("div", class_="rte")
                description = (
                    " ".join(p.get_text(strip=True) for div in description_divs for p in div.find_all("p"))
                    if description_divs else "No description available"
                )
            else:
                description = "Go to the website to know more about it"

            # Add product to the database
            product = {
                "Title": title,
                "Image URL": image_url,
                "Product Link": product_link,
                "Price (EGP)": f"{egp_price:.2f} LE" if isinstance(egp_price, float) else egp_price,
                "Description": description,
                "Source": "Jewelry by Galla"
            }
            insert_product(product)

            # Add title to the set to prevent future duplicates
            existing_titles.add(title)

        # Check for "Next" button to continue pagination
        pagination = soup.find("span", class_="next")
        if not pagination or not pagination.find("a"):
            break  # Exit if there's no next page

        page += 1

# Main function to scrape all jewelry types
def main():
    global existing_titles
    jewelry_types = ["ring", "bracelet", "necklace", "earrings"]

    # Create the table if not exists
    create_table()

    # Scrape each type of jewelry
    for jewelry_type in jewelry_types:
        scrape_products(jewelry_type)

    print("Scraped data has been saved to the database.")

if __name__ == "__main__":
    main()
