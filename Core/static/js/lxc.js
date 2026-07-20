async function loadLXC() {
    const tbody = document.getElementById("serverBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="8"><div class="loading-spinner"></div></td></tr>`;

    try {
        const response = await fetch("/api/lxc/list", { credentials: "include" });
        const containers = await response.json();
        tbody.innerHTML = "";

        if (containers.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-row" data-i18n="lxc.no_containers">Keine LXC-Container vorhanden.</td></tr>`;
            translatePage();
            return;
        }

        containers.forEach(container => {
            tbody.innerHTML += `
            <tr>
                <td>${container.id}</td>
                <td>${container.name}</td>
                <td>${container.server}</td>
                <td>${container.status}</td>
                <td>${container.ip}</td>
                <td>${container.cpu}</td>
                <td>${container.ram}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-start" data-i18n="lxc.start" onclick="startLXC(${container.id})">Start</button>
                        <button class="btn-stop" data-i18n="lxc.stop" onclick="stopLXC(${container.id})">Stop</button>
                        <button class="btn-restart" data-i18n="lxc.restart" onclick="restartLXC(${container.id})">Neustart</button>
                        <button class="btn-console" data-i18n="lxc.console" onclick="consoleLXC(${container.id})">Konsole</button>
                        <button class="btn-delete" data-i18n="lxc.delete" onclick="deleteLXC(${container.id})">Löschen</button>
                    </div>
                </td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-row">Fehler beim Laden der Container.</td></tr>`;
    }
}

async function startLXC(id) {
    const response = await fetch(`/api/lxc/start/${id}`, { method: "POST", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadLXC();
}

async function stopLXC(id) {
    const response = await fetch(`/api/lxc/stop/${id}`, { method: "POST", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadLXC();
}

async function restartLXC(id) {
    const response = await fetch(`/api/lxc/restart/${id}`, { method: "POST", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadLXC();
}

function consoleLXC(id) {
    window.location = "/panel/lxc/console/" + id;
}

async function deleteLXC(id) {
    if (!confirm("Container wirklich löschen?")) return;
    const response = await fetch(`/api/lxc/delete/${id}`, { method: "DELETE", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadLXC();
}

// Logout wird über auth.js behandelt
document.addEventListener("DOMContentLoaded", loadLXC);
setInterval(loadLXC, 10000);