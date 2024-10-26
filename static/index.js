document.addEventListener("DOMContentLoaded", function () {
    const deleteButton = document.getElementById("delete-button");

    deleteButton.addEventListener("click", function () {
        const productId = deleteButton.getAttribute("data-product-id");

        if (confirm("Are you sure you want to delete this product?")) {
            fetch(`/edit/${productId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Product deleted successfully.");
                    window.location.href = "/home"; // Redirect after deletion
                } else {
                    alert("Failed to delete product: " + data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred. Please try again.");
            });
        }
    });
});
