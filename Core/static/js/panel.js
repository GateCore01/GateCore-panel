async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: "include",
        ...options
    });
    if (!response.ok) {
        throw new Error(`HTTP ${response.status} für ${url}`);
    }
    return response.json();
}

// Ladeanimation für Karten
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div class="loading-spinner"></div>`;
    }
}

function formatPercent(value) {
    if (!Number.isFinite(value)) return "0%";
    return `${Math.max(0, Math.min(100, value)).toFixed(0)}%`;
}

function renderStatusList(items) {
    const container = document.getElementById("lxc-status-list");
    if (!container) return;
    if (!items.length) {
        container.innerHTML = '<div class="empty-state" data-i18n="dashboard.no_containers">Keine Container vorhanden.</div>';
        translatePage();
        return;
    }
    container.innerHTML = items.slice(0, 6).map(item => {
        const statusClass = item.status?.toLowerCase() === "running" ? "online" : "offline";
        return `
            <div class="status-item">
                <div>
                    <strong>${item.name || "Unbekannt"}</strong>
                    <div class="status-subtitle">${item.server || "Server"} • ${item.ip || "Keine IP"}</div>
                </div>
                <span class="status-badge ${statusClass}">${item.status || "Unbekannt"}</span>
            </div>
        `;
    }).join("");
    translatePage();
}

function renderMiniList(listId, items, label = "name") {
    const container = document.getElementById(listId);
    if (!container) return;
    if (!items.length) {
        container.innerHTML = '<div class="empty-state" data-i18n="dashboard.no_entries">Keine Einträge vorhanden.</div>';
        translatePage();
        return;
    }
    container.innerHTML = items.slice(0, 6).map(item =>
        `<div class="mini-item"><span>${item[label] || "Unbekannt"}</span><span class="mini-chip">${item.meta || "OK"}</span></div>`
    ).join("");
    translatePage();
}

async function loadDashboard() {
    // Ladeanimation für die Karten
    showLoading("lxc-status-list");
    showLoading("server-list");
    showLoading("storage-list");

    try {
        const [userResult, lxcResult, serverResult, usersResult, storageResult] = await Promise.all([
            fetchJson("/api/user").catch(() => null),
            fetchJson("/api/lxc/list").catch(() => []),
            fetchJson("/api/server/list").catch(() => []),
            fetchJson("/api/users/list").catch(() => []),
            fetchJson("/api/storage/list").catch(() => [])
        ]);

        const user = userResult || {};
        const lxcList = Array.isArray(lxcResult) ? lxcResult : [];
        const serverList = Array.isArray(serverResult) ? serverResult : [];
        const usersList = Array.isArray(usersResult) ? usersResult : [];
        const storageList = Array.isArray(storageResult) ? storageResult : [];

        const lxcCount = lxcList.length;
        const runningContainers = lxcList.filter(item => String(item.status || "").toLowerCase() === "running").length;

        const cpuValues = lxcList.map(item => Number(item.cpu)).filter(v => Number.isFinite(v));
        const ramValues = lxcList.map(item => Number(item.ram)).filter(v => Number.isFinite(v));
        const averageCpu = cpuValues.length ? cpuValues.reduce((a,b) => a+b, 0) / cpuValues.length : 0;
        const averageRam = ramValues.length ? ramValues.reduce((a,b) => a+b, 0) / ramValues.length : 0;

        // Benutzername mit i18n-Parameter setzen
        const welcomeEl = document.getElementById("dashboard-user");
        if (welcomeEl) {
            welcomeEl.dataset.i18nParams = JSON.stringify({ username: user?.username || "Admin" });
            welcomeEl.setAttribute("data-i18n", "dashboard.welcome");
        }

        document.getElementById("lxc-count").textContent = lxcCount;
        document.getElementById("lxc-status-meta").textContent = `${runningContainers} aktiv`;
        document.getElementById("server-count").textContent = serverList.length;
        document.getElementById("users-count").textContent = usersList.length;
        document.getElementById("storage-count").textContent = storageList.length;
        document.getElementById("cpu-usage").textContent = formatPercent(averageCpu);
        document.getElementById("ram-usage").textContent = formatPercent(averageRam);
        document.getElementById("updated-time").textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        renderStatusList(lxcList);
        renderMiniList("server-list", serverList.map(s => ({ name: s.name || s.host || "Server", meta: `${s.host || "-"}:${s.port || "-"}` })));
        renderMiniList("storage-list", storageList.map(p => ({ name: p.pool || p.name || "Pool", meta: p.filesystem || "Dateisystem" })));

        // Übersetzung für die gesamte Seite anwenden
        translatePage();

    } catch (error) {
        console.error("Dashboard-Ladefehler:", error);
        const statusList = document.getElementById("lxc-status-list");
        if (statusList) {
            statusList.innerHTML = '<div class="empty-state" data-i18n="dashboard.load_error">Dashboard konnte nicht geladen werden.</div>';
            translatePage();
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const refreshButton = document.getElementById("refreshDashboardButton");
    if (refreshButton) {
        refreshButton.addEventListener("click", () => {
            refreshButton.disabled = true;
            refreshButton.textContent = "⟳";
            loadDashboard().finally(() => {
                refreshButton.disabled = false;
                refreshButton.textContent = "Aktualisieren";
            });
        });
    }
    loadDashboard();
    setInterval(loadDashboard, 10000);
});