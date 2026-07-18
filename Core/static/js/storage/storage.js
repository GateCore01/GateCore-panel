// -------------------------------------------------
// GateCore Storage
// storage.js
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    loadStorage();

    setupLogout();

    // Alle 15 Sekunden aktualisieren
    setInterval(loadStorage, 15000);

});

// -------------------------------------------------
// Alles laden
// -------------------------------------------------

async function loadStorage() {

    await loadPools();

    await loadDisks();

}

// -------------------------------------------------
// Pools laden
// -------------------------------------------------

async function loadPools() {

    const tbody = document.getElementById("poolBody");

    tbody.innerHTML = "";

    try {

        const response = await fetch("/api/storage/list");

        const data = await response.json();

        if (data.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-row">
                        Keine Pools vorhanden.
                    </td>
                </tr>
            `;

            return;

        }

        data.forEach(pool => {

            tbody.innerHTML += `

                <tr>

                    <td>${pool.name}</td>

                    <td>${pool.type}</td>

                    <td>${pool.size}</td>

                    <td>${pool.used}</td>

                    <td>${pool.free}</td>

                    <td>${pool.usage}</td>

                    <td>${pool.status}</td>

                    <td>

                        <div class="action-buttons">

                            <button
                                class="btn-test"
                                onclick="detailsPool('${pool.name}')">

                                Details

                            </button>

                            <button
                                class="btn-edit"
                                onclick="editPool('${pool.name}')">

                                Bearbeiten

                            </button>

                            <button
                                class="btn-delete"
                                onclick="deletePool('${pool.name}')">

                                Löschen

                            </button>

                        </div>

                    </td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Festplatten laden
// -------------------------------------------------

async function loadDisks() {

    const tbody = document.getElementById("diskBody");

    tbody.innerHTML = "";

    try {

        const response = await fetch("/api/storage/disks");

        const data = await response.json();

        if (data.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-row">
                        Keine Festplatten gefunden.
                    </td>
                </tr>
            `;

            return;

        }

        data.forEach(disk => {

            tbody.innerHTML += `

                <tr>

                    <td>${disk.server}</td>

                    <td>${disk.device}</td>

                    <td>${disk.model}</td>

                    <td>${disk.size}</td>

                    <td>${disk.filesystem}</td>

                    <td>${disk.mountpoint}</td>

                    <td>${disk.status}</td>

                    <td>

                        <div class="action-buttons">

                            <button
                                class="btn-test"
                                onclick="smartDisk('${disk.device}')">

                                SMART

                            </button>

                            <button
                                class="btn-edit"
                                onclick="editDisk('${disk.device}')">

                                Bearbeiten

                            </button>

                        </div>

                    </td>

                </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Pool Details
// -------------------------------------------------

function detailsPool(pool) {

    window.location =
        "/panel/storage/details?pool=" +
        encodeURIComponent(pool);

}

// -------------------------------------------------
// Pool bearbeiten
// -------------------------------------------------

function editPool(pool) {

    window.location =
        "/panel/storage/edit?pool=" +
        encodeURIComponent(pool);

}

// -------------------------------------------------
// SMART
// -------------------------------------------------

function smartDisk(disk) {

    window.location =
        "/panel/storage/smart?disk=" +
        encodeURIComponent(disk);

}

// -------------------------------------------------
// Festplatte bearbeiten
// -------------------------------------------------

function editDisk(disk) {

    alert(
        "Festplatte " +
        disk +
        " bearbeiten folgt später."
    );

}

// -------------------------------------------------
// Pool löschen
// -------------------------------------------------

async function deletePool(pool) {

    if (!confirm(`Pool "${pool}" wirklich löschen?`))
        return;

    try {

        const response = await fetch(

            "/api/storage/delete/" +
            encodeURIComponent(pool),

            {
                method: "DELETE"
            }

        );

        const result = await response.json();

        alert(result.message);

        loadStorage();

    }

    catch (error) {

        console.error(error);

    }

}

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