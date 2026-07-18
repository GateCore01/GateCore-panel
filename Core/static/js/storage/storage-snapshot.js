// -------------------------------------------------
// GateCore
// storage-snapshots.js
// Teil 1
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupLogout();

    loadSnapshots();

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
        new URLSearchParams(
            window.location.search
        );

    return params.get("pool");

}

// -------------------------------------------------
// Snapshots laden
// -------------------------------------------------

async function loadSnapshots() {

    const pool = getPool();

    if (!pool) {

        showError(
            "Kein Speicherpool ausgewählt."
        );

        return;

    }

    const tbody =
        document.getElementById(
            "snapshotBody"
        );

    if (!tbody)
        return;

    tbody.innerHTML = "";

    try {

        const response =
            await fetch(

                "/api/storage/snapshots/" +
                encodeURIComponent(pool)

            );

        const snapshots =
            await response.json();

        if (snapshots.length === 0) {

            tbody.innerHTML = `

            <tr>

                <td colspan="7"
                    class="empty-row">

                    Keine Snapshots vorhanden.

                </td>

            </tr>

            `;

            return;

        }

        snapshots.forEach(snapshot => {

            tbody.innerHTML += `

            <tr>

                <td>${snapshot.name}</td>

                <td>${snapshot.dataset}</td>

                <td>${snapshot.created}</td>

                <td>${snapshot.used}</td>

                <td>${snapshot.referenced}</td>

                <td>${snapshot.status}</td>

                <td>

                    <div class="action-buttons">

                        <button
                            class="btn-edit"
                            onclick="renameSnapshot('${snapshot.name}')">

                            Umbenennen

                        </button>

                        <button
                            class="btn-test"
                            onclick="rollbackSnapshot('${snapshot.name}')">

                            Rollback

                        </button>

                        <button
                            class="btn-delete"
                            onclick="deleteSnapshot('${snapshot.name}')">

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

        showError(
            "Snapshots konnten nicht geladen werden."
        );

    }

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
// Snapshot erstellen
// -------------------------------------------------

async function createSnapshot() {

    const dataset =
        document.getElementById("dataset").value;

    const name =
        document.getElementById("snapshotName").value;

    if (dataset === "" || name === "") {

        showError(
            "Dataset und Snapshotname angeben."
        );

        return;

    }

    try {

        const response =
            await fetch(

                "/api/storage/snapshot/create",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool(),

                        dataset: dataset,

                        name: name

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            loadSnapshots();

        }

        else {

            showError(result.message);

        }

    }

    catch (error) {

        console.error(error);

        showError(
            "Snapshot konnte nicht erstellt werden."
        );

    }

}

// -------------------------------------------------
// Snapshot umbenennen
// -------------------------------------------------

async function renameSnapshot(oldName) {

    const newName =
        prompt(

            "Neuer Snapshotname:",

            oldName

        );

    if (!newName)
        return;

    try {

        const response =
            await fetch(

                "/api/storage/snapshot/rename",

                {

                    method: "PUT",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool(),

                        old_name: oldName,

                        new_name: newName

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            loadSnapshots();

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
// Snapshot löschen
// -------------------------------------------------

async function deleteSnapshot(name) {

    if (!confirm(
        "Snapshot wirklich löschen?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/snapshot/delete",

                {

                    method: "DELETE",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool(),

                        name: name

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            loadSnapshots();

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
// Rollback
// -------------------------------------------------

async function rollbackSnapshot(name) {

    if (!confirm(
        "Rollback durchführen?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/snapshot/rollback",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool(),

                        name: name

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
// Snapshot klonen
// -------------------------------------------------

async function cloneSnapshot(name) {

    const cloneName =
        prompt(
            "Name des Klons:"
        );

    if (!cloneName)
        return;

    try {

        const response =
            await fetch(

                "/api/storage/snapshot/clone",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool: getPool(),

                        snapshot: name,

                        clone: cloneName

                    })

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            loadSnapshots();

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
// Aktualisieren
// -------------------------------------------------

async function refreshSnapshots() {

    await loadSnapshots();

}

// -------------------------------------------------
// Buttons verbinden
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    const createButton =
        document.getElementById("createButton");

    if (createButton)
        createButton.onclick =
            createSnapshot;

    const refreshButton =
        document.getElementById("refreshButton");

    if (refreshButton)
        refreshButton.onclick =
            refreshSnapshots;

});

// -------------------------------------------------
// Automatisch aktualisieren
// -------------------------------------------------

setInterval(

    refreshSnapshots,

    15000

);