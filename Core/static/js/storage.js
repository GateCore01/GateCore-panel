// storage.js – BTRFS Pools & Subvolumes
async function loadStorage() {
    await loadPools();
    await loadSubvolumes();
}

async function loadPools() {
    const tbody = document.getElementById('poolBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch('/api/storage/pools', { credentials: 'include' });
        const pools = await response.json();
        tbody.innerHTML = '';
        if (pools.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="storage.no_pools">Keine Pools vorhanden.</td></tr>`;
        } else {
            pools.forEach(p => {
                const devices = p.devices ? JSON.parse(p.devices).join(', ') : '-';
                tbody.innerHTML += `
                <tr>
                    <td>${p.name}</td>
                    <td>${p.raid_level}</td>
                    <td>${p.mountpoint}</td>
                    <td>${devices}</td>
                    <td>${p.created}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn-delete" onclick="deletePool(${p.id})" data-i18n="storage.delete">Löschen</button>
                            <button onclick="showSubvolumes(${p.id})" data-i18n="storage.subvolumes">Subvolumes</button>
                            <button onclick="scrubPool(${p.id})" data-i18n="storage.scrub">Scrub</button>
                        </div>
                    </td>
                </tr>`;
            });
        }
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Fehler beim Laden der Pools.</td></tr>`;
    }
}

async function loadSubvolumes(poolId = null) {
    const tbody = document.getElementById('subvolumeBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="5"><div class="loading-spinner"></div></td></tr>`;
    let url = '/api/storage/subvolumes';
    if (poolId) url += `?pool_id=${poolId}`;
    try {
        const response = await fetch(url, { credentials: 'include' });
        const subvols = await response.json();
        tbody.innerHTML = '';
        if (subvols.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-row" data-i18n="storage.no_subvolumes">Keine Subvolumes.</td></tr>`;
        } else {
            subvols.forEach(s => {
                tbody.innerHTML += `
                <tr>
                    <td>${s.id}</td>
                    <td>${s.name}</td>
                    <td>${s.path}</td>
                    <td>${s.pool_id}</td>
                    <td><button class="btn-delete" onclick="deleteSubvolume(${s.id})" data-i18n="storage.delete">Löschen</button></td>
                </tr>`;
            });
        }
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="5" class="empty-row">Fehler beim Laden der Subvolumes.</td></tr>`;
    }
}

async function deletePool(id) {
    if (!confirm('Pool wirklich löschen?')) return;
    try {
        const response = await fetch(`/api/storage/pool/${id}`, { method: 'DELETE', credentials: 'include' });
        const result = await response.json();
        alert(result.message);
        loadStorage();
    } catch (err) { alert('Fehler: ' + err.message); }
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

async function scrubPool(id) {
    try {
        const response = await fetch(`/api/storage/pool/${id}/scrub/start`, { method: 'POST', credentials: 'include' });
        const result = await response.json();
        alert(result.message || 'Scrub gestartet');
    } catch (err) { alert('Fehler: ' + err.message); }
}

function showSubvolumes(poolId) {
    loadSubvolumes(poolId);
}

document.addEventListener('DOMContentLoaded', loadStorage);
setInterval(loadStorage, 30000);