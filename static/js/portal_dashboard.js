document.addEventListener('DOMContentLoaded', function () {
    // auto-hiding messages
    const messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        setTimeout(function () {
            messageContainer.style.opacity = '0';
            setTimeout(function () {
                messageContainer.style.display = 'none';
            }, 500);
        }, 3000);
    }

    initMissionClock();

    const simForms = document.querySelectorAll('.simulation-form');
    const historyTableBody = document.getElementById('history-table-body');
    const simMessageDisplay = document.getElementById('simulation-message-display');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    const simulationTypeMap = {
        travel: 'TRAVEL_TIME',
        season: 'SEASONAL_TEMPS',
        tidal: 'TIDAL_LOCKING',
        lifetime: 'STAR_LIFETIME',
    };

    const simulationTypeLabels = {
        TRAVEL_TIME: 'Travel Time',
        SEASONAL_TEMPS: 'Seasonal Temps',
        TIDAL_LOCKING: 'Tidal Locking',
        STAR_LIFETIME: 'Star Lifetime',
    };

    const activeSimulationForms = new Map();
    const minimumVisibleStateMs = 1500;
    // Backend marks runs stale after two minutes and Beat reconciles once per minute.
    // This extra minute keeps browser polling bounded while allowing reconciliation to land.
    const pendingPollingMaxAgeMs = 3 * 60 * 1000;

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

    function initMissionClock() {
        const pageHeader = document.querySelector('header.mb-7');
        const headerRow = pageHeader?.firstElementChild;
        if (!headerRow || document.getElementById('mission-clock')) return;

        const clock = document.createElement('div');
        clock.id = 'mission-clock';
        clock.setAttribute('role', 'group');
        clock.setAttribute('aria-label', 'Local date and time');

        Object.assign(clock.style, {
            alignSelf: 'flex-start',
            flexShrink: '0',
            width: '12.75rem',
            padding: '0.7rem 0.85rem 0.65rem',
            border: '1px solid rgba(103, 232, 249, 0.11)',
            borderRadius: '0.5rem',
            background: 'rgba(3, 10, 20, 0.48)',
            boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.012)',
            backdropFilter: 'blur(10px)',
            fontFamily: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
        });

        const dateLine = document.createElement('div');
        dateLine.dataset.clockDate = 'true';
        Object.assign(dateLine.style, {
            color: '#607985',
            fontSize: '0.6rem',
            fontWeight: '500',
            letterSpacing: '0.14em',
            lineHeight: '1',
            textAlign: 'left',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
        });

        const timeRow = document.createElement('div');
        Object.assign(timeRow.style, {
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'flex-start',
            gap: '0.28rem',
            marginTop: '0.45rem',
            paddingTop: '0.4rem',
            borderTop: '1px solid rgba(103, 232, 249, 0.07)',
        });

        const timeLine = document.createElement('span');
        timeLine.dataset.clockTime = 'true';
        Object.assign(timeLine.style, {
            color: '#b8d5dc',
            fontSize: '0.85rem',
            fontWeight: '500',
            letterSpacing: '0.045em',
            lineHeight: '1',
            textAlign: 'left',
            whiteSpace: 'nowrap',
            fontVariantNumeric: 'tabular-nums',
        });

        const zoneLine = document.createElement('span');
        zoneLine.dataset.clockZone = 'true';
        Object.assign(zoneLine.style, {
            color: '#4d6572',
            fontSize: '0.55rem',
            fontWeight: '600',
            letterSpacing: '0.08em',
            lineHeight: '1',
            textAlign: 'left',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
        });

        timeRow.append(timeLine, zoneLine);
        clock.append(dateLine, timeRow);
        headerRow.appendChild(clock);

        function updateClock() {
            const now = new Date();

            const dateParts = new Intl.DateTimeFormat(undefined, {
                weekday: 'short',
                month: 'short',
                day: '2-digit',
                year: 'numeric',
            }).formatToParts(now);

            const getDatePart = type => dateParts.find(part => part.type === type)?.value || '';
            dateLine.textContent = `${getDatePart('weekday')} · ${getDatePart('month')} ${getDatePart('day')} ${getDatePart('year')}`;

            timeLine.textContent = new Intl.DateTimeFormat(undefined, {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true,
            }).format(now);

            const zoneParts = new Intl.DateTimeFormat(undefined, {
                timeZoneName: 'short',
            }).formatToParts(now);
            zoneLine.textContent = zoneParts.find(part => part.type === 'timeZoneName')?.value || 'LOCAL';
        }

        updateClock();
        setInterval(updateClock, 1000);
    }

    function getSubmitButton(form) {
        return form.querySelector('button[type="submit"]');
    }

    function getSimulationCard(form) {
        return form.closest('.simulation-card');
    }

    function createSpinner() {
        const spinner = document.createElement('span');
        spinner.className = 'simulation-submit-spinner';
        spinner.setAttribute('aria-hidden', 'true');

        Object.assign(spinner.style, {
            width: '0.9rem',
            height: '0.9rem',
            flexShrink: '0',
            borderRadius: '9999px',
            border: '1.5px solid rgba(165, 243, 252, 0.28)',
            borderTopColor: '#a5f3fc',
        });

        if (!prefersReducedMotion.matches) {
            spinner.animate(
                [
                    {transform: 'rotate(0deg)'},
                    {transform: 'rotate(360deg)'},
                ],
                {
                    duration: 700,
                    iterations: Infinity,
                    easing: 'linear',
                },
            );
        }

        return spinner;
    }

    function setButtonContent(button, label, {showSpinner = false} = {}) {
        button.replaceChildren();

        if (showSpinner) {
            button.appendChild(createSpinner());
        }

        const labelNode = document.createElement('span');
        labelNode.textContent = label;
        button.appendChild(labelNode);
    }

    function setSimulationState(form, state) {
        const submitButton = getSubmitButton(form);
        const card = getSimulationCard(form);
        if (!submitButton) return;

        if (!submitButton.dataset.originalContent) {
            submitButton.dataset.originalContent = submitButton.innerHTML;
        }

        if (state === 'idle') {
            submitButton.disabled = false;
            submitButton.removeAttribute('aria-disabled');

            if (submitButton.dataset.originalContent) {
                submitButton.innerHTML = submitButton.dataset.originalContent;
                delete submitButton.dataset.originalContent;
            }

            delete form.dataset.runningState;
            delete form.dataset.submitting;

            if (card) {
                card.removeAttribute('aria-busy');
                delete card.dataset.state;
                card.style.removeProperty('border-color');
                card.style.removeProperty('box-shadow');
                card.style.removeProperty('background');
            }
            return;
        }

        form.dataset.runningState = state;
        submitButton.disabled = true;
        submitButton.setAttribute('aria-disabled', 'true');

        if (card) {
            card.setAttribute('aria-busy', 'true');
            card.dataset.state = state;
            card.style.borderColor = 'rgba(103, 232, 249, 0.46)';
            card.style.boxShadow = '0 0 0 1px rgba(34, 211, 238, 0.08), 0 18px 45px rgba(0, 0, 0, 0.28), inset 0 0 30px rgba(34, 211, 238, 0.04)';
            card.style.background = 'linear-gradient(180deg, rgba(12, 35, 53, 0.97), rgba(6, 20, 34, 0.99))';
        }

        if (state === 'starting') {
            setButtonContent(submitButton, 'Starting simulation…', {showSpinner: true});
        } else if (state === 'queued') {
            setButtonContent(submitButton, 'Queued · Tracking', {showSpinner: true});
        } else if (state === 'running') {
            setButtonContent(submitButton, 'Simulation running…', {showSpinner: true});
        } else if (state === 'complete') {
            setButtonContent(submitButton, 'Simulation complete');
        } else if (state === 'failed') {
            setButtonContent(submitButton, 'Simulation failed');
        } else if (state === 'timed-out') {
            setButtonContent(submitButton, 'Simulation timed out');
        }
    }

    function resetSimulationAfterMinimumDisplay(form) {
        const active = activeSimulationForms.get(form.dataset.simType);
        const startedAt = active?.startedAt || Date.now();
        const delay = Math.max(0, minimumVisibleStateMs - (Date.now() - startedAt));

        setTimeout(() => {
            setSimulationState(form, 'idle');
            activeSimulationForms.delete(form.dataset.simType);
        }, delay);
    }

    function finishActiveSimulation(simType, active, state) {
        setSimulationState(active.form, state);
        setTimeout(() => {
            setSimulationState(active.form, 'idle');
            activeSimulationForms.delete(simType);
        }, 1200);
    }

    function isRecentPendingRun(run) {
        if (run.status !== 'PENDING') return false;

        const createdAtMs = Date.parse(run.created_at);
        if (!Number.isFinite(createdAtMs)) return false;

        return Date.now() - createdAtMs < pendingPollingMaxAgeMs;
    }

    function handleSimSubmit(event) {
        event.preventDefault();

        const form = event.target;
        if (form.dataset.submitting === 'true' || activeSimulationForms.has(form.dataset.simType)) return;

        if (simMessageDisplay) {
            simMessageDisplay.innerHTML = '';
        }

        form.dataset.submitting = 'true';
        activeSimulationForms.set(form.dataset.simType, {
            form,
            startedAt: Date.now(),
            taskId: null,
        });
        setSimulationState(form, 'starting');

        const endpoint = form.dataset.apiEndpoint;
        const csrfToken = form.dataset.csrfToken;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
            body: JSON.stringify(data),
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }

                return response.json().then(apiError => {
                    throw apiError;
                });
            })
            .then(data => {
                const active = activeSimulationForms.get(form.dataset.simType);
                if (active) {
                    active.taskId = data.task_id;
                }

                delete form.dataset.submitting;
                setSimulationState(form, 'queued');
                displaySimulationMessage(`Simulation started successfully! Task ID: ${data.task_id}`, 'success');
                updateHistoryTable();
                startPolling();
            })
            .catch(error => {
                displaySimulationMessage(error, 'error');
                resetSimulationAfterMinimumDisplay(form);
            });
    }

    function syncActiveSimulationStates(results) {
        activeSimulationForms.forEach((active, simType) => {
            const elapsedMs = Date.now() - active.startedAt;
            const matchingRun = active.taskId
                ? results.find(run => run.task_id === active.taskId)
                : null;

            if (matchingRun) {
                if (isRecentPendingRun(matchingRun)) {
                    setSimulationState(active.form, 'running');
                    return;
                }

                if (matchingRun.status === 'SUCCESS') {
                    finishActiveSimulation(simType, active, 'complete');
                    return;
                }

                if (matchingRun.status === 'FAILURE') {
                    finishActiveSimulation(simType, active, 'failed');
                    return;
                }

                if (matchingRun.status === 'TIMED_OUT') {
                    finishActiveSimulation(simType, active, 'timed-out');
                    return;
                }
            }

            if (elapsedMs >= pendingPollingMaxAgeMs) {
                finishActiveSimulation(simType, active, 'timed-out');
            }
        });
    }

    function getSimulationTypeLabel(simulationType) {
        return simulationTypeLabels[simulationType]
            || simulationType.toLowerCase().replaceAll('_', ' ').replace(/\b\w/g, char => char.toUpperCase());
    }

    function getStatusLabel(status) {
        return status.replaceAll('_', ' ');
    }

    function updateHistoryTable(url = initialHistoryUrl) {
        fetch(url)
            .then(response => {
                if (!response.ok) return null;
                return response.json();
            })
            .then(data => {
                if (!historyTableBody || !data) return;

                syncActiveSimulationStates(data.results);

                if (data.results.length === 0) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-10 text-center text-sm text-slate-500">No simulation history found.</td></tr>`;
                    return;
                }

                historyPrevUrl = data.previous;
                historyNextUrl = data.next;
                updatePaginationControls(data);

                let hasRecentPendingRun = false;
                let tableHtml = '';

                data.results.forEach(run => {
                    if (isRecentPendingRun(run)) {
                        hasRecentPendingRun = true;
                    }

                    const statusClasses = {
                        SUCCESS: 'border-emerald-200 bg-emerald-50 text-emerald-700',
                        PENDING: 'border-amber-200 bg-amber-50 text-amber-700',
                        FAILURE: 'border-red-200 bg-red-50 text-red-700',
                        TIMED_OUT: 'border-amber-300/30 bg-amber-400/10 text-amber-200 shadow-[inset_0_0_12px_rgba(251,191,36,0.05)]',
                    };
                    const statusClass = statusClasses[run.status] || 'border-slate-200 bg-slate-50 text-slate-600';
                    const resultContainerClass = run.status === 'TIMED_OUT'
                        ? 'border border-amber-300/15 bg-amber-400/[0.06] text-amber-100'
                        : 'bg-slate-50 text-slate-700';

                    tableHtml += `
                        <tr class="text-sm transition-colors hover:bg-slate-50/70">
                            <td class="px-4 py-4 align-top sm:px-6">
                                <span class="font-semibold text-slate-800">${getSimulationTypeLabel(run.simulation_type)}</span>
                            </td>
                            <td class="px-4 py-4 align-top sm:px-6">
                                <span class="inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold tracking-wide ${statusClass}">
                                    ${getStatusLabel(run.status)}
                                </span>
                            </td>
                            <td class="px-4 py-4 align-top text-sm text-slate-600 sm:px-6">
                                <div
                                    class="max-w-xl overflow-x-auto whitespace-nowrap rounded-md px-3 py-2 font-mono text-xs leading-5 sm:whitespace-normal ${resultContainerClass}"
                                    role="region"
                                    aria-label="Simulation result (scroll horizontally on mobile)"
                                    tabindex="0"
                                    style="-webkit-overflow-scrolling: touch;"
                                  >
                                    ${formatResult(run.simulation_type, run.result, run.status)}
                                </div>
                            </td>
                            <td class="px-4 py-4 align-top whitespace-nowrap text-xs text-slate-500 sm:px-6">
                                ${new Date(run.created_at).toLocaleString()}
                            </td>
                        </tr>
                    `;
                });

                historyTableBody.innerHTML = tableHtml;

                if (hasRecentPendingRun || activeSimulationForms.size > 0) {
                    startPolling();
                } else {
                    stopPolling();
                }
            })
            .catch(error => {
                if (historyTableBody) {
                    historyTableBody.innerHTML = `<tr><td colspan="4" class="px-6 py-10 text-center text-sm text-red-600">Error loading simulation history. Are you logged in?</td></tr>`;
                }
                stopPolling();
            });
    }

    if (historyTableBody) {
        updateHistoryTable();
    }

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

        const bgColor = level === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
        let messageContent = '';

        if (level === 'error' && data && data.details) {
            const details = data.details;
            if (typeof details === 'object' && details !== null) {
                const detailMessages = [];
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

        simMessageDisplay.innerHTML = `<div class="p-4 rounded-md ${bgColor}" role="alert">${messageContent}</div>`;

        setTimeout(() => {
            if (simMessageDisplay) simMessageDisplay.innerHTML = '';
        }, 4000);
    }

    function formatResult(simType, resultData, status) {
        if (!resultData) return 'N/A';
        if (status === 'TIMED_OUT') {
            return `
                <span class="inline-flex items-start gap-2 text-amber-200">
                    <span class="mt-[0.35rem] h-1.5 w-1.5 flex-none rounded-full bg-amber-300/80" aria-hidden="true"></span>
                    <span>
                        <strong class="font-semibold text-amber-100">Execution window exceeded.</strong>
                        <span class="text-amber-200/75"> ${resultData.error || 'Simulation did not complete before the timeout threshold.'}</span>
                    </span>
                </span>
            `;
        }
        if (resultData.error) {
            return `<span class="text-red-600">${resultData.error}</span>`;
        }
        const renderer = resultRenderers[simType] || resultRenderers.default;
        return renderer(resultData);
    }

    const resultRenderers = {
        TRAVEL_TIME: (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Destination:</strong> ${result.star_system_name} <br>
            <strong>Travel Time:</strong> ${result.travel_time_years} years
        `,
        SEASONAL_TEMPS: (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Planet:</strong> ${result.planet_name} <br>
            <strong>Hottest Temp (Periastron):</strong> ${result.periastron_temp_k} K <br>
            <strong>Coldest Temp (Apoastron):</strong> ${result.apoastron_temp_k} K <br>
            <strong>Seasonal Difference:</strong> ${result.seasonal_temp_difference_k} K
        `,
        TIDAL_LOCKING: (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Planet:</strong> ${result.planet_name} <br>
            <strong>Star:</strong> ${result.star_name} <br>
            <strong>Is Likely Tidally Locked:</strong> ${result.is_locked ? 'True' : 'False'} <br>
            <strong>Locking Timescale Years:</strong> ${result.locking_timescale_years} <br>
            <strong>Star Age Years:</strong> ${result.star_age_years} <br>
            <strong>Conclusion:</strong> ${result.conclusion}
         `,
        STAR_LIFETIME: (result) => `
            <strong>Status:</strong> SUCCESS <br>
            <strong>Star:</strong> ${result.star_name} <br>
            <strong>Star Solar Mass:</strong> ${result.star_mass_solar} <br>
            <strong>Star Age:</strong> ${result.star_age_gyr} GYR <br>
            <strong>Estimated Total Lifetime:</strong> ${result.estimated_total_lifetime_gyr} GYR <br>
            <strong>Estimated Remaining Lifetime:</strong> ${result.estimated_remaining_lifetime_gyr} GYR <br>
            <strong>Percent Lifespan Complete:</strong> ${result.percent_lifespan_complete} % <br>
            <strong>Conclusion:</strong> ${result.conclusion}
         `,
        default: () => 'Task finished with an unknown result type.',
    };
});