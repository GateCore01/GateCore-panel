// docker.js – Container-Verwaltung
async function loadContainers() {
    const tbody = document.getElementById('containerBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-spinner"></div></td></tr>`;

    try {
        const response = await fetch('/api/docker/containers', { credentials: 'include' });
        const containers = await response.json();
        tbody.innerHTML = '';
        if (containers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="docker.no_containers">Keine Container vorhanden.</td></tr>`;
            window.translatePage?.();
            return;
        }
        containers.forEach(c => {
            const statusClass = c.status === 'running' ? 'online' : 'offline';
            tbody.innerHTML += `
            <tr>
                <td>${c.id}</td>
                <td>${c.name}</td>
                <td>${c.image}</td>
                <td><span class="status-badge ${statusClass}">${c.status}</span></td>
                <td>${c.created}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-start" onclick="containerAction('start', ${c.id})" data-i18n="docker.start">Start</button>
                        <button class="btn-stop" onclick="containerAction('stop', ${c.id})" data-i18n="docker.stop">Stop</button>
                        <button class="btn-restart" onclick="containerAction('restart', ${c.id})" data-i18n="docker.restart">Neustart</button>
                        <button class="btn-delete" onclick="containerAction('delete', ${c.id})" data-i18n="docker.delete">Löschen</button>
                        <button class="btn-logs" onclick="viewLogs(${c.id})" data-i18n="docker.logs">Logs</button>
                    </div>
                </td>
            </tr>`;
        });
        window.translatePage?.();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Fehler beim Laden der Container.</td></tr>`;
    }
}

async function containerAction(action, id) {
    const endpoints = {
        start: 'start',
        stop: 'stop',
        restart: 'restart',
        delete: 'delete'
    };
    const method = action === 'delete' ? 'DELETE' : 'POST';
    if (action === 'delete' && !confirm('Container wirklich löschen?')) return;
    try {
        const response = await fetch(`/api/docker/container/${endpoints[action]}/${id}`, {
            method: method,
            credentials: 'include'
        });
        const result = await response.json();
        alert(result.message);
        loadContainers();
    } catch (err) {
        alert('Fehler: ' + err.message);
    }
}

async function viewLogs(id) {
    try {
        const response = await fetch(`/api/docker/container/logs/${id}?tail=200`, { credentials: 'include' });
        const data = await response.json();
        alert(data.logs || 'Keine Logs');
    } catch (err) {
        alert('Fehler beim Laden der Logs: ' + err.message);
    }
}

document.addEventListener('DOMContentLoaded', loadContainers);
setInterval(loadContainers, 15000);