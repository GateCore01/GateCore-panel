// -------------------------------------------------
// GateCore
// storage-scrub.js
// Teil 1
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupLogout();

    loadScrub();

});

// -------------------------------------------------
// Logout
// -------------------------------------------------

function setupLogout() {

    const button =
        document.getElementById("logoutButton");

    if (!button)
        return;

    button.addEventListener("click", logout);

}

async function logout() {

    try {

        await fetch("/api/logout", {

            method: "POST"

        });

    }

    catch (e) {}

    window.location = "/";

}

// -------------------------------------------------
// Pool aus URL lesen
// -------------------------------------------------

function getPool() {

    const params =
        new URLSearchParams(window.location.search);

    return params.get("pool");

}

// -------------------------------------------------
// Scrub Status laden
// -------------------------------------------------

async function loadScrub() {

    const pool = getPool();

    if (!pool) {

        showError(
            "Kein ZFS-Pool ausgewählt."
        );

        return;

    }

    try {

        const response =
            await fetch(

                "/api/storage/scrub/" +
                encodeURIComponent(pool)

            );

        const data =
            await response.json();

        fillScrub(data);

    }

    catch (error) {

        console.error(error);

        showError(
            "Scrub-Status konnte nicht geladen werden."
        );

    }

}

// -------------------------------------------------
// Daten anzeigen
// -------------------------------------------------

function fillScrub(data) {

    setText(
        "poolName",
        data.pool
    );

    setText(
        "scrubStatus",
        data.status
    );

    setText(
        "scrubProgress",
        data.progress + " %"
    );

    setText(
        "scrubScanned",
        data.scanned
    );

    setText(
        "scrubIssued",
        data.issued
    );

    setText(
        "scrubRepaired",
        data.repaired
    );

    setText(
        "scrubErrors",
        data.errors
    );

    setText(
        "scrubSpeed",
        data.speed
    );

    setText(
        "scrubETA",
        data.eta
    );

    setText(
        "scrubStarted",
        data.started
    );

    setText(
        "scrubFinished",
        data.finished
    );

    updateProgressBar(
        data.progress
    );

    updateStatusBadge(
        data.status
    );

}

// -------------------------------------------------
// Fortschrittsbalken
// -------------------------------------------------

function updateProgressBar(progress) {

    const bar =
        document.getElementById(
            "progressBar"
        );

    if (!bar)
        return;

    const value =
        Math.max(
            0,
            Math.min(
                100,
                Number(progress)
            )
        );

    bar.style.width =
        value + "%";

    if (value < 50) {

        bar.style.background =
            "#0d6efd";

    }

    else if (value < 100) {

        bar.style.background =
            "#ffc107";

    }

    else {

        bar.style.background =
            "#198754";

    }

}

// -------------------------------------------------
// Statusbadge
// -------------------------------------------------

function updateStatusBadge(status) {

    const badge =
        document.getElementById(
            "statusBadge"
        );

    if (!badge)
        return;

    badge.innerHTML = status;

    badge.className = "";

    switch (
        status.toLowerCase()
    ) {

        case "running":

        case "scrubbing":

            badge.classList.add(
                "status-warning"
            );

            break;

        case "finished":

        case "completed":

        case "done":

            badge.classList.add(
                "status-success"
            );

            break;

        case "error":

        case "failed":

            badge.classList.add(
                "status-error"
            );

            break;

        default:

            badge.classList.add(
                "status-info"
            );

    }

}

// -------------------------------------------------
// Text setzen
// -------------------------------------------------

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (!element)
        return;

    element.innerHTML =
        value ?? "-";

}

// -------------------------------------------------
// Statusmeldungen
// -------------------------------------------------

function showSuccess(text) {

    const status =
        document.getElementById("status");

    if (!status)
        return;

    status.className =
        "status-success";

    status.innerHTML =
        text;

}

function showError(text) {

    const status =
        document.getElementById("status");

    if (!status)
        return;

    status.className =
        "status-error";

    status.innerHTML =
        text;

}

function clearStatus() {

    const status =
        document.getElementById("status");

    if (!status)
        return;

    status.className = "";

    status.innerHTML = "";

}

// -------------------------------------------------
// Scrub starten
// -------------------------------------------------

async function startScrub() {

    if (!confirm(
        "ZFS-Scrub wirklich starten?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/scrub/start",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool()

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            refreshScrub();

        }

        else {

            showError(result.message);

        }

    }

    catch (error) {

        console.error(error);

        showError(
            "Scrub konnte nicht gestartet werden."
        );

    }

}

// -------------------------------------------------
// Scrub abbrechen
// -------------------------------------------------

async function stopScrub() {

    if (!confirm(
        "Scrub wirklich abbrechen?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/scrub/stop",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool()

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            refreshScrub();

        }

        else {

            showError(result.message);

        }

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Scrub Verlauf laden
// -------------------------------------------------

async function loadHistory() {

    const history =
        document.getElementById(
            "historyBody"
        );

    if (!history)
        return;

    history.innerHTML = "";

    try {

        const response =
            await fetch(

                "/api/storage/scrub/history/" +
                encodeURIComponent(
                    getPool()
                )

            );

        const result =
            await response.json();

        if (result.length === 0) {

            history.innerHTML = `

            <tr>

                <td colspan="5"
                    class="empty-row">

                    Kein Scrub-Verlauf vorhanden.

                </td>

            </tr>

            `;

            return;

        }

        result.forEach(item => {

            history.innerHTML += `

            <tr>

                <td>${item.started}</td>

                <td>${item.finished}</td>

                <td>${item.duration}</td>

                <td>${item.errors}</td>

                <td>${item.result}</td>

            </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Aktualisieren
// -------------------------------------------------

async function refreshScrub() {

    await loadScrub();

    await loadHistory();

}

// -------------------------------------------------
// Buttons verbinden
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    refreshScrub();

    const startButton =
        document.getElementById(
            "startButton"
        );

    if (startButton)
        startButton.onclick =
            startScrub;

    const stopButton =
        document.getElementById(
            "stopButton"
        );

    if (stopButton)
        stopButton.onclick =
            stopScrub;

    const refreshButton =
        document.getElementById(
            "refreshButton"
        );

    if (refreshButton)
        refreshButton.onclick =
            refreshScrub;

});

// -------------------------------------------------
// Automatisch aktualisieren
// -------------------------------------------------

setInterval(

    refreshScrub,

    10000

);