import requests
from bs4 import BeautifulSoup
import json

# Base URL and headers
base_url = "https://eg.azzafahmy.com/search"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# List to store product details
products = []

# Function to scrape Azza Fahmy products
def scrape_azza_products(keyword):
    page = 1
    while True:
        print(f"Scraping '{keyword}' - Page {page}...")

        params = {"q": keyword, "page": page}
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}, stopping.")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        product_cards = soup.find_all("product-card", class_="product-card")

        if not product_cards:
            print(f"No products found on page {page} for '{keyword}', stopping.")
            break

        for card in product_cards:
            # Extract product title
            title_tag = card.find("a", class_="product-title")
            title = title_tag.text.strip() if title_tag else "No title available"

            # Extract product image
            img_tag = card.find("img", class_="product-card__image")
            image_url = "https:" + img_tag["src"] if img_tag else "No image available"

            # Extract product link
            link_tag = card.find("a", class_='product-card__media')
            product_link = "https://eg.azzafahmy.com" + link_tag["href"] if link_tag else "No link available"

            # Extract base price
           # Extract prices
            base_price_tag = card.find("sale-price", class_="text-subdued")
            if base_price_tag:
                for span in base_price_tag.find_all("span"):
                    span.extract()
                base_price = base_price_tag.get_text(strip=True)
            else:
                base_price = "Sold out"

            # Now, for each product, send a request to get more details (description and material)
            product_details = {
                'Title': title,
                'Image URL': image_url,
                'Product Link': product_link,
                'Price (EGP)': base_price,
                'Source': "Azza Fahmy"
            }

            # Send a request to the product page to get additional details (Technical Description and Material)
            product_page_response = requests.get(product_link, headers=headers)
            if product_page_response.status_code == 200:
                product_page_soup = BeautifulSoup(product_page_response.content, "html.parser")

                # Extract the Technical Description
                tech_desc_tag = product_page_soup.find("p", string="Technical Description")
                tech_description = "No technical description available"
                if tech_desc_tag:
                    tech_desc = tech_desc_tag.find_next("div", class_="prose")
                    if tech_desc:
                        tech_description = tech_desc.get_text(strip=True)

                
                # Add the extracted details
                product_details['Description'] = tech_description
            else:
                product_details['Description'] = "No technical description available"

            # Append product details to the list
            products.append(product_details)

        # Find the next page link in the pagination
        pagination_nav = soup.find("nav", class_="pagination")

        if pagination_nav:
            next_page = pagination_nav.find("a", {"rel": "next"})  # Look for the 'next' page link
            if next_page:
                page += 1  # Go to the next page
            else:
                print(f"No next page found for '{keyword}', stopping.")
                break  # No next page, stop scraping
        else:
            print(f"Pagination not found for '{keyword}', stopping.")
            break  # No pagination element, stop scraping

# Main function to start scraping
def main():
    jewelry_types = ["ring", "bracelet", "necklace", "earrings"]

    # Scrape each type of jewelry from Azza Fahmy
    for jewelry_type in jewelry_types:
        scrape_azza_products(jewelry_type)

    # Save the results to a JSON file
    with open("azzafahmy_products.json", "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

    print("Scraped data saved to 'azzafahmy_products.json'.")

if __name__ == "__main__":
    main()
