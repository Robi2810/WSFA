document.addEventListener("DOMContentLoaded", function() {
    const tableRows = document.querySelectorAll("tbody tr");

    // Function to animate table rows
    function animateRows() {
        tableRows.forEach((row, index) => {
            row.style.animation = `fadeInUp 0.5s ease ${index / 5}s forwards`;
        });
    }

    // Call the animation function
    animateRows();
});