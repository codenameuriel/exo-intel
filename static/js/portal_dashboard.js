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
    const simMessageDisplay = document.getElementById('simulation-message-display');

    simForms.forEach(form => {
        form.addEventListener('submit', handleSimSubmit);
    });

    let pollingIntervalId = null;
    let historyPrevUrl = null;
    let historyNextUrl = null;
    const initialHistoryUrl = '/simulations/history/';

    const prevButtons = document.querySelectorAll('.history-prev-btn');
    const nextButtons = document.querySelectorAll('.history-next-btn');
    const pageInfoSpans = document.querySelectorAll('.history-page-info');

    prevButtons.forEach(btn => btn.addEventListener('click', () => {
        if (historyPrevUrl) {
            updateHistoryTable(historyPrevUrl);
        }
    }));

    nextButtons.forEach(btn => btn.addEventListener('click', () => {
        if (historyNextUrl) {
            updateHistoryTable(historyNextUrl);
        }
    }));

    function handleSimSubmit(event) {
        event.preventDefault();

        const form = event.target;
        simMessageDisplay.innerHTML = '';

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
                    displaySimulationMessage(`Simulation started successfully! Task ID: ${data.task_id}`, 'success');
                    startPolling();
                } else {
                    // unlikely fallback
                    displaySimulationMessage('An unknown error occurred.', 'error');
                }
            })
            .catch(error => {
                // network error, fetch fails, api errors
                displaySimulationMessage(error, 'error');
            });
    }

    function updateHistoryTable(url = initialHistoryUrl) {
        fetch(url)
            .then(response => {
                if (!response.ok) return null;
                return response.json()
            })
            .then(data => {
                if (!historyTableBody || !data) return;

                if (data.results.length === 0) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">No simulation history found.</td></tr>`;
                    return;
                }

                historyPrevUrl = data.previous;
                historyNextUrl = data.next;
                updatePaginationControls(data);

                let isAnySimRunning = false;

                let tableHtml = '';
                data.results.forEach(run => {
                    if (run.status === 'PENDING') {
                        isAnySimRunning = true;
                    }
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

                if (isAnySimRunning) {
                    startPolling();
                } else {
                    stopPolling();
                }
            })
            .catch(error => {
                if (historyTableBody) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-sm text-red-500">Error loading history. Are you logged in?</td></tr>`;
                }
                stopPolling();
            });
    }

    updateHistoryTable();

    function updatePaginationControls(data) {
        const totalItems = data.count;
        const pageSize = 25; // DRF pagination setting
        const totalPages = Math.ceil(totalItems / pageSize);

        let currentPage = 1;
        if (data.previous) {
            const urlParams = new URLSearchParams(new URL(data.previous).search);
            currentPage = parseInt(urlParams.get('page') || '1') + 1;
        } else if (data.next) {
            currentPage = 1;
        } else if (totalItems > 0) {
            currentPage = 1;
        }

        pageInfoSpans.forEach(span => {
            if (totalItems > 0) {
                span.textContent = `Page ${currentPage} of ${totalPages}`;
            } else {
                span.textContent = '';
            }
        });

        prevButtons.forEach(btn => btn.disabled = !data.previous);
        nextButtons.forEach(btn => btn.disabled = !data.next);
    }

    function startPolling() {
        if (!pollingIntervalId) {
            pollingIntervalId = setInterval(updateHistoryTable, 2000);
        }
    }

    function stopPolling() {
        if (pollingIntervalId) {
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
        }
    }

    function displaySimulationMessage(data, level) {
        if (!simMessageDisplay) return;

        let messageHtml = '';
        const bgColor = level === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';

        let messageContent = '';

        // Handle API errors
        if (level === 'error' && data && data.details) {
            const details = data.details;
            if (typeof details === 'object' && details !== null) {
                let detailMessages = [];
                for (const [field, messages] of Object.entries(details)) {
                    const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
                    detailMessages.push(`<strong>${fieldName}:</strong> ${messages.join(', ')}`);
                }
                messageContent = detailMessages.join('<br>');
            } else {
                messageContent = details;
            }
        } else if (level === 'success') {
            messageContent = data;
        } else {
            messageContent = 'An unexpected error occurred. Please try again.';
        }

        messageHtml = `<div class="p-4 rounded-md ${bgColor}" role="alert">${messageContent}</div>`;
        simMessageDisplay.innerHTML = messageHtml;

        setTimeout(() => {
            if (simMessageDisplay) simMessageDisplay.innerHTML = '';
        }, 4000);
    }

    function formatResult(simType, resultData) {
        if (!resultData) return 'N/A';
        if (resultData.error) {
            return `<span class="text-red-600">${resultData.error}</span>`;
        }
        const renderer = resultRenderers[simType] || resultRenderers['default'];
        return renderer(resultData);
    }

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