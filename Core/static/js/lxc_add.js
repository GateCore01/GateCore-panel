const form = document.getElementById("lxcForm");
const statusBox = document.getElementById("status");
const logoutButton = document.getElementById("logoutButton");
const serverSelect = document.getElementById("server");
const templateSelect = document.getElementById("template");

function setStatus(message, success = true) {
    if (!statusBox) {
        return;
    }

    statusBox.innerText = message;
    statusBox.className = success ? "status-success" : "status-error";
}

if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
        await fetch("/api/logout", {
            method: "POST",
            credentials: "include"
        });

        window.location.replace("/");
    });
}

async function loadServers() {
    const response = await fetch("/api/server/select", {
        credentials: "include"
    });

    const servers = await response.json();

    if (!serverSelect) {
        return;
    }

    serverSelect.innerHTML = "";

    if (!Array.isArray(servers) || servers.length === 0) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Keine Server vorhanden";
        serverSelect.appendChild(option);
        return;
    }

    servers.forEach((server) => {
        const option = document.createElement("option");
        option.value = String(server.id);
        option.textContent = `${server.name} (${server.id})`;
        serverSelect.appendChild(option);
    });
}

async function loadTemplates() {
    const response = await fetch("/api/lxc/templates", {
        credentials: "include"
    });

    const templates = await response.json();

    if (!templateSelect) {
        return;
    }

    templateSelect.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "download";
    defaultOption.textContent = "Standard-Download";
    templateSelect.appendChild(defaultOption);

    if (!Array.isArray(templates) || templates.length === 0) {
        setStatus("Keine GitHub-Templates gefunden. Es wird der Standard-Download verwendet.", true);
        return;
    }

    templates.forEach((template) => {
        const option = document.createElement("option");
        option.value = String(template.name || "download");
        option.textContent = String(template.name || "download");
        templateSelect.appendChild(option);
    });
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
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json().catch(() => ({
            success: false,
            message: "Container konnte nicht gespeichert werden."
        }));

        setStatus(result.message || "Unbekannter Fehler.", result.success);

        if (result.success) {
            setTimeout(() => {
                window.location = "/panel/lxc";
            }, 1000);
        }
    });
}

Promise.all([
    loadServers(),
    loadTemplates()
]);
