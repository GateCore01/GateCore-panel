// -------------------------------------------------
// GateCore
// storage-add.js
// Teil 1
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    setupLogout();

    loadServers();

    document
        .getElementById("server")
        .addEventListener("change", loadDisks);

    document
        .getElementById("raid")
        .addEventListener("change", validateRaid);

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
// Server laden
// -------------------------------------------------

async function loadServers() {

    const select =
        document.getElementById("server");

    select.innerHTML = "";

    try {

        const response =
            await fetch("/api/server/list");

        const servers =
            await response.json();

        if (servers.length === 0) {

            select.innerHTML =
                "<option>Keine Server</option>";

            return;

        }

        servers.forEach(server => {

            select.innerHTML += `

                <option value="${server.id}">

                    ${server.name}

                </option>

            `;

        });

        loadDisks();

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Festplatten laden
// -------------------------------------------------

async function loadDisks() {

    const server =
        document.getElementById("server").value;

    const tbody =
        document.getElementById("diskBody");

    tbody.innerHTML = "";

    try {

        const response =
            await fetch(

                "/api/storage/disks/" + server

            );

        const disks =
            await response.json();

        if (disks.length === 0) {

            tbody.innerHTML = `

                <tr>

                    <td colspan="5"
                        class="empty-row">

                        Keine freien Laufwerke gefunden.

                    </td>

                </tr>

            `;

            return;

        }

        disks.forEach(disk => {

            tbody.innerHTML += `

                <tr>

                    <td>

                        <input
                            type="checkbox"
                            class="diskCheck"
                            value="${disk.device}"
                            onchange="validateRaid()">

                    </td>

                    <td>

                        ${disk.device}

                    </td>

                    <td>

                        ${disk.size}

                    </td>

                    <td>

                        ${disk.model}

                    </td>

                    <td>

                        ${disk.status}

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
// Gewählte Laufwerke
// -------------------------------------------------

function getSelectedDisks() {

    let disks = [];

    document
        .querySelectorAll(".diskCheck:checked")
        .forEach(item => {

            disks.push(item.value);

        });

    return disks;

}

// -------------------------------------------------
// RAID prüfen
// -------------------------------------------------

function validateRaid() {

    const raid =
        document.getElementById("raid").value;

    const count =
        getSelectedDisks().length;

    let needed = 2;

    switch (raid) {

        case "mirror":

            needed = 2;

            break;

        case "stripe":

            needed = 2;

            break;

        case "raidz":

            needed = 3;

            break;

        case "raidz2":

            needed = 4;

            break;

        case "raidz3":

            needed = 5;

            break;

    }

    const status =
        document.getElementById("status");

    if (count < needed) {

        status.className = "status-error";

        status.innerHTML =
            "Für " +
            raid.toUpperCase() +
            " werden mindestens " +
            needed +
            " Laufwerke benötigt.";

        return false;

    }

    status.className = "status-success";

    status.innerHTML =
        count +
        " Laufwerke ausgewählt.";

    return true;

}

// -------------------------------------------------
// Formular absenden
// -------------------------------------------------

document
    .getElementById("storageForm")
    .addEventListener("submit", createStorage);

// -------------------------------------------------
// Pool erstellen
// -------------------------------------------------

async function createStorage(event) {

    event.preventDefault();

    if (!validateRaid())
        return;

    const button =
        event.submitter;

    button.disabled = true;

    button.innerHTML =
        "Speichere...";

    const data = {

        server:

            document
                .getElementById("server")
                .value,

        name:

            document
                .getElementById("poolname")
                .value,

        raid:

            document
                .getElementById("raid")
                .value,

        compression:

            document
                .getElementById("compression")
                .value,

        atime:

            document
                .getElementById("atime")
                .checked,

        autotrim:

            document
                .getElementById("autotrim")
                .checked,

        disks:

            getSelectedDisks()

    };

    try {

        const response =
            await fetch(

                "/api/storage/create",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(data)

                }

            );

        const result =
            await response.json();

        if (result.success) {

            showSuccess(result.message);

            setTimeout(() => {

                window.location =
                    "/panel/storage";

            }, 1200);

        }

        else {

            showError(result.message);

        }

    }

    catch (error) {

        console.error(error);

        showError(
            "Server nicht erreichbar."
        );

    }

    button.disabled = false;

    button.innerHTML =
        "Speicher erstellen";

}

// -------------------------------------------------
// Erfolg
// -------------------------------------------------

function showSuccess(text) {

    const status =
        document.getElementById("status");

    status.className =
        "status-success";

    status.innerHTML = text;

}

// -------------------------------------------------
// Fehler
// -------------------------------------------------

function showError(text) {

    const status =
        document.getElementById("status");

    status.className =
        "status-error";

    status.innerHTML = text;

}

// -------------------------------------------------
// Formular zurücksetzen
// -------------------------------------------------

function resetForm() {

    document
        .getElementById("storageForm")
        .reset();

    document
        .getElementById("diskBody")
        .innerHTML = "";

    document
        .getElementById("status")
        .innerHTML = "";

}

// -------------------------------------------------
// Poolname prüfen
// -------------------------------------------------

function validatePoolName() {

    const input =
        document.getElementById("poolname");

    const regex =
        /^[a-zA-Z0-9_-]+$/;

    if (!regex.test(input.value)) {

        showError(
            "Ungültiger Poolname."
        );

        return false;

    }

    return true;

}

document
    .getElementById("poolname")
    .addEventListener("input", () => {

        validatePoolName();

    });

// -------------------------------------------------
// RAID Änderung
// -------------------------------------------------

document
    .getElementById("raid")
    .addEventListener("change", () => {

        validateRaid();

    });

// -------------------------------------------------
// Aktualisieren
// -------------------------------------------------

async function refreshDisks() {

    await loadDisks();

}

// -------------------------------------------------
// Seite verlassen
// -------------------------------------------------

window.addEventListener("beforeunload", () => {

    document
        .querySelectorAll("button")
        .forEach(button => {

            button.disabled = false;

        });

});