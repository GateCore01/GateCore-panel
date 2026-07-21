// storage-add.js – BTRFS Pool erstellen
document.addEventListener('DOMContentLoaded', loadServers);

async function loadServers() {
    const select = document.getElementById('server');
    select.innerHTML = `<option data-i18n="storage.loading">Lade Server...</option>`;
    try {
        const response = await fetch('/api/server/select', { credentials: 'include' });
        const servers = await response.json();
        select.innerHTML = '';
        if (servers.length === 0) {
            select.innerHTML = `<option value="" data-i18n="storage.no_servers">Keine Server</option>`;
        } else {
            servers.forEach(server => {
                const opt = document.createElement('option');
                opt.value = server.id;
                opt.textContent = server.name;
                select.appendChild(opt);
            });
        }
        window.translatePage?.();
    } catch (e) {
        select.innerHTML = `<option value="" data-i18n="storage.load_error">Fehler beim Laden</option>`;
    }
}

document.getElementById('createPoolForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('poolname').value.trim(),
        server_id: parseInt(document.getElementById('server').value),
        mountpoint: document.getElementById('mountpoint').value.trim(),
        raid_level: document.getElementById('raid').value,
        devices: document.getElementById('devices').value.split(',').map(s => s.trim()).filter(s => s)
    };
    if (data.devices.length < 1) {
        alert('Mindestens ein Gerät angeben.');
        return;
    }
    const status = document.getElementById('status');
    status.innerText = 'Pool wird erstellt...';
    try {
        const response = await fetch('/api/storage/pool/create', {
            method: 'POST',
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