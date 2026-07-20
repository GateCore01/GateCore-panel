document.addEventListener("DOMContentLoaded", () => {
    loadPool();
    loadDisks();
    loadDatasets();
});

function getPool() {
    const params = new URLSearchParams(window.location.search);
    return params.get("pool");
}

async function loadPool() {
    const pool = getPool();
    if (!pool) {
        document.getElementById("status").innerHTML = "Kein Pool angegeben.";
        return;
    }
    try {
        const response = await fetch("/api/storage/details/" + encodeURIComponent(pool));
        const data = await response.json();
        fillGeneral(data);
        fillProperties(data);
        fillUsage(data);
        translatePage();
    } catch (error) {
        console.error(error);
        document.getElementById("status").innerHTML = "Pool konnte nicht geladen werden.";
    }
}

function fillGeneral(data) {
    setText("poolName", data.name);
    setText("poolType", data.type);
    setText("poolStatus", data.status);
    setText("poolSize", data.size);
    setText("poolUsed", data.used);
    setText("poolFree", data.free);
    setText("poolHealth", data.health);
    setText("poolVersion", data.version);
    setText("serverName", data.server);
}

function fillProperties(data) {
    setText("poolCompression", data.compression);
    setText("poolAtime", data.atime);
    setText("poolAutotrim", data.autotrim);
}

function fillUsage(data) {
    setText("poolUsage", data.usage + " %");
    setText("poolFragmentation", data.fragmentation);
    setText("poolDedup", data.dedup);
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "-";
}

async function loadDisks() {
    const pool = getPool();
    const tbody = document.getElementById("diskBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="7"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/disks/" + encodeURIComponent(pool));
        const disks = await response.json();
        tbody.innerHTML = "";
        if (disks.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-row" data-i18n="storage.no_disks_found">Keine Laufwerke vorhanden.</td></tr>`;
            translatePage();
            return;
        }
        disks.forEach(disk => {
            tbody.innerHTML += `
            <tr>
                <td>${disk.device}</td>
                <td>${disk.serial}</td>
                <td>${disk.model}</td>
                <td>${disk.size}</td>
                <td>${disk.status}</td>
                <td>${disk.temperature}</td>
                <td><button class="btn-test" data-i18n="storage.smart" onclick="smartDisk('${disk.device}')">SMART</button></td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Fehler beim Laden der Festplatten.</td></tr>`;
    }
}

async function loadDatasets() {
    const pool = getPool();
    const tbody = document.getElementById("datasetBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="7"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/datasets/" + encodeURIComponent(pool));
        const datasets = await response.json();
        tbody.innerHTML = "";
        if (datasets.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-row" data-i18n="storage.no_datasets">Keine Datensätze vorhanden.</td></tr>`;
            translatePage();
            return;
        }
        datasets.forEach(ds => {
            tbody.innerHTML += `
            <tr>
                <td>${ds.name}</td>
                <td>${ds.mountpoint}</td>
                <td>${ds.compression}</td>
                <td>${ds.size}</td>
                <td>${ds.used}</td>
                <td>${ds.free}</td>
                <td><button class="btn-edit" data-i18n="button.edit" onclick="editDataset('${ds.name}')">Bearbeiten</button></td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Fehler beim Laden der Datensätze.</td></tr>`;
    }
}

function editDataset(name) {
    alert("Dataset " + name + " bearbeiten folgt später.");
}

function smartDisk(disk) {
    window.location = "/panel/storage/smart?disk=" + encodeURIComponent(disk);
}

document.getElementById("refreshButton")?.addEventListener("click", () => { loadPool(); loadDisks(); loadDatasets(); });
document.getElementById("snapshotButton")?.addEventListener("click", () => {
    window.location = "/panel/storage/snapshots?pool=" + encodeURIComponent(getPool());
});
document.getElementById("scrubButton")?.addEventListener("click", () => {
    window.location = "/panel/storage/scrub?pool=" + encodeURIComponent(getPool());
});
document.getElementById("smartButton")?.addEventListener("click", () => {
    window.location = "/panel/storage/smart?pool=" + encodeURIComponent(getPool());
});
document.getElementById("editButton")?.addEventListener("click", () => {
    window.location = "/panel/storage/edit?pool=" + encodeURIComponent(getPool());
});
document.getElementById("deleteButton")?.addEventListener("click", async () => {
    if (!confirm("Pool wirklich löschen?")) return;
    const response = await fetch("/api/storage/delete/" + encodeURIComponent(getPool()), { method: "DELETE" });
    const result = await response.json();
    alert(result.message);
    if (result.success) window.location = "/panel/storage";
});