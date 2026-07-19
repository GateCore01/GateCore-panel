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

async function logout() {
    try {
        const response = await fetch("/api/logout", {
            method: "POST",
            credentials: "include"
        });

        if (response.ok) {
            window.location.replace("/");
        }
    } catch (error) {
        console.error("Logout fehlgeschlagen:", error);
    }
}

function formatPercent(value) {
    if (!Number.isFinite(value)) {
        return "0%";
    }

    return `${Math.max(0, Math.min(100, value)).toFixed(0)}%`;
}

function renderStatusList(items) {
    const container = document.getElementById("lxc-status-list");

    if (!container) {
        return;
    }

    if (!items.length) {
        container.innerHTML = '<div class="empty-state">Keine Container vorhanden.</div>';
        return;
    }

    container.innerHTML = items
        .slice(0, 6)
        .map((item) => {
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
        })
        .join("");
}

function renderMiniList(listId, items, label = "name") {
    const container = document.getElementById(listId);

    if (!container) {
        return;
    }

    if (!items.length) {
        container.innerHTML = '<div class="empty-state">Keine Einträge vorhanden.</div>';
        return;
    }

    container.innerHTML = items
        .slice(0, 6)
        .map((item) => `<div class="mini-item"><span>${item[label] || "Unbekannt"}</span><span class="mini-chip">${item.meta || "OK"}</span></div>`)
        .join("");
}

async function loadDashboard() {
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
        const runningContainers = lxcList.filter((item) => String(item.status || "").toLowerCase() === "running").length;

        const cpuValues = lxcList
            .map((item) => Number(item.cpu))
            .filter((value) => Number.isFinite(value));

        const ramValues = lxcList
            .map((item) => Number(item.ram))
            .filter((value) => Number.isFinite(value));

        const averageCpu = cpuValues.length
            ? cpuValues.reduce((sum, value) => sum + value, 0) / cpuValues.length
            : 0;

        const averageRam = ramValues.length
            ? ramValues.reduce((sum, value) => sum + value, 0) / ramValues.length
            : 0;

        document.getElementById("dashboard-user").textContent = user?.username || "Admin";
        document.getElementById("lxc-count").textContent = lxcCount;
        document.getElementById("lxc-status-meta").textContent = `${runningContainers} aktiv`;
        document.getElementById("server-count").textContent = serverList.length;
        document.getElementById("users-count").textContent = usersList.length;
        document.getElementById("storage-count").textContent = storageList.length;
        document.getElementById("cpu-usage").textContent = formatPercent(averageCpu);
        document.getElementById("ram-usage").textContent = formatPercent(averageRam);
        document.getElementById("updated-time").textContent = new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

        renderStatusList(lxcList);
        renderMiniList(
            "server-list",
            serverList.map((server) => ({
                name: server.name || server.host || "Server",
                meta: `${server.host || "-"}:${server.port || "-"}`
            })),
            "name"
        );
        renderMiniList(
            "storage-list",
            storageList.map((pool) => ({
                name: pool.pool || pool.name || "Pool",
                meta: pool.filesystem || "Dateisystem"
            })),
            "name"
        );
    } catch (error) {
        console.error("Dashboard-Ladefehler:", error);
        const statusList = document.getElementById("lxc-status-list");
        if (statusList) {
            statusList.innerHTML = '<div class="empty-state">Dashboard konnte nicht geladen werden.</div>';
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const logoutButton = document.getElementById("logoutButton");
    const refreshButton = document.getElementById("refreshDashboardButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", logout);
    }

    if (refreshButton) {
        refreshButton.addEventListener("click", () => {
            refreshButton.disabled = true;
            refreshButton.textContent = "Aktualisiert...";
            loadDashboard().finally(() => {
                refreshButton.disabled = false;
                refreshButton.textContent = "Aktualisieren";
            });
        });
    }

    loadDashboard();
    setInterval(loadDashboard, 10000);
});