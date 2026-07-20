document.addEventListener("DOMContentLoaded", () => {
    loadSMART();
});

function getDisk() {
    const params = new URLSearchParams(window.location.search);
    return params.get("disk");
}

async function loadSMART() {
    const disk = getDisk();
    if (!disk) {
        document.getElementById("status").innerHTML = "Kein Laufwerk ausgewählt.";
        return;
    }
    try {
        const response = await fetch("/api/storage/smart/" + encodeURIComponent(disk));
        const data = await response.json();
        fillGeneral(data);
        fillHealth(data);
        fillAttributes(data.attributes);
        fillTests(data.tests);
        translatePage();
    } catch (error) {
        console.error(error);
        document.getElementById("status").innerHTML = "SMART-Daten konnten nicht geladen werden.";
    }
}

function fillGeneral(data) {
    setText("serverName", data.server);
    setText("deviceName", data.device);
    setText("deviceModel", data.model);
    setText("serialNumber", data.serial);
    setText("firmwareVersion", data.firmware);
    setText("deviceSize", data.capacity);
    setText("deviceType", data.type);
    setText("smartStatus", data.smart_status);
}

function fillHealth(data) {
    setText("temperature", data.temperature + " °C");
    setText("lifeRemaining", data.remaining_life);
    setText("powerOnHours", data.power_on_hours);
    setText("powerCycles", data.power_cycles);
    setText("hostWrites", data.host_writes);
    setText("hostReads", data.host_reads);
    setText("wearLevel", data.wear_level);
}

function fillAttributes(attrs) {
    const tbody = document.getElementById("smartBody");
    if (!tbody) return;
    tbody.innerHTML = "";
    if (!attrs || attrs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="storage.no_smart_data">Keine SMART Daten vorhanden.</td></tr>`;
        translatePage();
        return;
    }
    attrs.forEach(attr => {
        tbody.innerHTML += `
        <tr>
            <td>${attr.id}</td>
            <td>${attr.name}</td>
            <td>${attr.current}</td>
            <td>${attr.worst}</td>
            <td>${attr.threshold}</td>
            <td>${attr.raw}</td>
        </tr>`;
    });
    translatePage();
}

function fillTests(tests) {
    const tbody = document.getElementById("testBody");
    if (!tbody) return;
    tbody.innerHTML = "";
    if (!tests || tests.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-row" data-i18n="storage.no_tests">Keine Tests vorhanden.</td></tr>`;
        translatePage();
        return;
    }
    tests.forEach(test => {
        tbody.innerHTML += `
        <tr>
            <td>${test.type}</td>
            <td>${test.status}</td>
            <td>${test.progress}</td>
            <td>${test.date}</td>
        </tr>`;
    });
    translatePage();
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "-";
}

document.getElementById("shortTest")?.addEventListener("click", () => startTest("short"));
document.getElementById("longTest")?.addEventListener("click", () => startTest("long"));
document.getElementById("abortTest")?.addEventListener("click", async () => {
    const disk = getDisk();
    const response = await fetch("/api/storage/smart/abort", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ disk })
    });
    const result = await response.json();
    alert(result.message);
    loadSMART();
});
document.getElementById("refreshSMART")?.addEventListener("click", loadSMART);

async function startTest(type) {
    const disk = getDisk();
    const response = await fetch("/api/storage/smart/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ disk, type })
    });
    const result = await response.json();
    alert(result.message);
    loadSMART();
}