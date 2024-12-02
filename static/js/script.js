// Global Variables
let currentProducts = [];
let currentPage = 1;
const PRODUCTS_PER_PAGE = 6;

// Function to Fetch Products based on Search Query
function handleSearch() {
    const query = document.getElementById("searchInput").value.trim().toLowerCase();

    fetch(`/search?q=${query}`)
        .then(response => response.json())
        .then(data => {
            currentProducts = data;
            currentPage = 1;
            renderProducts();
            renderPagination();
        });
}

// Function to Render Products on the Current Page
function renderProducts() {
    const resultsContainer = document.getElementById("results");
    resultsContainer.innerHTML = "";

    const startIndex = (currentPage - 1) * PRODUCTS_PER_PAGE;
    const endIndex = startIndex + PRODUCTS_PER_PAGE;
    const productsToDisplay = currentProducts.slice(startIndex, endIndex);

    productsToDisplay.forEach(product => {
        const productDiv = document.createElement("div");
        productDiv.className = "product";

        // Product Image
        const img = document.createElement("img");
        img.src = product["Image URL"];
        img.alt = product.Title;

        // Product Title
        const title = document.createElement("h3");
        title.textContent = product.Title;

        // Product Description
        const description = document.createElement("p");
        description.textContent = product.Description.substring(0, 100) + "...";

        // Product Price
        const price = document.createElement("p");
        price.textContent = `Price: ${product["Price (EGP)"]}`;

        // Product Link
        const link = document.createElement("a");
        link.href = product["Product Link"];
        link.textContent = "View Product";
        link.target = "_blank";

        // Favorite Heart Icon
        const heartIcon = document.createElement("span");
        heartIcon.className = "heart";
        heartIcon.innerHTML = "&#10084;"; // Heart symbol

        // Check if the product is in favorites
        if (favoriteLinks.includes(product["Product Link"])) {
            heartIcon.classList.add("liked");
        }

        // Toggle favorite on click
        heartIcon.onclick = () => toggleFavorite(product["Product Link"], heartIcon);

        // Append Elements to Product Div
        productDiv.appendChild(img);
        productDiv.appendChild(title);
        productDiv.appendChild(description);
        productDiv.appendChild(price);
        productDiv.appendChild(link);
        productDiv.appendChild(heartIcon);

        resultsContainer.appendChild(productDiv);
    });
}

// Function to Render Pagination Links
function renderPagination() {
    const paginationContainer = document.getElementById("pagination");
    paginationContainer.innerHTML = "";

    const totalPages = Math.ceil(currentProducts.length / PRODUCTS_PER_PAGE);

    for (let i = 1; i <= totalPages; i++) {
        const pageLink = document.createElement("a");
        pageLink.textContent = i;
        pageLink.href = "#";
        pageLink.className = i === currentPage ? "active" : "";

        pageLink.addEventListener("click", (e) => {
            e.preventDefault();
            currentPage = i;
            renderProducts();
            renderPagination();
        });

        paginationContainer.appendChild(pageLink);
    }
}
function removeFromFavorites(productUrl) {
    console.log("Removing:", productUrl); // Debugging log
    fetch('/remove_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_url: productUrl }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Removed from favorites!");
            location.reload(); // Reload the page to refresh the favorites list
        } else {
            alert("Failed to remove favorite.");
        }
    })
    .catch(error => {
        console.error("Error removing favorite:", error);
    });
}





// Function to toggle favorite status of a product
function toggleFavorite(productUrl, heartIcon) {
    fetch("/toggle_favorite", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ product_url: productUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            heartIcon.classList.toggle("liked");
            // Update the favoriteLinks in real time
            if (data.action === "added") {
                favoriteLinks.push(productUrl);
            } else {
                favoriteLinks = favoriteLinks.filter(link => link !== productUrl);
            }
        }
    });
}



// Initial Call to Fetch Products on Page Load
window.onload = handleSearch;
