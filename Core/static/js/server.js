async function loadServers() {
    const tbody = document.getElementById("serverBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-spinner"></div></td></tr>`;

    try {
        const response = await fetch("/api/server/list", { credentials: "include" });
        const servers = await response.json();
        tbody.innerHTML = "";
        if (servers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="server.no_servers">Keine Server vorhanden.</td></tr>`;
            translatePage();
            return;
        }
        servers.forEach(server => {
            tbody.innerHTML += `
            <tr>
                <td>${server.id}</td>
                <td>${server.name}</td>
                <td>${server.host}</td>
                <td>${server.port}</td>
                <td>${server.username}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-test" data-i18n="button.test" onclick="testServer(${server.id})">🔌</button>
                        <button class="btn-edit" data-i18n="button.edit" onclick="editServer(${server.id})">✏️</button>
                        <button class="btn-delete" data-i18n="button.delete" onclick="deleteServer(${server.id})">🗑️</button>
                    </div>
                </td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Fehler beim Laden der Server.</td></tr>`;
    }
}

async function deleteServer(id) {
    if (!confirm("Server wirklich löschen?")) return;
    const response = await fetch(`/api/server/delete/${id}`, { method: "DELETE", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadServers();
}

async function testServer(id) {
    const response = await fetch(`/api/server/test/${id}`, { method: "POST", credentials: "include" });
    const result = await response.json();
    alert(result.message);
}

function editServer(id) {
    window.location = "/panel/server/edit/" + id;
}

document.addEventListener("DOMContentLoaded", loadServers);