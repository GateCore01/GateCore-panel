const SERVER_ADD_API_URL = '/api/control/servers';
const SERVER_ADD_FILES_API_URL = '/api/servers';
const SERVER_ADD_HOSTS_API_URL = '/api/hosts';

function getServerAddElement(id) {
    return document.getElementById(id);
}

function showServerAddMessage(message, type = 'success') {
    const box = getServerAddElement('message-box');
    if (!box) return;
    box.textContent = message || '';
    box.className = `message-box ${type}`;
}

async function fetchServerAddJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            ...(options.headers || {})
        },
        ...options
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
    }

    return data;
}

function normalizeServerList(payload) {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.servers)) return payload.servers;
    return [];
}

function normalizeHostList(payload) {
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload?.hosts)) return payload.hosts;
    return [];
}

function getSelectedHost(hosts) {
    const select = getServerAddElement('select-host');
    if (!select) return null;
    return hosts.find((host) => {
        const address = String(host.address || '').trim();
        const name = String(host.name || '').trim();
        return select.value === address || select.value === name;
    }) || null;
}

function buildServerPath(host, serverName) {
    const basePath = String(host?.storagePath || '/var/www/html').trim() || '/var/www/html';
    const safeName = String(serverName || 'service')
        .trim()
        .replace(/[^A-Za-z0-9._-]+/g, '-')
        .replace(/^-+|-+$/g, '') || 'service';

    return `${basePath.replace(/\/+$/, '')}/${safeName}`;
}

function buildServiceControlCommand(type, serverName) {
    const name = String(serverName || '').trim();
    if (type === 'windows') {
        return `Start-Service -Name "${name.replace(/"/g, '\\"')}"`;
    }

    return `systemctl start ${name}`;
}

function renderHostOptions(hosts) {
    const select = getServerAddElement('select-host');
    if (!select) return;

    select.innerHTML = '<option value="">-- Host auswählen --</option>';
    hosts.forEach((host) => {
        const option = document.createElement('option');
        const address = String(host.address || '').trim();
        const name = String(host.name || '').trim();
        option.value = address || name;
        option.textContent = name && address ? `${name} (${address})` : (name || address || 'Unbekannter Host');
        select.appendChild(option);
    });
}

function renderServerRows(servers) {
    const body = getServerAddElement('server-table-body');
    if (!body) return;

    body.innerHTML = '';
    if (!servers.length) {
        body.innerHTML = '<tr><td colspan="6">Keine Dienste gefunden.</td></tr>';
        return;
    }

    servers.forEach((server) => {
        const row = document.createElement('tr');
        const serverType = server.serverType || server.type || server.system || 'linux';
        const serverTypeLabel = serverType === 'windows' ? 'Windows' : 'Linux';
        row.innerHTML = `
            <td>${server.name || '-'}</td>
            <td>${server.host || '-'}</td>
            <td>${serverTypeLabel}</td>
            <td>${server.startCommand || '-'}</td>
            <td>${server.autostart ? 'Ja' : 'Nein'}</td>
            <td><button type="button" class="delete-server-button" data-id="${server.id || ''}">Löschen</button></td>
        `;
        body.appendChild(row);
    });

    body.querySelectorAll('.delete-server-button').forEach((button) => {
        button.addEventListener('click', async () => {
            const id = button.getAttribute('data-id');
            if (!id || !window.confirm('Diesen Dienst wirklich löschen?')) return;

            try {
                button.disabled = true;
                await fetchServerAddJson(SERVER_ADD_API_URL, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id })
                });
                showServerAddMessage('Server erfolgreich gelöscht.', 'success');
                await loadServerAddData();
            } catch (error) {
                showServerAddMessage(error.message || 'Server konnte nicht gelöscht werden.', 'error');
                button.disabled = false;
            }
        });
    });
}

async function loadServerAddData() {
    try {
        const [hostsPayload, serversPayload] = await Promise.all([
            fetchServerAddJson(SERVER_ADD_HOSTS_API_URL),
            fetchServerAddJson(SERVER_ADD_API_URL)
        ]);

        const hosts = normalizeHostList(hostsPayload);
        const servers = normalizeServerList(serversPayload);
        renderHostOptions(hosts);
        renderServerRows(servers);
        return { hosts, servers };
    } catch (error) {
        showServerAddMessage(error.message || 'Daten konnten nicht geladen werden.', 'error');
        renderServerRows([]);
        return { hosts: [], servers: [] };
    }
}

async function uploadInitialServerFile(serverId, file) {
    const response = await fetch(`${SERVER_ADD_FILES_API_URL}/${serverId}/files`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/octet-stream',
            'X-File-Name': file.name
        },
        body: file
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.message || 'Upload fehlgeschlagen');
    }

    return data;
}

function getServerFormPayload(hosts) {
    const type = getServerAddElement('select-server-system')?.value || 'linux';
    const name = getServerAddElement('input-server-name')?.value.trim() || '';
    const startCommand = getServerAddElement('input-start-command')?.value.trim() || '';
    const autostart = Boolean(getServerAddElement('input-autostart')?.checked);
    const host = getSelectedHost(hosts);

    if (!name) {
        throw new Error('Bitte gib einen Dienst-Namen ein.');
    }
    if (!host) {
        throw new Error('Bitte wähle einen Host aus.');
    }

    if (!startCommand) {
        throw new Error('Bitte gib einen Startbefehl ein.');
    }

    const controlCommand = buildServiceControlCommand(type, name);

    return {
        type,
        system: type,
        serverType: type,
        name,
        host: host.address || host.name,
        path: buildServerPath(host, name),
        startCommand,
        systemdCommand: controlCommand,
        serviceStartCommand: controlCommand,
        controlCommand,
        autostart,
        onlineStatus: 'offline',
        status: 'offline',
        createdAt: new Date().toISOString()
    };
}

function resetServerForm() {
    const fields = [
        'input-server-name',
        'input-start-command',
        'input-upload'
    ];

    fields.forEach((id) => {
        const field = getServerAddElement(id);
        if (field) field.value = '';
    });

    const autostart = getServerAddElement('input-autostart');
    if (autostart) autostart.checked = true;
}

async function handleSaveServer() {
    const button = getServerAddElement('save-server-button');
    if (button) button.disabled = true;

    try {
        showServerAddMessage('Dienst wird gespeichert...', 'success');
        const hostsPayload = await fetchServerAddJson(SERVER_ADD_HOSTS_API_URL);
        const hosts = normalizeHostList(hostsPayload);
        const payload = getServerFormPayload(hosts);

        const result = await fetchServerAddJson(SERVER_ADD_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const servers = normalizeServerList(result);
        const savedServer = servers.find((server) => (
            String(server.name || '') === payload.name &&
            String(server.host || '') === payload.host
        )) || servers[servers.length - 1] || result.server || payload;

        const uploadFile = getServerAddElement('input-upload')?.files?.[0];
        if (uploadFile && savedServer.id) {
            showServerAddMessage('Dienst gespeichert, Datei wird hochgeladen...', 'success');
            await uploadInitialServerFile(savedServer.id, uploadFile);
        }

        showServerAddMessage(uploadFile ? 'Dienst und Datei erfolgreich gespeichert.' : 'Dienst erfolgreich gespeichert.', 'success');
        resetServerForm();
        await loadServerAddData();
    } catch (error) {
        showServerAddMessage(error.message || 'Dienst konnte nicht gespeichert werden.', 'error');
    } finally {
        if (button) button.disabled = false;
    }
}

function bindServerAddEvents() {
    const saveButton = getServerAddElement('save-server-button');
    if (saveButton) {
        saveButton.addEventListener('click', handleSaveServer);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    bindServerAddEvents();
    await loadServerAddData();
});
