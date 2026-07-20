// storage.js – mit korrektem /api/storage/disks
document.addEventListener("DOMContentLoaded", () => {
    loadStorage();
    setInterval(loadStorage, 15000);
});

async function loadStorage() {
    await loadPools();
    await loadDisks();
}

async function loadPools() {
    const tbody = document.getElementById("poolBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="8"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/list", { credentials: "include" });
        const data = await response.json();
        tbody.innerHTML = "";
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-row" data-i18n="storage.no_pools">Keine Pools vorhanden.</td></tr>`;
            window.translatePage?.();
            return;
        }
        data.forEach(pool => {
            tbody.innerHTML += `
            <tr>
                <td>${pool.name || pool.pool || '-'}</td>
                <td>${pool.type || pool.raid || '-'}</td>
                <td>${pool.size || '-'}</td>
                <td>${pool.used || '-'}</td>
                <td>${pool.free || '-'}</td>
                <td>${pool.usage || '-'}</td>
                <td>${pool.status || 'unknown'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-test" data-i18n="storage.details" onclick="detailsPool('${pool.name || pool.pool}')">Details</button>
                        <button class="btn-edit" data-i18n="storage.edit" onclick="editPool('${pool.name || pool.pool}')">Bearbeiten</button>
                        <button class="btn-delete" data-i18n="storage.delete" onclick="deletePool('${pool.name || pool.pool}')">Löschen</button>
                    </div>
                </td>
            </tr>`;
        });
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-row">Fehler beim Laden der Pools.</td></tr>`;
    }
}

async function loadDisks() {
    const tbody = document.getElementById("diskBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="8"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/disks", { credentials: "include" });
        const data = await response.json();
        tbody.innerHTML = "";
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-row" data-i18n="storage.no_disks">Keine Festplatten gefunden.</td></tr>`;
            window.translatePage?.();
            return;
        }
        data.forEach(disk => {
            tbody.innerHTML += `
            <tr>
                <td>${disk.server || '-'}</td>
                <td>${disk.device || '-'}</td>
                <td>${disk.model || '-'}</td>
                <td>${disk.size || '-'}</td>
                <td>${disk.filesystem || '-'}</td>
                <td>${disk.mountpoint || '-'}</td>
                <td>${disk.status || 'unknown'}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-test" data-i18n="storage.smart" onclick="smartDisk('${disk.device}')">SMART</button>
                        <button class="btn-edit" data-i18n="button.edit" onclick="editDisk('${disk.device}')">Bearbeiten</button>
                    </div>
                </td>
            </tr>`;
        });
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-row">Fehler beim Laden der Festplatten: ${error.message}</td></tr>`;
    }
}

function detailsPool(pool) { window.location = "/panel/storage/details?pool=" + encodeURIComponent(pool); }
function editPool(pool) { window.location = "/panel/storage/edit?pool=" + encodeURIComponent(pool); }
function smartDisk(disk) { window.location = "/panel/storage/smart?disk=" + encodeURIComponent(disk); }
function editDisk(disk) { alert("Festplatte " + disk + " bearbeiten folgt später."); }

async function deletePool(pool) {
    if (!confirm(`Pool "${pool}" wirklich löschen?`)) return;
    try {
        const response = await fetch("/api/storage/delete/" + encodeURIComponent(pool), { method: "DELETE", credentials: "include" });
        const result = await response.json();
        alert(result.message);
        loadStorage();
    } catch (error) { console.error(error); }
}