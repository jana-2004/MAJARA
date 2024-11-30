import requests
import json
from bs4 import BeautifulSoup

# Base URL and headers
base_url = "https://jewelsbygalla.com/en-eg/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# List to store all products
all_products = []
existing_titles = set()  # To track titles that are already saved

# Load existing products from JSON file
def load_existing_products(file_path="galla_products.json"):
    global existing_titles
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            existing_products = json.load(file)
            # Add all existing titles to the set
            for product in existing_products:
                existing_titles.add(product["Title"])
            return existing_products
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Function to scrape products for a given keyword
def scrape_products(keyword):
    global all_products, existing_titles
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

            # Add product to the list
            all_products.append({
                "Title": title,
                "Image URL": image_url,
                "Product Link": product_link,
                "Price (EGP)": f"{egp_price:.2f} LE" if isinstance(egp_price, float) else egp_price,
                "Description": description,
                "Source":"Jewlery by galla"
            })

            # Add title to the set to prevent future duplicates
            existing_titles.add(title)

        # Check for "Next" button to continue pagination
        pagination = soup.find("span", class_="next")
        if not pagination or not pagination.find("a"):
            break  # Exit if there's no next page

        page += 1

# Main function to scrape all jewelry types
def main():
    global all_products
    jewelry_types = ["ring", "bracelet", "necklace", "earrings"]

    # Load existing products
    all_products = load_existing_products()

    # Scrape each type of jewelry
    for jewelry_type in jewelry_types:
        scrape_products(jewelry_type)

    # Save all unique products to the JSON file
    with open("galla_products.json", "w", encoding="utf-8") as file:
        json.dump(all_products, file, ensure_ascii=False, indent=4)

    print("Scraped data saved to 'galla_products.json'.")

if __name__ == "__main__":
    main()
