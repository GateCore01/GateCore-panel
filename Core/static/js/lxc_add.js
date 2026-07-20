const form = document.getElementById("lxcForm");
const statusBox = document.getElementById("status");
const logoutButton = document.getElementById("logoutButton");
const serverSelect = document.getElementById("server");
const templateSelect = document.getElementById("template");

function setStatus(message, success = true) {
    if (!statusBox) return;
    statusBox.innerText = message;
    statusBox.className = success ? "status-success" : "status-error";
}

if (logoutButton) {
    logoutButton.addEventListener("click", window.logout);
}

async function loadServers() {
    serverSelect.innerHTML = `<option data-i18n="lxc.loading">Lade Server...</option>`;
    try {
        const response = await fetch("/api/server/select", { credentials: "include" });
        const servers = await response.json();
        serverSelect.innerHTML = "";
        if (!Array.isArray(servers) || servers.length === 0) {
            serverSelect.innerHTML = `<option value="" data-i18n="lxc.no_servers">Keine Server vorhanden</option>`;
        } else {
            servers.forEach(server => {
                const option = document.createElement("option");
                option.value = String(server.id);
                option.textContent = `${server.name} (${server.id})`;
                serverSelect.appendChild(option);
            });
        }
        translatePage();
    } catch (e) {
        serverSelect.innerHTML = `<option value="" data-i18n="lxc.load_error">Fehler beim Laden</option>`;
    }
}

async function loadTemplates() {
    templateSelect.innerHTML = `<option data-i18n="lxc.loading">Lade Templates...</option>`;
    try {
        const response = await fetch("/api/lxc/templates", { credentials: "include" });
        const templates = await response.json();
        templateSelect.innerHTML = `<option value="download" data-i18n="lxc.template_download">Standard-Download</option>`;
        if (Array.isArray(templates) && templates.length > 0) {
            templates.forEach(t => {
                const opt = document.createElement("option");
                opt.value = String(t.name || "download");
                opt.textContent = String(t.name || "download");
                templateSelect.appendChild(opt);
            });
        }
        translatePage();
    } catch (e) {
        templateSelect.innerHTML = `<option value="download" data-i18n="lxc.template_download">Standard-Download</option>`;
    }
}

if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            name: document.getElementById("name").value.trim(),
            vmid: parseInt(document.getElementById("vmid").value, 10),
            server: document.getElementById("server").value,
            template: document.getElementById("template").value || "download"
        };
        if (!payload.name || Number.isNaN(payload.vmid) || !payload.server) {
            setStatus("Bitte alle Felder korrekt ausfüllen.", false);
            return;
        }
        setStatus("Container wird gespeichert...", true);
        const response = await fetch("/api/lxc/add", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await response.json().catch(() => ({ success: false, message: "Container konnte nicht gespeichert werden." }));
        setStatus(result.message || "Unbekannter Fehler.", result.success);
        if (result.success) {
            setTimeout(() => { window.location = "/panel/lxc"; }, 1000);
        }
    });
}

Promise.all([loadServers(), loadTemplates()]);