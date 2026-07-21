// storage-snapshots.js – BTRFS Snapshots
document.addEventListener('DOMContentLoaded', loadPoolsAndSubvolumes);

async function loadPoolsAndSubvolumes() {
    const poolSelect = document.getElementById('pool');
    const subvolSelect = document.getElementById('subvolume');
    if (!poolSelect || !subvolSelect) return;
    poolSelect.innerHTML = `<option data-i18n="storage.loading">Lade Pools...</option>`;
    try {
        const response = await fetch('/api/storage/pools', { credentials: 'include' });
        const pools = await response.json();
        poolSelect.innerHTML = '';
        pools.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            poolSelect.appendChild(opt);
        });
        // Nach Pool‑Auswahl Subvolumes laden
        poolSelect.addEventListener('change', loadSubvolumesForPool);
        if (pools.length > 0) {
            poolSelect.value = pools[0].id;
            await loadSubvolumesForPool();
        }
        window.translatePage?.();
        loadSnapshotList();
    } catch (e) {
        poolSelect.innerHTML = `<option value="" data-i18n="storage.load_error">Fehler beim Laden</option>`;
    }
}

async function loadSubvolumesForPool() {
    const poolId = document.getElementById('pool').value;
    const subvolSelect = document.getElementById('subvolume');
    if (!poolId || !subvolSelect) return;
    subvolSelect.innerHTML = `<option data-i18n="storage.loading">Lade Subvolumes...</option>`;
    try {
        const response = await fetch(`/api/storage/subvolumes?pool_id=${poolId}`, { credentials: 'include' });
        const subvols = await response.json();
        subvolSelect.innerHTML = '';
        subvols.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name;
            subvolSelect.appendChild(opt);
        });
        window.translatePage?.();
    } catch (e) {
        subvolSelect.innerHTML = `<option value="" data-i18n="storage.load_error">Fehler beim Laden</option>`;
    }
}

document.getElementById('snapshotForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const subvolumeId = document.getElementById('subvolume').value;
    const snapshotName = document.getElementById('snapshotName').value.trim();
    if (!subvolumeId || !snapshotName) {
        alert('Bitte Subvolume und Snapshotnamen angeben.');
        return;
    }
    const status = document.getElementById('status');
    status.innerText = 'Snapshot wird erstellt...';
    try {
        const response = await fetch('/api/storage/snapshot/create', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subvolume_id: parseInt(subvolumeId), snapshot_name: snapshotName })
        });
        const result = await response.json();
        status.innerText = result.message;
        if (response.ok) {
            loadSnapshotList();
            document.getElementById('snapshotName').value = '';
        }
    } catch (err) {
        status.innerText = 'Fehler: ' + err.message;
    }
});

async function loadSnapshotList() {
    const tbody = document.getElementById('snapshotBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="4"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch('/api/storage/snapshots', { credentials: 'include' });
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

async function deleteSnapshot(id) {
    if (!confirm('Snapshot wirklich löschen?')) return;
    try {
        const response = await fetch(`/api/storage/snapshot/${id}`, { method: 'DELETE', credentials: 'include' });
        const result = await response.json();
        alert(result.message);
        loadSnapshotList();
    } catch (err) { alert('Fehler: ' + err.message); }
}