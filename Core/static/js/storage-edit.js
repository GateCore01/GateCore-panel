// storage-edit.js – BTRFS Pool bearbeiten
document.addEventListener('DOMContentLoaded', loadPool);

function getPoolId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

async function loadPool() {
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
        document.getElementById('poolname').value = p.name;
        document.getElementById('raid').value = p.raid_level;
        document.getElementById('mountpoint').value = p.mountpoint;
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        document.getElementById('status').innerHTML = 'Pool konnte nicht geladen werden.';
    }
}

document.getElementById('editPoolForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = getPoolId();
    const data = {
        id: id,
        name: document.getElementById('poolname').value.trim(),
        raid_level: document.getElementById('raid').value,
        mountpoint: document.getElementById('mountpoint').value.trim()
    };
    const status = document.getElementById('status');
    status.innerText = 'Speichere...';
    try {
        const response = await fetch(`/api/storage/pool/${id}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        status.innerText = result.message;
        if (response.ok) {
            setTimeout(() => window.location = '/panel/storage', 1500);
        }
    } catch (err) {
        status.innerText = 'Fehler: ' + err.message;
    }
});