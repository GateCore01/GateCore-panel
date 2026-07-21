// storage-details.js – BTRFS Pool Details mit Subvolumes und Snapshots
document.addEventListener('DOMContentLoaded', () => {
    loadPoolDetails();
    loadSubvolumes();
    loadSnapshots();
});

function getPoolId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

async function loadPoolDetails() {
    const id = getPoolId();
    if (!id) {
        document.getElementById('status').innerHTML = 'Keine Pool‑ID angegeben.';
        return;
    }
    try {
        const response = await fetch(`/api/storage/pools?pool_id=${id}`, { credentials: 'include' });
        const pools = await response.json();
        if (pools.length === 0) {
            document.getElementById('status').innerHTML = 'Pool nicht gefunden.';
            return;
        }
        const p = pools[0];
        setText('poolName', p.name);
        setText('serverName', p.server_id); // ggf. Servername laden
        setText('poolRaid', p.raid_level);
        setText('poolMountpoint', p.mountpoint);
        setText('poolDevices', p.devices ? JSON.parse(p.devices).join(', ') : '-');
        setText('poolCreated', p.created);
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        document.getElementById('status').innerHTML = 'Pool konnte nicht geladen werden.';
    }
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? '-';
}

async function loadSubvolumes() {
    const id = getPoolId();
    const tbody = document.getElementById('subvolumeBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="3"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch(`/api/storage/subvolumes?pool_id=${id}`, { credentials: 'include' });
        const subvols = await response.json();
        tbody.innerHTML = '';
        if (subvols.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="empty-row" data-i18n="storage.no_subvolumes">Keine Subvolumes.</td></tr>`;
        } else {
            subvols.forEach(s => {
                tbody.innerHTML += `
                <tr>
                    <td>${s.name}</td>
                    <td>${s.path}</td>
                    <td><button class="btn-delete" onclick="deleteSubvolume(${s.id})" data-i18n="storage.delete">Löschen</button></td>
                </tr>`;
            });
        }
        window.translatePage?.();
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="3" class="empty-row">Fehler beim Laden der Subvolumes.</td></tr>`;
    }
}

async function loadSnapshots() {
    const id = getPoolId();
    const tbody = document.getElementById('snapshotBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="4"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch(`/api/storage/snapshots?pool_id=${id}`, { credentials: 'include' });
        const snaps = await response.json();
        tbody.innerHTML = '';
        if (snaps.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-row" data-i18n="storage.no_snapshots">Keine Snapshots.</td></tr>`;
        } else {
            snaps.forEach(s => {
                tbody.innerHTML += `
                <tr>
                    <td>${s.snapshot_name}</td>
                    <td>${s.path}</td>
                    <td>${s.created}</td>
                    <td><button class="btn-delete" onclick="deleteSnapshot(${s.id})" data-i18n="storage.delete">Löschen</button></td>
                </tr>`;
            });
        }
        window.translatePage?.();
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-row">Fehler beim Laden der Snapshots.</td></tr>`;
    }
}

async function deleteSubvolume(id) {
    if (!confirm('Subvolume wirklich löschen?')) return;
    try {
        const response = await fetch(`/api/storage/subvolume/${id}`, { method: 'DELETE', credentials: 'include' });
        const result = await response.json();
        alert(result.message);
        loadSubvolumes();
    } catch (err) { alert('Fehler: ' + err.message); }
}

async function deleteSnapshot(id) {
    if (!confirm('Snapshot wirklich löschen?')) return;
    try {
        const response = await fetch(`/api/storage/snapshot/${id}`, { method: 'DELETE', credentials: 'include' });
        const result = await response.json();
        alert(result.message);
        loadSnapshots();
    } catch (err) { alert('Fehler: ' + err.message); }
}