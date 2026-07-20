// logs.js – Logs laden und anzeigen
async function loadServers() {
    const select = document.getElementById("serverFilter");
    if (!select) return;
    select.innerHTML = `<option value="all" data-i18n="logs.all_servers">Alle Server</option>`;
    try {
        const response = await fetch("/api/server/select", { credentials: "include" });
        const servers = await response.json();
        servers.forEach(server => {
            select.innerHTML += `<option value="${server.id}">${server.name}</option>`;
        });
        window.translatePage?.();
    } catch (e) {
        console.error("Fehler beim Laden der Server:", e);
    }
}

async function loadLogs() {
    const tbody = document.getElementById("logsBody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-spinner"></div></td></tr>`;

    const level = document.getElementById("logLevel")?.value || "all";
    const server = document.getElementById("serverFilter")?.value || "all";

    try {
        const response = await fetch(`/api/logs/list?level=${level}&server=${server}`, {
            credentials: "include"
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const logs = await response.json();
        tbody.innerHTML = "";

        if (!logs || logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="logs.no_entries">Keine Logeinträge gefunden.</td></tr>`;
            window.translatePage?.();
            return;
        }

        logs.forEach(log => {
            const tr = document.createElement("tr");
            // Datum formatieren
            const date = new Date(log.timestamp);
            const formattedDate = date.toLocaleString();
            tr.innerHTML = `
                <td>${formattedDate}</td>
                <td>${log.server || '-'}</td>
                <td><span class="status-badge ${log.level === 'ERROR' ? 'offline' : log.level === 'WARNING' ? 'warning' : 'online'}">${log.level || 'INFO'}</span></td>
                <td>${log.username || '-'}</td>
                <td>${log.action || '-'}</td>
                <td>${log.details || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
        window.translatePage?.();
    } catch (error) {
        console.error("Fehler beim Laden der Logs:", error);
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Fehler beim Laden der Logs: ${error.message}</td></tr>`;
    }
}

// Event-Listener für Filter
document.addEventListener("DOMContentLoaded", function() {
    const logLevel = document.getElementById("logLevel");
    const serverFilter = document.getElementById("serverFilter");
    const refreshBtn = document.getElementById("refreshButton");
    const clearBtn = document.getElementById("clearButton");

    if (logLevel) logLevel.addEventListener("change", loadLogs);
    if (serverFilter) serverFilter.addEventListener("change", loadLogs);
    if (refreshBtn) refreshBtn.addEventListener("click", loadLogs);
    if (clearBtn) clearBtn.addEventListener("click", clearLogs);

    loadServers();
    loadLogs();
});

// Logs löschen (optional)
async function clearLogs() {
    if (!confirm("Alle Logs wirklich löschen?")) return;
    try {
        const response = await fetch("/api/logs/clear", {
            method: "DELETE",
            credentials: "include"
        });
        const result = await response.json();
        alert(result.message);
        loadLogs();
    } catch (e) {
        alert("Fehler beim Löschen der Logs: " + e.message);
    }
}