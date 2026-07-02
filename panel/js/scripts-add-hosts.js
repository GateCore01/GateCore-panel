const settingsStorageKey = 'gateCoreHostSettings';
const HOSTS_FILE_PATH = '/api/hosts';

function showMessage(message, type = 'success') {
    const box = document.getElementById('message-box');
    if (!box) return;
    box.textContent = message;
    box.className = `message-box ${type}`;
}

function getSavedSettings() {
    try {
        const saved = localStorage.getItem(settingsStorageKey);
        return saved ? JSON.parse(saved) : { sshUser: '', sshPort: '22', storagePath: '' };
    } catch (err) {
        return { sshUser: '', sshPort: '22', storagePath: '' };
    }
}

function saveSettings(settings) {
    localStorage.setItem(settingsStorageKey, JSON.stringify(settings));
}

async function fetchHostList() {
    try {
        const response = await fetch(HOSTS_FILE_PATH, {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        if (Array.isArray(data)) {
            return data;
        }

        if (data && data.hosts && Array.isArray(data.hosts)) {
            return data.hosts;
        }

        return [];
    } catch (error) {
        console.warn('Hosts konnten nicht geladen werden.', error);
        return [];
    }
}

async function saveHostToFile(host) {
    const response = await fetch(HOSTS_FILE_PATH, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(host)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    return response.json();
}

async function deleteHostFromFile(address) {
    const response = await fetch(HOSTS_FILE_PATH, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ address })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    return response.json();
}

function renderHostRows(hosts) {
    const body = document.getElementById('host-table-body');
    if (!body) return;

    body.innerHTML = '';
    if (!hosts || hosts.length === 0) {
        body.innerHTML = '<tr><td colspan="7">Keine Hosts gefunden.</td></tr>';
        return;
    }

    hosts.forEach((host) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${host.name || '-'}</td>
            <td>${host.address || '-'}</td>
            <td>${host.sshUser || '-'}</td>
            <td>${host.sshPort || '-'}</td>
            <td>${host.storagePath || '-'}</td>
            <td>${host.status || 'geladen'}</td>
            <td><button type="button" class="delete-host-button" data-address="${host.address || ''}">Löschen</button></td>
        `;
        body.appendChild(row);
    });

    body.querySelectorAll('.delete-host-button').forEach((button) => {
        button.addEventListener('click', async () => {
            const address = button.getAttribute('data-address');
            if (!address) return;
            try {
                await deleteHostFromFile(address);
                showMessage('Host erfolgreich gelöscht.', 'success');
                await loadHosts();
            } catch (error) {
                showMessage(error.message || 'Host konnte nicht gelöscht werden.', 'error');
            }
        });
    });
}

async function loadHosts() {
    const settings = getSavedSettings();
    const sshUserInput = document.getElementById('input-ssh-user');
    const sshPortInput = document.getElementById('input-ssh-port');
    const storagePathInput = document.getElementById('input-storage-path');

    if (sshUserInput) {
        sshUserInput.value = settings.sshUser || '';
    }
    if (sshPortInput) {
        sshPortInput.value = settings.sshPort || '22';
    }
    if (storagePathInput) {
        storagePathInput.value = settings.storagePath || '';
    }

    const hosts = await fetchHostList();
    renderHostRows(hosts);
}

async function handleSaveHost() {
    const nameField = document.getElementById('input-host-name');
    const addressField = document.getElementById('input-host-address');
    const sshUserField = document.getElementById('input-ssh-user');
    const sshPasswordField = document.getElementById('input-ssh-password');
    const sshPortField = document.getElementById('input-ssh-port');
    const storagePathField = document.getElementById('input-storage-path');

    if (!nameField || !addressField || !sshUserField || !sshPortField || !storagePathField) {
        showMessage('Formular nicht gefunden.', 'error');
        return;
    }

    const name = nameField.value.trim();
    const address = addressField.value.trim();
    const sshUser = sshUserField.value.trim();
    const sshPassword = sshPasswordField ? sshPasswordField.value : '';
    const sshPort = (sshPortField.value || '22').trim();
    const storagePath = storagePathField.value.trim();

    if (!name || !address) {
        showMessage('Bitte gib einen Hostnamen und eine Adresse ein.', 'error');
        return;
    }

    saveSettings({ sshUser, sshPort, storagePath });

    const newHost = {
        name,
        address,
        sshUser,
        sshPassword,
        sshPort,
        storagePath,
        status: 'gespeichert'
    };

    try {
        await saveHostToFile(newHost);
        showMessage('Host erfolgreich gespeichert.', 'success');
    } catch (error) {
        showMessage(error.message || 'Host konnte nicht gespeichert werden.', 'error');
        return;
    }

    nameField.value = '';
    addressField.value = '';
    if (sshUserField) {
        sshUserField.value = '';
    }
    if (sshPasswordField) {
        sshPasswordField.value = '';
    }
    if (sshPortField) {
        sshPortField.value = '22';
    }
    if (storagePathField) {
        storagePathField.value = '';
    }
    await loadHosts();
}

function buildCsvText(hosts) {
    const header = ['name', 'address', 'sshUser', 'sshPort', 'storagePath', 'status'];
    const rows = hosts.map(host => [host.name || '', host.address || '', host.sshUser || '', host.sshPort || '', host.storagePath || '', host.status || '']);
    const csvLines = [header.join(','), ...rows.map(row => row.map(value => `"${String(value).replace(/"/g, '""')}"`).join(','))];
    return csvLines.join('\r\n');
}

function downloadCsv(content, filename = 'hosts.csv') {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

async function exportHostsAsCsv() {
    const hosts = await fetchHostList();
    const csvText = buildCsvText(hosts);
    downloadCsv(csvText, 'hosts.csv');
}

function bindSaveButton() {
    const saveButton = document.getElementById('save-host-button');
    if (saveButton) {
        saveButton.addEventListener('click', handleSaveHost);
    }

    const exportButton = document.getElementById('export-csv-button');
    if (exportButton) {
        exportButton.addEventListener('click', exportHostsAsCsv);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    bindSaveButton();
    loadHosts();
});
