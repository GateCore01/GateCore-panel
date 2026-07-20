document.addEventListener("DOMContentLoaded", () => {
    loadScrubData();
});

function getPool() {
    const params = new URLSearchParams(window.location.search);
    return params.get("pool");
}

async function loadScrubData() {
    const pool = getPool();
    if (!pool) {
        document.getElementById("status").innerHTML = "Kein Pool ausgewählt.";
        return;
    }
    try {
        const response = await fetch("/api/storage/scrub/" + encodeURIComponent(pool));
        const data = await response.json();
        fillScrub(data);
        translatePage();
    } catch (error) {
        console.error(error);
        document.getElementById("status").innerHTML = "Scrub-Status konnte nicht geladen werden.";
    }
}

function fillScrub(data) {
    setText("currentPool", data.pool);
    setText("scrubState", data.status);
    setText("scrubProgress", data.progress + " %");
    setText("scrubScanned", data.scanned);
    setText("scrubRemaining", data.remaining);
    setText("scrubSpeed", data.speed);
    setText("scrubEta", data.eta);
    setText("scrubErrors", data.errors);
    setText("poolHealth", data.health);
    setText("readErrors", data.read_errors);
    setText("writeErrors", data.write_errors);
    setText("checksumErrors", data.checksum_errors);
    setText("damagedBlocks", data.damaged_blocks);
    setText("lastScrub", data.last_scrub);
    setText("nextScrub", data.next_scrub);
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "-";
}

document.getElementById("scrubForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const pool = document.getElementById("pool").value;
    const response = await fetch("/api/storage/scrub/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool })
    });
    const result = await response.json();
    document.getElementById("status").innerHTML = result.message;
    if (result.success) loadScrubData();
});
document.getElementById("stopScrub")?.addEventListener("click", async () => {
    const pool = getPool();
    const response = await fetch("/api/storage/scrub/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pool })
    });
    const result = await response.json();
    alert(result.message);
    loadScrubData();
});
document.getElementById("refreshButton")?.addEventListener("click", loadScrubData);