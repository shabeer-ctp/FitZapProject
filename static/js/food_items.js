function filterItems() {
    let input = document.getElementById("searchInput").value.trim().toLowerCase(); // Trim spaces
    let rows = document.querySelectorAll("#foodTable tr");

    rows.forEach(row => {
        let foodCell = row.cells[0]; // Get the first column (Food Item Name)
        if (foodCell) {
            let foodName = foodCell.textContent.trim().toLowerCase();
            row.style.display = foodName.includes(input) ? "" : "none";
        }
    });
}

