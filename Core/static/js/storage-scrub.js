// storage-scrub.js – BTRFS Scrub
document.addEventListener('DOMContentLoaded', loadPoolsForSelect);

async function loadPoolsForSelect() {
    const select = document.getElementById('pool');
    if (!select) return;
    select.innerHTML = `<option data-i18n="storage.loading">Lade Pools...</option>`;
    try {
        const response = await fetch('/api/storage/pools', { credentials: 'include' });
        const pools = await response.json();
        select.innerHTML = '';
        pools.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            select.appendChild(opt);
        });
        window.translatePage?.();
    } catch (e) {
        select.innerHTML = `<option value="" data-i18n="storage.load_error">Fehler beim Laden</option>`;
    }
}

document.getElementById('scrubForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const poolId = document.getElementById('pool').value;
    if (!poolId) {
        alert('Bitte wähle einen Pool.');
        return;
    }
    const status = document.getElementById('status');
    status.innerText = 'Scrub wird gestartet...';
    try {
        const response = await fetch(`/api/storage/pool/${poolId}/scrub/start`, {
            method: 'POST',
            credentials: 'include'
        });
        const result = await response.json();
        status.innerText = result.message || 'Scrub gestartet.';
        loadScrubStatus(poolId);
    } catch (err) {
        status.innerText = 'Fehler: ' + err.message;
    }
});

document.getElementById('stopScrub')?.addEventListener('click', async () => {
    const poolId = document.getElementById('pool').value;
    if (!poolId) return;
    try {
        const response = await fetch(`/api/storage/pool/${poolId}/scrub/stop`, {
            method: 'POST',
            credentials: 'include'
        });
        const result = await response.json();
        alert(result.message);
        loadScrubStatus(poolId);
    } catch (err) { alert('Fehler: ' + err.message); }
});

async function loadScrubStatus(poolId) {
    try {
        const response = await fetch(`/api/storage/pool/${poolId}/scrub/status`, { credentials: 'include' });
        const data = await response.json();
        document.getElementById('scrubState').textContent = data.status || '-';
        document.getElementById('scrubProgress').textContent = data.progress || '-';
        document.getElementById('scrubErrors').textContent = data.errors || '-';
        window.translatePage?.();
    } catch (err) {
        console.error(err);
    }
}