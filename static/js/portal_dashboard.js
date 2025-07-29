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

    const simForms = document.querySelectorAll('.simulation-form');
    const historyTableBody = document.getElementById('history-table-body');

    simForms.forEach(form => {
        form.addEventListener('submit', handleSimSubmit);
    });

    let intervalId;

    function handleSimSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const errorDisplay = document.querySelector('.form-error-display');
        errorDisplay.innerHTML = '';

        const endpoint = form.dataset.apiEndpoint;
        const csrfToken = form.dataset.csrfToken;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(data),
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }

                return response.json().then(apiError=> {
                    throw apiError;
                });
            })
            .then(data => {
                if (data.task_id) {
                    updateHistoryTable(true);
                    intervalId = setInterval(updateHistoryTable, 5000);
                } else {
                    // unlikely fallback
                    displayError(errorDisplay, { details: 'An unknown error occurred.' });
                }
            })
            .catch(error => {
                // network error, fetch fails, api errors
                displayError(errorDisplay, error);
            });
    }

    function displayError(element, error) {
        let errorHtml = '<div class="p-4 rounded-md bg-red-100 text-red-800 mb-8" role="alert">';

        // api error
        if (error && error.details) {
            if (typeof error.details === 'object') {
                for (const [field, messages] of Object.entries(error.details)) {
                    const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
                    errorHtml += `<p><strong>${fieldName}:</strong> ${messages.join(', ')}</p>`;
                }
            } else {
                errorHtml += `<p>${error.details}</p>`;
            }
        } else {
            // unexpected errors, network failures
            errorHtml += `<p>An unexpected error occurred: ${error.message}. Please try again.</p>`;
        }

        errorHtml += '</div>';
        element.innerHTML = errorHtml;

        setTimeout(() => {
            element.innerHTML = '';
        }, 7000);
    }

    function formatResult(simType, resultData) {
        if (!resultData) return 'N/A';
        if (resultData.error) {
            return `<span class="text-red-600">${resultData.error}</span>`;
        }
        const renderer = resultRenderers[simType] || resultRenderers['default'];
        return renderer(resultData);
    }

    function updateHistoryTable(simulationTriggered) {
        fetch('/simulations/history/')
            .then(response => response.json())
            .then(data => {
                if (!historyTableBody || !data) return;

                if (data.results.length === 0) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">No simulation history found.</td></tr>`;
                    return;
                }

                // stop polling
                if (!simulationTriggered) {
                    const latestSimulationRun = data.results[0];

                    if (latestSimulationRun.status !== 'PENDING' && intervalId) {
                        clearInterval(intervalId)
                    }
                }

                let tableHtml = '';
                data.results.forEach(run => {
                    tableHtml += `
                        <tr class="text-sm">
                            <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">${run.simulation_type}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-gray-500">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                    ${run.status === 'SUCCESS' ? 'bg-green-100 text-green-800' : ''}
                                    ${run.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' : ''}
                                    ${run.status === 'FAILURE' ? 'bg-red-100 text-red-800' : ''}">
                                    ${run.status}
                                </span>
                            </td>
                            <td class="px-6 py-4 text-gray-500">${formatResult(run.simulation_type, run.result)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-gray-500">${new Date(run.created_at).toLocaleString()}</td>
                        </tr>
                    `;
                });
                historyTableBody.innerHTML= tableHtml;
            })
            .catch(error => {
                if (historyTableBody) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-sm text-red-500">Error loading history. Are you logged in?</td></tr>`;
                }
            });
    }

    updateHistoryTable();

    const resultRenderers = {
        'TRAVEL_TIME': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Destination:</strong> ${result.star_system_name} <br>
            <strong>Travel Time:</strong> ${result.travel_time_years} years
        `,
        'SEASONAL_TEMPS': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Planet:</strong> ${result.planet_name} <br>
            <strong>Hottest Temp (Periastron):</strong> ${result.periastron_temp_k} K <br>
            <strong>Coldest Temp (Apoastron):</strong> ${result.apoastron_temp_k} K <br>
            <strong>Seasonal Difference:</strong> ${result.seasonal_temp_difference_k} K
        `,
         'TIDAL_LOCKING': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Planet:</strong> ${result.planet_name} <br>
            <strong>Star:</strong> ${result.star_name} <br>
            <strong>Is Likely Tidally Locked:</strong> ${result.is_locked ? 'True' : 'False'} <br>
            <strong>Locking Timescale Years:</strong> ${result.locking_timescale_years} <br>
            <strong>Star Age Years:</strong> ${result.star_age_years} <br>
            <strong>Conclusion:</strong> ${result.conclusion}
         `,
         'STELLAR_LIFETIME': (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Star:</strong> ${result.star_name} <br>
            <strong>Star Solar Mass:</strong> ${result.star_mass_solar} <br>
            <strong>Star Age:</strong> ${result.star_age_gyr} GYR <br>
            <strong>Estimated Total Lifetime:</strong> ${result.estimated_total_lifetime_gyr} GYR <br>
            <strong>Estimated Remaining Lifetime:</strong> ${result.estimated_remaining_lifetime_gyr} GYR <br>
            <strong>Percent Lifespan Complete:</strong> ${result.percent_lifespan_complete} % <br>
            <strong>Conclusion:</strong> ${result.conclusion}
         `,
         'default': (result) => `Task finished with an unknown result type.`
    };
});