document.addEventListener("DOMContentLoaded", () => {
    loadServers();
    document.getElementById("server").addEventListener("change", loadDisks);
    document.getElementById("raid").addEventListener("change", validateRaid);
});

async function loadServers() {
    const select = document.getElementById("server");
    select.innerHTML = `<option data-i18n="storage.loading">Lade Server...</option>`;
    try {
        const response = await fetch("/api/server/list");
        const servers = await response.json();
        select.innerHTML = "";
        if (servers.length === 0) {
            select.innerHTML = `<option value="" data-i18n="storage.no_servers">Keine Server</option>`;
        } else {
            servers.forEach(server => {
                select.innerHTML += `<option value="${server.id}">${server.name}</option>`;
            });
            loadDisks();
        }
        translatePage();
    } catch (error) {
        console.error(error);
        select.innerHTML = `<option value="" data-i18n="storage.load_error">Fehler beim Laden</option>`;
    }
}

async function loadDisks() {
    const server = document.getElementById("server").value;
    const tbody = document.getElementById("diskBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="5"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/disks/" + server);
        const disks = await response.json();
        tbody.innerHTML = "";
        if (disks.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-row" data-i18n="storage.no_disks_found">Keine freien Laufwerke gefunden.</td></tr>`;
            translatePage();
            return;
        }
        disks.forEach(disk => {
            tbody.innerHTML += `
            <tr>
                <td><input type="checkbox" class="diskCheck" value="${disk.device}" onchange="validateRaid()"></td>
                <td>${disk.device}</td>
                <td>${disk.size}</td>
                <td>${disk.model}</td>
                <td>${disk.status}</td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="5" class="empty-row">Fehler beim Laden der Laufwerke.</td></tr>`;
    }
}

function getSelectedDisks() {
    const disks = [];
    document.querySelectorAll(".diskCheck:checked").forEach(item => disks.push(item.value));
    return disks;
}

function validateRaid() {
    const raid = document.getElementById("raid").value;
    const count = getSelectedDisks().length;
    let needed = 2;
    switch (raid) {
        case "mirror": needed = 2; break;
        case "stripe": needed = 2; break;
        case "raidz": needed = 3; break;
        case "raidz2": needed = 4; break;
        case "raidz3": needed = 5; break;
    }
    const status = document.getElementById("status");
    if (count < needed) {
        status.className = "status-error";
        status.innerHTML = `Für ${raid.toUpperCase()} werden mindestens ${needed} Laufwerke benötigt.`;
        return false;
    }
    status.className = "status-success";
    status.innerHTML = `${count} Laufwerke ausgewählt.`;
    return true;
}

document.getElementById("createPoolForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!validateRaid()) return;
    const button = event.submitter;
    button.disabled = true;
    button.innerHTML = "Speichere...";

    const data = {
        server: document.getElementById("server").value,
        name: document.getElementById("poolname").value,
        raid: document.getElementById("raid").value,
        compression: document.getElementById("compression").value,
        atime: document.getElementById("atime").value,
        autotrim: document.getElementById("autotrim").value,
        disks: getSelectedDisks()
    };

    try {
        const response = await fetch("/api/storage/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            document.getElementById("status").className = "status-success";
            document.getElementById("status").innerHTML = result.message;
            setTimeout(() => { window.location = "/panel/storage"; }, 1200);
        } else {
            document.getElementById("status").className = "status-error";
            document.getElementById("status").innerHTML = result.message;
        }
    } catch (error) {
        console.error(error);
        document.getElementById("status").className = "status-error";
        document.getElementById("status").innerHTML = "Server nicht erreichbar.";
    }
    button.disabled = false;
    button.innerHTML = "Speicher erstellen";
});