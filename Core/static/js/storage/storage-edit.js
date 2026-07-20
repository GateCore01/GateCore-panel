document.addEventListener("DOMContentLoaded", () => {
    loadPool();
});

function getPool() {
    const params = new URLSearchParams(window.location.search);
    return params.get("pool");
}

async function loadPool() {
    const pool = getPool();
    if (!pool) {
        document.getElementById("status").innerHTML = "Kein Pool ausgewählt.";
        return;
    }
    try {
        const response = await fetch("/api/storage/details/" + encodeURIComponent(pool));
        const data = await response.json();
        fillForm(data);
        translatePage();
    } catch (error) {
        console.error(error);
        document.getElementById("status").innerHTML = "Pool konnte nicht geladen werden.";
    }
}

function fillForm(data) {
    setValue("poolname", data.name);
    setValue("compression", data.compression);
    setValue("atime", data.atime);
    setValue("autotrim", data.autotrim);
    setValue("comment", data.comment);
    setText("infoName", data.name);
    setText("infoType", data.type);
    setText("infoSize", data.size);
    setText("infoUsed", data.used);
    setText("infoFree", data.free);
    setText("infoUsage", data.usage + " %");
    setText("infoState", data.status);
    setText("infoHealth", data.health);
}

function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value ?? "";
}
function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "-";
}

document.getElementById("editPoolForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.submitter;
    button.disabled = true;
    button.innerHTML = "Speichere...";
    const data = {
        name: getPool(),
        new_name: document.getElementById("poolname").value,
        compression: document.getElementById("compression").value,
        atime: document.getElementById("atime").value,
        autotrim: document.getElementById("autotrim").value,
        comment: document.getElementById("comment").value
    };
    try {
        const response = await fetch("/api/storage/update", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        document.getElementById("status").className = result.success ? "status-success" : "status-error";
        document.getElementById("status").innerHTML = result.message;
        if (result.success) loadPool();
    } catch (error) {
        document.getElementById("status").className = "status-error";
        document.getElementById("status").innerHTML = "Server nicht erreichbar.";
    }
    button.disabled = false;
    button.innerHTML = "Speichern";
});

document.getElementById("scrubButton")?.addEventListener("click", () => {
    window.location = "/panel/storage/scrub?pool=" + encodeURIComponent(getPool());
});
document.getElementById("exportButton")?.addEventListener("click", async () => {
    if (!confirm("Pool exportieren?")) return;
    const response = await fetch("/api/storage/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool: getPool() })
    });
    const result = await response.json();
    alert(result.message);
});
document.getElementById("destroyButton")?.addEventListener("click", async () => {
    if (!confirm("Pool wirklich löschen?")) return;
    const response = await fetch("/api/storage/delete/" + encodeURIComponent(getPool()), { method: "DELETE" });
    const result = await response.json();
    alert(result.message);
    if (result.success) window.location = "/panel/storage";
});