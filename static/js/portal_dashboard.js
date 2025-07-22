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

    let statusInterval;

    const simForms = document.querySelectorAll('.simulation-form');

    simForms.forEach(form => {
        console.log("simForm: ", form);
        form.addEventListener('submit', handleSimSubmit);
    });

    function handleSimSubmit(event) {
        event.preventDefault();

        if (statusInterval) clearInterval(statusInterval);

        const form = event.target;

        const statusDisplay = form.nextElementSibling.querySelector('.status-display');

        console.log('statusDisplay', statusDisplay);

        const endpoint = form.dataset.apiEndpoint;
        const simType = form.dataset.simType;
        const csrfToken = form.dataset.csrfToken;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        statusDisplay.textContent = `Starting ${simType} simulation...`;

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                if (data.task_id) {
                    statusDisplay.textContent = `Task started! ID: ${data.task_id}. Checking status...`;
                    checkTaskStatus(data.task_id, statusDisplay, simType);
                } else {
                    statusDisplay.textContent = `Error: ${data.error || 'Unknown error'}`;
                }
            })
            .catch(error => {
                statusDisplay.textContent = `Request failed: ${error}`;
            })
    }

     const resultRenderers = {
        'travel': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Destination:</strong> ${result.star_system_name} <br>
            <strong>Travel Time:</strong> ${result.travel_time_years} years
        `,
        'season': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Planet:</strong> ${result.planet_name} <br>
            <strong>Hottest Temp (Periastron):</strong> ${result.periastron_temp_k} K <br>
            <strong>Coldest Temp (Apoastron):</strong> ${result.apoastron_temp_k} K <br>
            <strong>Seasonal Difference:</strong> ${result.seasonal_temp_difference_k} K
        `,
        'default': (result) => `Task finished with an unknown result type.`
    };

    function checkTaskStatus(taskId, displayElement, simType) {
        statusInterval = setInterval(() => {
            fetch(`/tasks/status/${taskId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'SUCCESS') {
                        clearInterval(statusInterval);
                        const result = data.result;
                        const renderer = resultRenderers[simType] || resultRenderers['default'];
                        displayElement.innerHTML = renderer(result);
                    } else if (data.status === 'FAILURE') {
                        clearInterval(statusInterval);
                        displayElement.textContent = `Task Failed: ${data.result.message || 'Unknown error'}`;
                    } else {
                        displayElement.textContent = `Task ID: ${taskId} | Status: ${data.status}...`;
                    }
                })
                .catch(error => {
                    clearInterval(statusInterval);
                    displayElement.textContent = `Failed to check status: ${error}`;
                });
        }, 3000); // Check every 3 seconds
    }
});