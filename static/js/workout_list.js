function filterItems() {
    let input = document.getElementById("searchInput").value.toLowerCase();
    let rows = document.querySelectorAll("#workoutTable tr");

    rows.forEach(row => {
        let workoutName = row.cells[0]?.textContent.toLowerCase();
        row.style.display = workoutName && workoutName.includes(input) ? "" : "none";
    });
}
