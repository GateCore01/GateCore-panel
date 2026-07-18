// -------------------------------------------------
// GateCore
// storage-smart.js
// Teil 1
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupLogout();

    loadSmart();

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
// Laufwerk aus URL lesen
// -------------------------------------------------

function getDisk() {

    const params =
        new URLSearchParams(window.location.search);

    return params.get("disk");

}

// -------------------------------------------------
// SMART Daten laden
// -------------------------------------------------

async function loadSmart() {

    const disk = getDisk();

    if (!disk) {

        showError(
            "Kein Laufwerk ausgewählt."
        );

        return;

    }

    try {

        const response =
            await fetch(

                "/api/storage/smart/" +
                encodeURIComponent(disk)

            );

        const data =
            await response.json();

        fillGeneral(data);

        fillHealth(data);

    }

    catch (error) {

        console.error(error);

        showError(
            "SMART-Daten konnten nicht geladen werden."
        );

    }

}

// -------------------------------------------------
// Allgemeine Informationen
// -------------------------------------------------

function fillGeneral(data) {

    setText("diskName", data.device);

    setText("diskModel", data.model);

    setText("diskSerial", data.serial);

    setText("diskFirmware", data.firmware);

    setText("diskCapacity", data.capacity);

    setText("diskInterface", data.interface);

    setText("diskRotation", data.rotation);

    setText("diskPowerOn", data.power_on_hours);

    setText("diskPowerCycle", data.power_cycles);

}

// -------------------------------------------------
// SMART Status
// -------------------------------------------------

function fillHealth(data) {

    setText("diskHealth", data.health);

    setText(
        "diskTemperature",
        data.temperature + " °C"
    );

    setText(
        "diskReallocated",
        data.reallocated
    );

    setText(
        "diskPending",
        data.pending
    );

    setText(
        "diskOffline",
        data.offline
    );

    const badge =
        document.getElementById("healthBadge");

    if (!badge)
        return;

    badge.innerHTML =
        data.health;

    badge.className = "";

    switch (data.health.toLowerCase()) {

        case "healthy":

        case "passed":

        case "ok":

            badge.classList.add(
                "status-success"
            );

            break;

        case "warning":

            badge.classList.add(
                "status-warning"
            );

            break;

        default:

            badge.classList.add(
                "status-error"
            );

    }

    updateTemperature(
        data.temperature
    );

}

// -------------------------------------------------
// Temperaturanzeige
// -------------------------------------------------

function updateTemperature(temp) {

    const bar =
        document.getElementById(
            "temperatureBar"
        );

    if (!bar)
        return;

    bar.style.width =
        Math.min(temp, 100) + "%";

    if (temp < 40) {

        bar.style.background =
            "#198754";

    }

    else if (temp < 50) {

        bar.style.background =
            "#ffc107";

    }

    else {

        bar.style.background =
            "#dc3545";

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
// SMART Attribute laden
// -------------------------------------------------

async function loadAttributes() {

    const disk = getDisk();

    const tbody =
        document.getElementById("attributeBody");

    if (!tbody)
        return;

    tbody.innerHTML = "";

    try {

        const response =
            await fetch(

                "/api/storage/smart/attributes/" +
                encodeURIComponent(disk)

            );

        const attributes =
            await response.json();

        if (attributes.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-row">
                        Keine SMART-Attribute vorhanden.
                    </td>
                </tr>
            `;

            return;

        }

        attributes.forEach(attr => {

            tbody.innerHTML += `

                <tr>

                    <td>${attr.id}</td>

                    <td>${attr.name}</td>

                    <td>${attr.value}</td>

                    <td>${attr.worst}</td>

                    <td>${attr.threshold}</td>

                    <td>${attr.raw}</td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// SMART Selbsttest starten
// -------------------------------------------------

async function startTest(type) {

    if (!confirm("SMART-Test starten?"))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/smart/test",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        disk: getDisk(),

                        type: type

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

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
// SMART Log laden
// -------------------------------------------------

async function loadLog() {

    const disk = getDisk();

    const log =
        document.getElementById("smartLog");

    if (!log)
        return;

    try {

        const response =
            await fetch(

                "/api/storage/smart/log/" +
                encodeURIComponent(disk)

            );

        const result =
            await response.json();

        log.value =
            result.log;

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Aktualisieren
// -------------------------------------------------

async function refreshSmart() {

    await loadSmart();

    await loadAttributes();

    await loadLog();

}

// -------------------------------------------------
// Buttons
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    refreshSmart();

    const shortButton =
        document.getElementById("shortTestButton");

    if (shortButton)
        shortButton.onclick =
            () => startTest("short");

    const longButton =
        document.getElementById("longTestButton");

    if (longButton)
        longButton.onclick =
            () => startTest("long");

    const conveyanceButton =
        document.getElementById("conveyanceTestButton");

    if (conveyanceButton)
        conveyanceButton.onclick =
            () => startTest("conveyance");

    const refreshButton =
        document.getElementById("refreshButton");

    if (refreshButton)
        refreshButton.onclick =
            refreshSmart;

});

// -------------------------------------------------
// Automatisch aktualisieren
// -------------------------------------------------

setInterval(refreshSmart, 15000);