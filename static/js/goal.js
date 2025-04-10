document.addEventListener("DOMContentLoaded", function() {
    const goalForm = document.getElementById("goalForm");
    const resultDiv = document.getElementById("result");

    goalForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent default form submission

        let formData = new FormData(goalForm);

        fetch("/set_goal/", {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultDiv.innerHTML = '<p class="success-message">Goal updated successfully! Redirecting...</p>';
                
                // Redirect to calorie calculator page after 1.5 seconds
                setTimeout(() => {
                    window.location.href = "/calories/";

                }, 1500);
            } else {
                resultDiv.innerHTML = '<p class="error-message">Failed to update goal. Please try again.</p>';
            }
        })
        .catch(error => {
            console.error("Error:", error);
            resultDiv.innerHTML = '<p class="error-message">An error occurred. Please try again.</p>';
        });
    });
});
