document.addEventListener('DOMContentLoaded', function() {
    // auto-hiding messages
    const messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        // Wait for 3 seconds (3000 milliseconds)
        setTimeout(function() {
            // Start fading the message out
            messageContainer.style.opacity = '0';

            // After the fade-out transition (500ms), hide it completely
            setTimeout(function() {
                messageContainer.style.display = 'none';
            }, 500);
        }, 3000);
    }

    const simForm = document.getElementById('simulation-form');
    const statusDisplay = document.getElementById('status-display');
    let statusInterval;

    simForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Clear any previous status checks
        if (statusInterval) {
            clearInterval(statusInterval);
        }

        const formData = new FormData(simForm);
        const data = {
            star_system_id: formData.get('star_system_id'),
            speed_percentage: formData.get('speed_percentage'),
        };

        const csrfToken = simForm.dataset.csrfToken;

        statusDisplay.textContent = 'Starting simulation...';

        // Send the asynchronous POST request to our API endpoint
        fetch('/simulations/travel-time/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                statusDisplay.textContent = `Task started! ID: ${data.task_id}. Checking status...`;
                // Start polling the status endpoint
                checkTaskStatus(data.task_id);
            } else {
                statusDisplay.textContent = `Error: ${data.error || 'Unknown error'}`;
            }
        })
        .catch(error => {
            statusDisplay.textContent = `Request failed: ${error}`;
        });
    });

    function checkTaskStatus(taskId) {
        statusInterval = setInterval(() => {
            fetch(`/tasks/status/${taskId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'SUCCESS') {
                        clearInterval(statusInterval);
                        const result = data.result;
                        statusDisplay.innerHTML = `
                            <strong>Status:</strong> SUCCESS <br>
                            <strong>Destination:</strong> ${result.star_system_name} <br>
                            <strong>Travel Time:</strong> ${result.travel_time_years} years
                        `;
                    } else if (data.status === 'FAILURE') {
                        clearInterval(statusInterval);
                        statusDisplay.textContent = `Task Failed: ${data.result.error || 'Unknown error'}`;
                    } else {
                        statusDisplay.textContent = `Task ID: ${taskId} | Status: ${data.status}...`;
                    }
                })
                .catch(error => {
                    clearInterval(statusInterval);
                    statusDisplay.textContent = `Failed to check status: ${error}`;
                });
        }, 3000); // Check every 3 seconds
    }
});