const serversApiPath = '/api/control/servers';
const hostsApiPath = '/api/hosts';

function showMessage(message, type = 'success') {
    const box = document.getElementById('message-box');
    if (!box) return;
    box.textContent = message;
    box.className = `message-box ${type}`;
}

async function loadHostsForSelection() {
    const select = document.getElementById('select-host');
    if (!select) return;

    try {
        const response = await fetch(hostsApiPath, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const hosts = Array.isArray(data) ? data : (data && Array.isArray(data.hosts) ? data.hosts : []);
        select.innerHTML = '<option value="">-- Host auswählen --</option>';

        hosts.forEach((host) => {
            const option = document.createElement('option');
            option.value = host.address || host.name || '';
            option.textContent = `${host.name || host.address || 'Host'} (${host.address || '-'})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.warn('Hosts konnten nicht geladen werden.', error);
        select.innerHTML = '<option value="">-- Host auswählen --</option>';
    }
}

async function loadServers() {
    try {
        const response = await fetch(serversApiPath, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const servers = Array.isArray(data) ? data : (data && Array.isArray(data.servers) ? data.servers : []);
        renderServerRows(servers);
    } catch (error) {
        console.warn('Server konnten nicht geladen werden.', error);
        renderServerRows([]);
    }
}

function renderServerRows(servers) {
    const body = document.getElementById('server-table-body');
    if (!body) return;

    body.innerHTML = '';
    if (!servers || servers.length === 0) {
        body.innerHTML = '<tr><td colspan="8">Keine Dienste gefunden.</td></tr>';
        return;
    }

    servers.forEach((server) => {
        const row = document.createElement('tr');
        const autostartText = server.autostart ? 'Ja' : 'Nein';
        const onlineText = server.onlineStatus || 'unknown';
        const serverTypeLabel = server.serverType === 'minecraft' ? 'Minecraft' : 'Systemd';
        row.innerHTML = `
            <td>${server.name || '-'}</td>
            <td>${server.host || '-'}</td>
            <td>${server.path || '-'}</td>
            <td>${serverTypeLabel}</td>
            <td>${server.startCommand || '-'}</td>
            <td>${server.serviceStartCommand || '-'}</td>
            <td>${autostartText}</td>
            <td>${onlineText}</td>
            <td><button type="button" class="delete-server-button" data-id="${server.id || ''}">Löschen</button></td>
        `;
        body.appendChild(row);
    });

    body.querySelectorAll('.delete-server-button').forEach((button) => {
        button.addEventListener('click', async () => {
            const id = button.getAttribute('data-id');
            if (!id) return;
            try {
                const response = await fetch(serversApiPath, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ id })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `HTTP ${response.status}`);
                }

                showMessage('Server erfolgreich gelöscht.', 'success');
                await loadServers();
            } catch (error) {
                showMessage(error.message || 'Server konnte nicht gelöscht werden.', 'error');
            }
        });
    });
}

async function handleSaveServer() {
    const nameField = document.getElementById('input-server-name');
    const hostField = document.getElementById('select-host');
    const pathField = document.getElementById('input-server-path');
    const serverTypeField = document.getElementById('select-server-kind');
    const minecraftCommandField = document.getElementById('input-minecraft-command');
    const systemdCommandField = document.getElementById('input-systemd-command');
    const autostartField = document.getElementById('input-autostart');
    const onlineStatusField = document.getElementById('select-online-status');

    if (!nameField || !hostField || !pathField || !serverTypeField || !minecraftCommandField || !systemdCommandField || !autostartField || !onlineStatusField) {
        showMessage('Formular nicht gefunden.', 'error');
        return;
    }

    const payload = {
        name: nameField.value.trim(),
        host: hostField.value.trim(),
        path: pathField.value.trim(),
        serverType: serverTypeField.value,
        startCommand: minecraftCommandField.value.trim(),
        serviceStartCommand: systemdCommandField.value.trim(),
        controlCommand: serverTypeField.value === 'minecraft' ? minecraftCommandField.value.trim() : systemdCommandField.value.trim(),
        autostart: autostartField.checked,
        onlineStatus: onlineStatusField.value,
        status: onlineStatusField.value,
        createdAt: new Date().toISOString()
    };

    if (!payload.name || !payload.host || !payload.path || (!payload.startCommand && !payload.serviceStartCommand)) {
        showMessage('Bitte alle Pflichtfelder ausfüllen.', 'error');
        return;
    }

    try {
        const response = await fetch(serversApiPath, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}`);
        }

        showMessage('Server erfolgreich gespeichert.', 'success');
        nameField.value = '';
        hostField.value = '';
        pathField.value = '';
        minecraftCommandField.value = '';
        systemdCommandField.value = '';
        autostartField.checked = true;
        onlineStatusField.value = 'offline';
        await loadServers();
    } catch (error) {
        showMessage(error.message || 'Server konnte nicht gespeichert werden.', 'error');
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    await loadHostsForSelection();
    await loadServers();
    document.getElementById('save-server-button')?.addEventListener('click', handleSaveServer);
});
