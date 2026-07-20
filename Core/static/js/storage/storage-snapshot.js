document.addEventListener("DOMContentLoaded", () => {
    loadSnapshots();
});

function getPool() {
    const params = new URLSearchParams(window.location.search);
    return params.get("pool");
}

async function loadSnapshots() {
    const pool = getPool();
    if (!pool) {
        document.getElementById("status").innerHTML = "Kein Pool ausgewählt.";
        return;
    }
    const tbody = document.getElementById("snapshotBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="7"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/storage/snapshots/" + encodeURIComponent(pool));
        const snapshots = await response.json();
        tbody.innerHTML = "";
        if (snapshots.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-row" data-i18n="storage.no_snapshots">Keine Snapshots vorhanden.</td></tr>`;
            translatePage();
            return;
        }
        snapshots.forEach(snap => {
            tbody.innerHTML += `
            <tr>
                <td>${snap.name}</td>
                <td>${snap.pool}</td>
                <td>${snap.dataset}</td>
                <td>${snap.size}</td>
                <td>${snap.created}</td>
                <td>${snap.description}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-test" data-i18n="storage.rollback_snapshot" onclick="rollbackSnapshot('${snap.name}')">Rollback</button>
                        <button class="btn-edit" data-i18n="storage.clone_snapshot" onclick="cloneSnapshot('${snap.name}')">Klonen</button>
                        <button class="btn-edit" data-i18n="storage.rename_snapshot" onclick="renameSnapshot('${snap.name}')">Umbenennen</button>
                        <button class="btn-delete" data-i18n="storage.delete_snapshot" onclick="deleteSnapshot('${snap.name}')">Löschen</button>
                    </div>
                </td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="7" class="empty-row">Fehler beim Laden der Snapshots.</td></tr>`;
    }
}

document.getElementById("snapshotForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const pool = getPool();
    const dataset = document.getElementById("dataset").value;
    const name = document.getElementById("snapshotName").value;
    const description = document.getElementById("description").value;
    const response = await fetch("/api/storage/snapshot/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool, dataset, name, description })
    });
    const result = await response.json();
    document.getElementById("status").innerHTML = result.message;
    if (result.success) loadSnapshots();
});

async function rollbackSnapshot(name) {
    if (!confirm("Rollback durchführen?")) return;
    const pool = getPool();
    const response = await fetch("/api/storage/snapshot/rollback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool, name })
    });
    const result = await response.json();
    alert(result.message);
    loadSnapshots();
}

async function cloneSnapshot(name) {
    const cloneName = prompt("Name des Klons:");
    if (!cloneName) return;
    const pool = getPool();
    const response = await fetch("/api/storage/snapshot/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool, snapshot: name, clone: cloneName })
    });
    const result = await response.json();
    alert(result.message);
    loadSnapshots();
}

async function renameSnapshot(oldName) {
    const newName = prompt("Neuer Snapshotname:", oldName);
    if (!newName) return;
    const pool = getPool();
    const response = await fetch("/api/storage/snapshot/rename", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool, old_name: oldName, new_name: newName })
    });
    const result = await response.json();
    alert(result.message);
    loadSnapshots();
}

async function deleteSnapshot(name) {
    if (!confirm("Snapshot wirklich löschen?")) return;
    const pool = getPool();
    const response = await fetch("/api/storage/snapshot/delete", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool, name })
    });
    const result = await response.json();
    alert(result.message);
    loadSnapshots();
}