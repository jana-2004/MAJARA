// Global Variables
let currentProducts = [];
let currentPage = 1;
const PRODUCTS_PER_PAGE = 6;

function openFilterPanel() {
    document.getElementById("filterPanel").style.width = "300px";
}

function closeFilterPanel() {
    document.getElementById("filterPanel").style.width = "0";
}


function toggleSection(sectionId, arrowId) {
    const section = document.getElementById(sectionId);
    const arrow = document.getElementById(arrowId);

    if (section.classList.contains("hidden")) {
        section.classList.remove("hidden");
        arrow.classList.remove("collapsed");
        arrow.classList.add("expanded");
    } else {
        section.classList.add("hidden");
        arrow.classList.remove("expanded");
        arrow.classList.add("collapsed");
    }
}
const priceRange = document.getElementById("priceRange");
const minPrice = document.getElementById("minPrice");
const maxPrice = document.getElementById("maxPrice");

priceRange.addEventListener("input", () => {
    const value = priceRange.value;
    minPrice.textContent = `LE 0`;
    maxPrice.textContent = `LE ${Number(value).toLocaleString()}`;
});


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

       
        const img = document.createElement("img");
        img.src = product["Image URL"];
        img.alt = product.Title;

        
        const title = document.createElement("h3");
        title.textContent = product.Title;

       
        const descriptionDiv = document.createElement("div");
        const descriptionText = product.Description;
        const descriptionPreview = descriptionText.substring(0, 100) + "..."; 
        const fullDescription = document.createElement("p");
        fullDescription.textContent = descriptionText;

        
        const readMoreLink = document.createElement("a");
        readMoreLink.href = "#";
        readMoreLink.textContent = "Read More";
        readMoreLink.style.color = "#007bff"; 

       
        readMoreLink.onclick = (e) => {
            e.preventDefault();
            descriptionDiv.innerHTML = ""; 
            descriptionDiv.appendChild(fullDescription); 
        };

        descriptionDiv.appendChild(document.createTextNode(descriptionPreview));
        descriptionDiv.appendChild(readMoreLink);

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
        productDiv.appendChild(descriptionDiv); // Append description with "Read More"
        productDiv.appendChild(price);
        productDiv.appendChild(link);
        productDiv.appendChild(heartIcon);

        resultsContainer.appendChild(productDiv);
    });
}



function renderPagination() {
    const paginationContainer = document.getElementById("pagination");
    paginationContainer.innerHTML = "";
    paginationContainer.className = "pagination-container";

    const totalPages = Math.ceil(currentProducts.length / PRODUCTS_PER_PAGE);
    const visiblePages = 5; // Maximum number of pages to display at once
    const startPage = Math.max(1, currentPage - Math.floor(visiblePages / 2));
    const endPage = Math.min(totalPages, startPage + visiblePages - 1);

    // "Previous" button
    const prevButton = document.createElement("a");
    prevButton.textContent = "«";
    prevButton.href = "#";
    prevButton.className = `pagination-link ${currentPage === 1 ? "disabled" : ""}`;
    prevButton.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            renderProducts();
            renderPagination();
        }
    });
    paginationContainer.appendChild(prevButton);

    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        const pageLink = document.createElement("a");
        pageLink.textContent = i;
        pageLink.href = "#";
        pageLink.className = `pagination-link ${i === currentPage ? "active" : ""}`;
        pageLink.addEventListener("click", (e) => {
            e.preventDefault();
            currentPage = i;
            renderProducts();
            renderPagination();
        });
        paginationContainer.appendChild(pageLink);
    }

    // "Next" button
    const nextButton = document.createElement("a");
    nextButton.textContent = "»";
    nextButton.href = "#";
    nextButton.className = `pagination-link ${currentPage === totalPages ? "disabled" : ""}`;
    nextButton.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentPage < totalPages) {
            currentPage++;
            renderProducts();
            renderPagination();
        }
    });
    paginationContainer.appendChild(nextButton);
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





function applyFilters() {
    let query = document.getElementById("searchInput").value.trim().toLowerCase();
    query = query.replace(/[^a-z0-9\s]/gi, ''); // Clean out non-alphanumeric characters

    // If query is a single character, allow it to match partial words
    if (query.length === 1) {
        query = query.trim();
    }
    const minPrice = parseFloat(document.getElementById("priceRange").min);
    const maxPrice = parseFloat(document.getElementById("priceRange").value);

    // Get selected brands, product types, and stone types
    const selectedBrands = [];
    const selectedProductTypes = [];
    const selectedStoneTypes = [];

    // Collect selected brands
    document.querySelectorAll("#brandSection input[type='checkbox']:checked").forEach(checkbox => {
        selectedBrands.push(checkbox.parentElement.textContent.trim().toLowerCase());
    });


    // Collect selected product types
    document.querySelectorAll("#productTypeSection input[type='checkbox']:checked").forEach(checkbox => {
        selectedProductTypes.push(checkbox.parentElement.textContent.trim().toLowerCase());
    });

    // Collect selected stone types
    document.querySelectorAll("#stoneTypeSection input[type='checkbox']:checked").forEach(checkbox => {
        selectedStoneTypes.push(checkbox.parentElement.textContent.trim().toLowerCase());
    });


    console.log("Selected Filters:", {
        selectedBrands,
        selectedProductTypes,
        selectedStoneTypes
    }); 

    // Prepare filter parameters
    const filters = {
        query: query,
        minPrice: minPrice,
        maxPrice: maxPrice,
        brands: selectedBrands,
        productTypes: selectedProductTypes,
        stoneTypes: selectedStoneTypes
    };

    fetch("/filter_products", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        currentProducts = data;
        currentPage = 1;
        renderProducts();
        renderPagination();
    });
}





// Listen to changes on the price range, checkboxes, or search input to update the filtered results
document.getElementById("priceRange").addEventListener("input", (e) => {
    document.getElementById("minPrice").textContent = `LE 0`;
    document.getElementById("maxPrice").textContent = `LE ${e.target.value}`;
    applyFilters();
});
document.getElementById("searchInput").addEventListener("input", applyFilters);
document.querySelectorAll(".filter-section input[type='checkbox']").forEach(checkbox => {
    checkbox.addEventListener("change", applyFilters);
});



document.getElementById('darkModeToggle').addEventListener('click', function () {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
});

window.addEventListener('DOMContentLoaded', function () {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});


// Initial Call to Fetch Products on Page Load
window.onload = handleSearch;


var modal = document.getElementById("notification-modal");
var notificationIcon = document.getElementById("notification-icon");
var closeModal = document.getElementById("close-modal");

// When the user clicks the notification icon, open the modal
notificationIcon.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
closeModal.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}