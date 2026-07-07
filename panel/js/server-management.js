const SERVER_API_URL = '/api/servers';
let activeServer = null;
let activeManagerPath = '';

function getServerListContainer() {
    return document.getElementById('server-list');
}

function getEmptyState() {
    return document.getElementById('server-empty-state');
}

function getManagerModal() {
    return document.getElementById('file-manager-modal');
}

function setManagerStatus(message, isError = false) {
    const status = document.getElementById('file-manager-status');
    if (!status) return;
    status.textContent = message || '';
    status.style.color = isError ? '#b91c1c' : '#166534';
}

function setUploadProgress(label, percent = 0) {
    const progressLabel = document.getElementById('file-manager-progress-label');
    const progressBar = document.getElementById('file-manager-progress-bar');
    const progressTrack = document.querySelector('.file-manager-progress-track');
    const normalizedPercent = Math.max(0, Math.min(100, percent));
    if (progressLabel) {
        progressLabel.textContent = label || 'Bereit';
    }
    if (progressBar) {
        progressBar.style.width = `${normalizedPercent}%`;
    }
    if (progressTrack) {
        progressTrack.setAttribute('aria-valuenow', String(Math.round(normalizedPercent)));
    }
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: 'include',
        ...options
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.message || 'Anfrage fehlgeschlagen');
    }

    return data;
}

async function loadServers() {
    try {
        const servers = await fetchJson(SERVER_API_URL, { method: 'GET' });
        renderServerList(Array.isArray(servers) ? servers : []);
    } catch (error) {
        const container = getServerListContainer();
        if (container) {
            container.innerHTML = `<p class="server-error">${error.message}</p>`;
        }
    }
}

function renderServerList(servers) {
    const container = getServerListContainer();
    const emptyState = getEmptyState();

    if (!container) return;

    if (!servers.length) {
        container.innerHTML = '';
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        return;
    }

    if (emptyState) {
        emptyState.style.display = 'none';
    }

    container.innerHTML = '';

    servers.forEach((server) => {
        const card = document.createElement('article');
        card.className = 'server-card';
        card.innerHTML = `
            <div class="server-card-header">
                <div>
                    <h3>${server.name || 'Unbekannter Dienst'}</h3>
                    <p>${server.host || '-'}</p>
                </div>
                <span class="server-status ${server.onlineStatus || server.status || 'offline'}">${server.onlineStatus || server.status || 'offline'}</span>
            </div>
            <div class="server-meta">
                <span>Pfad: ${server.path || '-'}</span>
                <span>Start: ${server.startCommand || '-'}</span>
            </div>
            <div class="server-actions">
                <button type="button" class="server-action-button" data-action="files" data-id="${server.id || ''}">Datei-Manager</button>
                <button type="button" class="server-action-button secondary" data-action="delete" data-id="${server.id || ''}">Löschen</button>
            </div>
        `;
        container.appendChild(card);
    });

    container.querySelectorAll('[data-action="files"]').forEach((button) => {
        button.addEventListener('click', () => openFileManager(button.dataset.id));
    });

    container.querySelectorAll('[data-action="delete"]').forEach((button) => {
        button.addEventListener('click', async () => {
            const serverId = button.dataset.id;
            if (!serverId || !window.confirm('Diesen Dienst wirklich aus der Konfiguration entfernen?')) {
                return;
            }

            try {
                await fetchJson(SERVER_API_URL, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: serverId })
                });
                await loadServers();
            } catch (error) {
                alert(error.message || 'Server konnte nicht entfernt werden.');
            }
        });
    });
}

async function openFileManager(serverId) {
    const servers = await fetchJson(SERVER_API_URL, { method: 'GET' });
    const server = Array.isArray(servers) ? servers.find((item) => String(item.id) === String(serverId)) : null;

    if (!server) {
        alert('Server nicht gefunden.');
        return;
    }

    activeServer = server;
    activeManagerPath = '';

    const modal = getManagerModal();
    const title = document.getElementById('file-manager-title');
    const pathLabel = document.getElementById('file-manager-path');
    if (modal) {
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
    }
    if (title) {
        title.textContent = `Datei-Manager · ${server.name || 'Dienst'}`;
    }
    if (pathLabel) {
        pathLabel.textContent = 'Pfad wird geladen...';
    }
    setManagerStatus('');
    setUploadProgress('Bereit', 0);

    await loadFileManagerEntries(server, '');
}

async function loadFileManagerEntries(server, currentPath = '') {
    try {
        const data = await fetchJson(`${SERVER_API_URL}/${server.id}/files?path=${encodeURIComponent(currentPath || '')}`, {
            method: 'GET'
        });

        activeManagerPath = currentPath || '';
        const pathLabel = document.getElementById('file-manager-path');
        const entriesContainer = document.getElementById('file-manager-entries');
        if (pathLabel) {
            pathLabel.textContent = data.path || '-';
        }
        if (!entriesContainer) return;

        if (!Array.isArray(data.entries) || !data.entries.length) {
            entriesContainer.innerHTML = '<p class="file-manager-empty">Dieser Ordner ist leer.</p>';
            return;
        }

        entriesContainer.innerHTML = '';
        const list = document.createElement('ul');
        list.className = 'file-manager-list';

        data.entries.forEach((entry) => {
            const item = document.createElement('li');
            item.className = 'file-manager-entry';
            const childPath = currentPath ? `${currentPath}/${entry.name}` : entry.name;
            item.innerHTML = `
                <span>${entry.name || '-'}</span>
                <div class="file-manager-entry-actions">
                    ${entry.isDirectory ? '<span class="file-manager-entry-badge">Ordner</span>' : '<button type="button" class="file-manager-inline-button" data-action="download" data-name="' + encodeURIComponent(entry.name || '') + '" data-path="' + encodeURIComponent(childPath) + '">Download</button><button type="button" class="file-manager-inline-button danger" data-action="delete" data-name="' + encodeURIComponent(entry.name || '') + '" data-path="' + encodeURIComponent(childPath) + '">Löschen</button>'}
                </div>
            `;
            if (entry.isDirectory) {
                item.addEventListener('click', (event) => {
                    if (event.target.closest('button')) return;
                    loadFileManagerEntries(server, childPath);
                });
                item.classList.add('is-directory');
            }
            list.appendChild(item);
        });

        list.querySelectorAll('[data-action="download"]').forEach((button) => {
            button.addEventListener('click', async () => {
                const name = decodeURIComponent(button.getAttribute('data-name') || '');
                const path = decodeURIComponent(button.getAttribute('data-path') || '');
                try {
                    button.disabled = true;
                    const response = await fetch(`${SERVER_API_URL}/${server.id}/files/download?path=${encodeURIComponent(path)}`, {
                        credentials: 'include'
                    });
                    if (!response.ok) {
                        const data = await response.json().catch(() => ({}));
                        throw new Error(data.message || 'Download fehlgeschlagen');
                    }
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = name;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                    setManagerStatus(`Datei heruntergeladen: ${name}`);
                } catch (error) {
                    setManagerStatus(error.message || 'Download fehlgeschlagen.', true);
                } finally {
                    button.disabled = false;
                }
            });
        });

        list.querySelectorAll('[data-action="delete"]').forEach((button) => {
            button.addEventListener('click', async () => {
                const name = decodeURIComponent(button.getAttribute('data-name') || '');
                const path = decodeURIComponent(button.getAttribute('data-path') || '');
                if (!window.confirm(`"${name}" wirklich löschen?`)) return;
                try {
                    button.disabled = true;
                    const response = await fetch(`${SERVER_API_URL}/${server.id}/files/delete?path=${encodeURIComponent(path)}`, {
                        credentials: 'include',
                        method: 'DELETE'
                    });
                    const data = await response.json().catch(() => ({}));
                    if (!response.ok) throw new Error(data.message || 'Löschen fehlgeschlagen');
                    setManagerStatus(`Datei gelöscht: ${name}`);
                    await loadFileManagerEntries(server, activeManagerPath || '');
                } catch (error) {
                    setManagerStatus(error.message || 'Löschen fehlgeschlagen.', true);
                } finally {
                    button.disabled = false;
                }
            });
        });

        entriesContainer.appendChild(list);
    } catch (error) {
        setManagerStatus(error.message || 'Ordner konnte nicht geladen werden.', true);
    }
}

function uploadFileWithProgress(serverId, targetPath, file) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${SERVER_API_URL}/${serverId}/files?path=${encodeURIComponent(targetPath || '')}`);
        xhr.withCredentials = true;
        xhr.setRequestHeader('Content-Type', 'application/octet-stream');
        xhr.setRequestHeader('X-File-Name', file.name);
        xhr.setRequestHeader('X-Remote-Path', targetPath || '');

        xhr.upload.addEventListener('progress', (event) => {
            if (!event.lengthComputable) {
                setUploadProgress('Upload läuft...', 35);
                return;
            }

            const percent = Math.round((event.loaded / event.total) * 100);
            setUploadProgress(`Upload läuft: ${percent}%`, percent);
        });

        xhr.addEventListener('load', () => {
            let data = {};
            try {
                data = JSON.parse(xhr.responseText || '{}');
            } catch (error) {
                data = {};
            }

            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(data);
                return;
            }

            reject(new Error(data.message || 'Upload fehlgeschlagen'));
        });

        xhr.addEventListener('error', () => reject(new Error('Upload fehlgeschlagen')));
        xhr.addEventListener('abort', () => reject(new Error('Upload abgebrochen')));
        xhr.send(file);
    });
}

async function handleFileUpload(event) {
    event.preventDefault();
    if (!activeServer) {
        setManagerStatus('Kein Server ausgewählt.', true);
        return;
    }

    const input = document.getElementById('file-manager-file-input');
    const file = input?.files?.[0];

    if (!file) {
        setManagerStatus('Bitte wähle zuerst eine Datei aus.', true);
        return;
    }

    setUploadProgress(`Upload wird vorbereitet...`, 5);
    const submitButton = event.currentTarget?.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }
    try {
        await uploadFileWithProgress(activeServer.id, activeManagerPath || '', file);
        setUploadProgress(`Upload abgeschlossen: ${file.name}`, 100);
        setManagerStatus(`Datei hochgeladen: ${file.name}`);
        input.value = '';
        await loadFileManagerEntries(activeServer, activeManagerPath || '');
    } catch (error) {
        setUploadProgress('Upload fehlgeschlagen', 0);
        setManagerStatus(error.message || 'Upload fehlgeschlagen.', true);
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
}

function closeFileManager() {
    const modal = getManagerModal();
    if (modal) {
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
    }
    activeServer = null;
    activeManagerPath = '';
    setUploadProgress('Bereit', 0);
}

function bindFileManagerEvents() {
    const form = document.getElementById('file-manager-upload-form');
    const closeButton = document.getElementById('close-file-manager-button');
    const modal = getManagerModal();

    if (form) {
        form.addEventListener('submit', handleFileUpload);
    }
    const fileInput = document.getElementById('file-manager-file-input');
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            const file = fileInput.files?.[0];
            setUploadProgress(file ? `Ausgewählt: ${file.name}` : 'Bereit', 0);
            setManagerStatus('');
        });
    }
    if (closeButton) {
        closeButton.addEventListener('click', closeFileManager);
    }
    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeFileManager();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    bindFileManagerEvents();
    loadServers();
});
