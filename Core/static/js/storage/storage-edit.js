// -------------------------------------------------
// GateCore
// storage-edit.js
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
// Poolname aus URL
// -------------------------------------------------

function getPool() {

    const params =
        new URLSearchParams(window.location.search);

    return params.get("pool");

}

// -------------------------------------------------
// Pool laden
// -------------------------------------------------

async function loadPool() {

    const pool = getPool();

    if (!pool) {

        showError("Kein Pool ausgewählt.");

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

        fillForm(data);

    }

    catch (error) {

        console.error(error);

        showError(
            "Pool konnte nicht geladen werden."
        );

    }

}

// -------------------------------------------------
// Formular füllen
// -------------------------------------------------

function fillForm(data) {

    setValue("poolname", data.name);

    setValue("compression", data.compression);

    setValue("recordsize", data.recordsize);

    setValue("ashift", data.ashift);

    setValue("mountpoint", data.mountpoint);

    setChecked("autotrim", data.autotrim);

    setChecked("atime", data.atime);

    setChecked("readonly", data.readonly);

    setChecked("dedup", data.dedup);

    setValue("comment", data.comment);

    setText("poolStatus", data.status);

    setText("poolHealth", data.health);

    setText("poolSize", data.size);

    setText("poolUsed", data.used);

    setText("poolFree", data.free);

}

// -------------------------------------------------
// Value setzen
// -------------------------------------------------

function setValue(id, value) {

    const element =
        document.getElementById(id);

    if (!element)
        return;

    element.value =
        value ?? "";

}

// -------------------------------------------------
// Checkbox setzen
// -------------------------------------------------

function setChecked(id, value) {

    const element =
        document.getElementById(id);

    if (!element)
        return;

    element.checked =
        value === true ||
        value === "on" ||
        value === "yes" ||
        value === "enabled";

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

    clearStatus();

    return true;

}

document
    .getElementById("poolname")
    ?.addEventListener(

        "input",

        validatePoolName

    );

// -------------------------------------------------
// Status
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
// Formular speichern
// -------------------------------------------------

const form =
    document.getElementById("storageForm");

if (form) {

    form.addEventListener("submit", savePool);

}

async function savePool(event) {

    event.preventDefault();

    if (!validatePoolName())
        return;

    const button =
        event.submitter;

    button.disabled = true;

    button.innerHTML =
        "Speichern...";

    const data = {

        name:
            getPool(),

        new_name:
            document.getElementById("poolname").value,

        compression:
            document.getElementById("compression").value,

        recordsize:
            document.getElementById("recordsize").value,

        ashift:
            document.getElementById("ashift").value,

        mountpoint:
            document.getElementById("mountpoint").value,

        autotrim:
            document.getElementById("autotrim").checked,

        atime:
            document.getElementById("atime").checked,

        readonly:
            document.getElementById("readonly").checked,

        dedup:
            document.getElementById("dedup").checked,

        comment:
            document.getElementById("comment").value

    };

    try {

        const response =
            await fetch(

                "/api/storage/update",

                {

                    method: "PUT",

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
        "Speichern";

}

// -------------------------------------------------
// Formular zurücksetzen
// -------------------------------------------------

function resetForm() {

    loadPool();

    clearStatus();

}

// -------------------------------------------------
// Pool exportieren
// -------------------------------------------------

async function exportPool() {

    if (!confirm(
        "Pool wirklich exportieren?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/export",

                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        pool:
                            getPool()

                    })

                }

            );

        const result =
            await response.json();

        alert(result.message);

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Pool löschen
// -------------------------------------------------

async function deletePool() {

    if (!confirm(
        "Pool wirklich löschen?"
    ))
        return;

    try {

        const response =
            await fetch(

                "/api/storage/delete/" +
                encodeURIComponent(
                    getPool()
                ),

                {

                    method: "DELETE"

                }

            );

        const result =
            await response.json();

        alert(result.message);

        if (result.success) {

            window.location =
                "/panel/storage";

        }

    }

    catch (error) {

        console.error(error);

    }

}

// -------------------------------------------------
// Aktualisieren
// -------------------------------------------------

async function refreshPool() {

    await loadPool();

}

// -------------------------------------------------
// Buttons verbinden
// -------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    const exportButton =
        document.getElementById("exportButton");

    if (exportButton)
        exportButton.onclick =
            exportPool;

    const deleteButton =
        document.getElementById("deleteButton");

    if (deleteButton)
        deleteButton.onclick =
            deletePool;

    const refreshButton =
        document.getElementById("refreshButton");

    if (refreshButton)
        refreshButton.onclick =
            refreshPool;

    const resetButton =
        document.getElementById("resetButton");

    if (resetButton)
        resetButton.onclick =
            resetForm;

});

// -------------------------------------------------
// Automatische Aktualisierung
// -------------------------------------------------

setInterval(() => {

    loadPool();

}, 15000);