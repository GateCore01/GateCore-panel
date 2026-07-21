// storage-smart.js – SMART (für BTRFS nicht zentral, nur falls über Laufwerke)
// In BTRFS ist SMART nicht direkt im Pool, sondern pro Gerät. Hier vereinfacht.
document.addEventListener('DOMContentLoaded', loadDisks);

async function loadDisks() {
    const tbody = document.getElementById('smartBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6"><div class="loading-spinner"></div></td></tr>`;
    try {
        // Wir nutzen den bestehenden /api/storage/disks-Endpunkt (der über SSH lsblk abfragt)
        const response = await fetch('/api/storage/disks', { credentials: 'include' });
        const disks = await response.json();
        tbody.innerHTML = '';
        if (disks.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-row" data-i18n="storage.no_smart_data">Keine SMART Daten.</td></tr>`;
        } else {
            disks.forEach(d => {
                tbody.innerHTML += `
                <tr>
                    <td>${d.device}</td>
                    <td>${d.model || '-'}</td>
                    <td>${d.serial || '-'}</td>
                    <td>${d.size || '-'}</td>
                    <td>${d.status || '-'}</td>
                    <td><button onclick="viewSmartDetail('${d.device}')" data-i18n="storage.details">Details</button></td>
                </tr>`;
            });
        }
        window.translatePage?.();
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Fehler beim Laden der Laufwerke.</td></tr>`;
    }
}

function viewSmartDetail(device) {
    // Optional: Navigiere zu einer Detailseite mit /panel/storage/smart?disk=...
    window.location = `/panel/storage/smart?disk=${encodeURIComponent(device)}`;
}