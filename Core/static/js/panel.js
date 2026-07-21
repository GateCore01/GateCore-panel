// panel.js – Dashboard mit Docker-Containern statt LXC
async function loadDashboard() {
    // ... bestehende Funktion für LXC durch Docker ersetzen
    // Ersetze 'lxc-status-list' mit Docker-Containern
    try {
        const [userResult, dockerResult, serverResult, usersResult, storageResult] = await Promise.all([
            fetchJson("/api/user").catch(() => null),
            fetchJson("/api/docker/containers").catch(() => []),
            fetchJson("/api/server/list").catch(() => []),
            fetchJson("/api/users/list").catch(() => []),
            fetchJson("/api/storage/pools").catch(() => [])
        ]);

        const user = userResult || {};
        const dockerList = Array.isArray(dockerResult) ? dockerResult : [];
        const serverList = Array.isArray(serverResult) ? serverResult : [];
        const usersList = Array.isArray(usersResult) ? usersList : [];
        const storageList = Array.isArray(storageResult) ? storageResult : [];

        const containerCount = dockerList.length;
        const runningContainers = dockerList.filter(c => c.status === 'running').length;

        // ... Karten aktualisieren
        document.getElementById("lxc-count").textContent = containerCount;
        document.getElementById("lxc-status-meta").textContent = `${runningContainers} aktiv`;

        // Container-Status-Liste (ersetzt LXC)
        const statusList = document.getElementById("lxc-status-list");
        if (statusList) {
            if (dockerList.length === 0) {
                statusList.innerHTML = '<div class="empty-state" data-i18n="dashboard.no_containers">Keine Container vorhanden.</div>';
            } else {
                statusList.innerHTML = dockerList.slice(0, 6).map(c => {
                    const statusClass = c.status === 'running' ? 'online' : 'offline';
                    return `
                        <div class="status-item">
                            <div>
                                <strong>${c.name}</strong>
                                <div class="status-subtitle">${c.image} • ${c.status}</div>
                            </div>
                            <span class="status-badge ${statusClass}">${c.status}</span>
                        </div>
                    `;
                }).join('');
            }
        }

        // ... restliche Dashboard-Logik
        translatePage();
    } catch (error) {
        console.error("Dashboard-Ladefehler:", error);
    }
}