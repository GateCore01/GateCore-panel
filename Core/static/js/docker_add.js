// docker_add.js – Container erstellen
document.addEventListener('DOMContentLoaded', loadServers);

async function loadServers() {
    const select = document.getElementById('server');
    select.innerHTML = `<option data-i18n="docker.loading">Lade Server...</option>`;
    try {
        const response = await fetch('/api/server/select', { credentials: 'include' });
        const servers = await response.json();
        select.innerHTML = '';
        if (servers.length === 0) {
            select.innerHTML = `<option value="" data-i18n="docker.no_servers">Keine Server vorhanden</option>`;
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
        select.innerHTML = `<option value="" data-i18n="docker.load_error">Fehler beim Laden</option>`;
    }
}

document.getElementById('dockerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        name: document.getElementById('name').value.trim(),
        server_id: parseInt(document.getElementById('server').value),
        image: document.getElementById('image').value.trim(),
        command: document.getElementById('command').value.trim(),
        env: document.getElementById('env').value.split(',').map(s => s.trim()).filter(s => s),
        volumes: document.getElementById('volumes').value.split(',').map(s => s.trim()).filter(s => s),
        ports: document.getElementById('ports').value.split(',').map(s => s.trim()).filter(s => s),
        detach: true
    };
    const status = document.getElementById('status');
    status.innerText = 'Container wird erstellt...';
    try {
        const response = await fetch('/api/docker/container/create', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        status.innerText = result.message;
        if (response.ok) {
            setTimeout(() => window.location = '/panel/docker', 1500);
        }
    } catch (err) {
        status.innerText = 'Fehler: ' + err.message;
    }
});