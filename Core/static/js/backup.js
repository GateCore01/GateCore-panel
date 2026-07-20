// backup.js – Backup-Verwaltung mit API
document.addEventListener('DOMContentLoaded', function() {
    loadBackups();
    document.getElementById('refreshBackupButton')?.addEventListener('click', loadBackups);
    document.getElementById('createBackupButton')?.addEventListener('click', createBackup);
});

async function loadBackups() {
    const tbody = document.getElementById('backupBody');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="5"><div class="loading-spinner"></div></td></tr>`;
    
    try {
        const response = await fetch('/api/backup/list', { credentials: 'include' });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const backups = await response.json();
        tbody.innerHTML = '';
        
        if (backups.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-row" data-i18n="backup.no_backups">No backups available.</td></tr>`;
            window.translatePage?.();
            return;
        }
        
        backups.forEach(backup => {
            tbody.innerHTML += `
            <tr>
                <td>${backup.name}</td>
                <td>${backup.date}</td>
                <td>${backup.size}</td>
                <td><span class="status-badge ${backup.status === 'OK' ? 'online' : 'offline'}">${backup.status}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-restore" data-id="${backup.id}" data-i18n="backup.restore">Restore</button>
                        <button class="btn-delete" data-id="${backup.id}" data-i18n="button.delete">Delete</button>
                    </div>
                </td>
            </tr>`;
        });
        
        // Event-Listener für dynamische Buttons
        document.querySelectorAll('.btn-restore').forEach(btn => {
            btn.addEventListener('click', function() { restoreBackup(this.dataset.id); });
        });
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', function() { deleteBackup(this.dataset.id); });
        });
        
        window.translatePage?.();
    } catch (error) {
        console.error('Error loading backups:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="empty-row">Error loading backups: ${error.message}</td></tr>`;
    }
}

async function createBackup() {
    if (!confirm('Backup aller Server erstellen?')) return;
    
    try {
        const response = await fetch('/api/backup/create', {
            method: 'POST',
            credentials: 'include'
        });
        const result = await response.json();
        alert(result.message || 'Backup created successfully');
        loadBackups();
    } catch (error) {
        alert('Error creating backup: ' + error.message);
    }
}

async function restoreBackup(id) {
    if (!confirm('Are you sure you want to restore this backup?')) return;
    
    try {
        const response = await fetch(`/api/backup/restore/${id}`, {
            method: 'POST',
            credentials: 'include'
        });
        const result = await response.json();
        alert(result.message);
        loadBackups();
    } catch (error) {
        alert('Error restoring backup: ' + error.message);
    }
}

async function deleteBackup(id) {
    if (!confirm('Are you sure you want to delete this backup?')) return;
    
    try {
        const response = await fetch(`/api/backup/delete/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        const result = await response.json();
        alert(result.message);
        loadBackups();
    } catch (error) {
        alert('Error deleting backup: ' + error.message);
    }
}