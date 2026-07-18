// -------------------------------------------------
// GateCore
// storage-details.js
// Teil 1
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupLogout();

    loadPool();

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
// Poolinformationen laden
// -------------------------------------------------

async function loadPool() {

    const pool = getPool();

    if (!pool) {

        showError(
            "Kein Pool angegeben."
        );

        return;

    }

    try {

        const response =
            await fetch(

                "/api/storage/details/" +
                encodeURIComponent(pool)

            );

        const data =
            await response.json();

        fillGeneral(data);

        fillProperties(data);

        fillUsage(data);

    }

    catch (error) {

        console.error(error);

        showError(
            "Pool konnte nicht geladen werden."
        );

    }

}

// -------------------------------------------------
// Allgemeine Informationen
// -------------------------------------------------

function fillGeneral(data) {

    setText("poolName", data.name);

    setText("poolType", data.type);

    setText("poolStatus", data.status);

    setText("poolSize", data.size);

    setText("poolUsed", data.used);

    setText("poolFree", data.free);

    setText("poolHealth", data.health);

    setText("poolGuid", data.guid);

    setText("poolVersion", data.version);

    setText("poolHost", data.server);

}

// -------------------------------------------------
// Eigenschaften
// -------------------------------------------------

function fillProperties(data) {

    setText(
        "compression",
        data.compression
    );

    setText(
        "atime",
        data.atime
    );

    setText(
        "autotrim",
        data.autotrim
    );

    setText(
        "ashift",
        data.ashift
    );

    setText(
        "recordsize",
        data.recordsize
    );

    setText(
        "mountpoint",
        data.mountpoint
    );

    setText(
        "readonly",
        data.readonly
    );

    setText(
        "dedup",
        data.dedup
    );

}

// -------------------------------------------------
// Speicherbelegung
// -------------------------------------------------

function fillUsage(data) {

    const percent =
        parseFloat(data.usage);

    setText(
        "usagePercent",
        percent + " %"
    );

    const bar =
        document.getElementById("usageBar");

    if (bar) {

        bar.style.width =
            percent + "%";

        if (percent < 60) {

            bar.style.background =
                "#198754";

        }

        else if (percent < 85) {

            bar.style.background =
                "#ffc107";

        }

        else {

            bar.style.background =
                "#dc3545";

        }

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

    element.textContent =
        value ?? "-";

}

// -------------------------------------------------
// Fehler
// -------------------------------------------------

function showError(text) {

    const status =
        document.getElementById("status");

    if (!status)
        return;

    status.className =
        "status-error";

    status.innerHTML = text;

}

// -------------------------------------------------
// Festplatten laden
// -------------------------------------------------

async function loadDisks() {

    const pool = getPool();

    const tbody =
        document.getElementById("diskBody");

    if (!tbody)
        return;

    tbody.innerHTML = "";

    try {

        const response =
            await fetch(
                "/api/storage/disks/" +
                encodeURIComponent(pool)
            );

        const disks =
            await response.json();

        if (disks.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-row">
                        Keine Laufwerke vorhanden.
                    </td>
                </tr>
            `;

            return;

        }

        disks.forEach(disk => {

            tbody.innerHTML += `

            <tr>

                <td>${disk.device}</td>

                <td>${disk.model}</td>

                <td>${disk.size}</td>

                <td>${disk.status}</td>

                <td>${disk.serial}</td>

            </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Datasets laden
// -------------------------------------------------

async function loadDatasets() {

    const pool = getPool();

    const tbody =
        document.getElementById("datasetBody");

    if (!tbody)
        return;

    tbody.innerHTML = "";

    try {

        const response =
            await fetch(
                "/api/storage/datasets/" +
                encodeURIComponent(pool)
            );

        const datasets =
            await response.json();

        if (datasets.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-row">
                        Keine Datasets vorhanden.
                    </td>
                </tr>
            `;

            return;

        }

        datasets.forEach(dataset => {

            tbody.innerHTML += `

            <tr>

                <td>${dataset.name}</td>

                <td>${dataset.used}</td>

                <td>${dataset.available}</td>

                <td>${dataset.mountpoint}</td>

                <td>${dataset.compression}</td>

            </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Pool exportieren
// -------------------------------------------------

async function exportPool() {

    if (!confirm("Pool exportieren?"))
        return;

    const pool = getPool();

    const response =
        await fetch(

            "/api/storage/export",

            {

                method: "POST",

                headers: {

                    "Content-Type":"application/json"

                },

                body: JSON.stringify({

                    pool: pool

                })

            }

        );

    const result =
        await response.json();

    alert(result.message);

}

// -------------------------------------------------
// Scrub starten
// -------------------------------------------------

function startScrub() {

    window.location =
        "/panel/storage/scrub?pool=" +
        encodeURIComponent(getPool());

}

// -------------------------------------------------
// SMART
// -------------------------------------------------

function openSmart() {

    window.location =
        "/panel/storage/smart?pool=" +
        encodeURIComponent(getPool());

}

// -------------------------------------------------
// Snapshots
// -------------------------------------------------

function openSnapshots() {

    window.location =
        "/panel/storage/snapshots?pool=" +
        encodeURIComponent(getPool());

}

// -------------------------------------------------
// Bearbeiten
// -------------------------------------------------

function editPool() {

    window.location =
        "/panel/storage/edit?pool=" +
        encodeURIComponent(getPool());

}

// -------------------------------------------------
// Aktualisieren
// -------------------------------------------------

async function refreshPool() {

    await loadPool();

    await loadDisks();

    await loadDatasets();

}

// -------------------------------------------------
// Buttons verbinden
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    loadDisks();

    loadDatasets();

    refreshPool();

    const exportButton =
        document.getElementById("exportButton");

    if (exportButton)
        exportButton.onclick = exportPool;

    const scrubButton =
        document.getElementById("scrubButton");

    if (scrubButton)
        scrubButton.onclick = startScrub;

    const smartButton =
        document.getElementById("smartButton");

    if (smartButton)
        smartButton.onclick = openSmart;

    const snapshotButton =
        document.getElementById("snapshotButton");

    if (snapshotButton)
        snapshotButton.onclick = openSnapshots;

    const editButton =
        document.getElementById("editButton");

    if (editButton)
        editButton.onclick = editPool;

    const refreshButton =
        document.getElementById("refreshButton");

    if (refreshButton)
        refreshButton.onclick = refreshPool;

});

// -------------------------------------------------
// Automatische Aktualisierung
// -------------------------------------------------

setInterval(refreshPool, 15000);