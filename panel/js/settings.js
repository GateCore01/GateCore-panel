let settingsConfig = null;

async function loadSettingsConfig() {
    const response = await fetch('../../config/settings-config.json');
    if (!response.ok) {
        throw new Error('Konfigurationsdatei konnte nicht geladen werden.');
    }

    settingsConfig = await response.json();
}

function buildApiEndpoints() {
    const apiBaseUrl = settingsConfig?.apiBaseUrl || '';
    return {
        settings: `${apiBaseUrl}${settingsConfig?.endpoints?.settings || '/settings'}`,
        password: `${apiBaseUrl}${settingsConfig?.endpoints?.password || '/password'}`
    };
}

let apiEndpoints = {
    settings: '/settings',
    password: '/password'
};

function collectSettingsPayload() {
    return {
        panelName: document.getElementById('panel-name').value,
        language: document.getElementById('language').value,
        emailNotifications: document.getElementById('email-notifications').checked,
        darkMode: document.getElementById('dark-mode').checked,
        autoSaveInterval: Number(document.getElementById('auto-save-interval').value || 0)
    };
}

function buildExportConfig() {
    const uiSettings = collectSettingsPayload();
    const newPassword = document.getElementById('new-password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;

    return {
        ...settingsConfig,
        uiSettings,
        securitySettings: {
            twoFactorEnabled: document.getElementById('two-factor').checked,
            passwordChangeRequested: Boolean(newPassword || passwordConfirm)
        }
    };
}

function downloadConfigFile(config) {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'settings-config.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function collectPasswordPayload() {
    const newPassword = document.getElementById('new-password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;

    if (!newPassword || newPassword !== passwordConfirm) {
        throw new Error('Passwörter stimmen nicht überein oder sind leer.');
    }

    return {
        newPassword,
        twoFactorEnabled: document.getElementById('two-factor').checked
    };
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Request failed with status ${response.status}`);
    }

    return response.json().catch(() => ({}));
}

function showStatus(message, isError = false) {
    const status = document.getElementById('settings-status');
    if (!status) {
        const container = document.createElement('div');
        container.id = 'settings-status';
        container.style.marginTop = '12px';
        container.style.fontWeight = '600';
        document.querySelector('.chart').appendChild(container);
    }

    const target = document.getElementById('settings-status');
    target.textContent = message;
    target.style.color = isError ? '#b91c1c' : '#166534';
}

async function saveSettings() {
    try {
        const payload = collectSettingsPayload();
        await postJson(apiEndpoints.settings, payload);
        const exportConfig = buildExportConfig();
        settingsConfig = exportConfig;
        downloadConfigFile(exportConfig);
        showStatus('Einstellungen erfolgreich gesendet und als JSON exportiert.');
    } catch (error) {
        showStatus(error.message || 'Fehler beim Senden der Einstellungen.', true);
    }
}

async function changePassword() {
    try {
        const payload = collectPasswordPayload();
        await postJson(apiEndpoints.password, payload);
        showStatus('Passwortänderung erfolgreich an die API gesendet.');
    } catch (error) {
        showStatus(error.message || 'Fehler beim Senden des Passworts.', true);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadSettingsConfig();
        apiEndpoints = buildApiEndpoints();
    } catch (error) {
        showStatus(error.message || 'Konfiguration konnte nicht geladen werden.', true);
    }

    const savedTheme = document.cookie.includes('gatecore_dark_mode=1');
    window.applyTheme?.(savedTheme);

    document.getElementById('save-settings-btn')?.addEventListener('click', saveSettings);
    document.getElementById('change-password-btn')?.addEventListener('click', changePassword);
    document.getElementById('dark-mode')?.addEventListener('change', (event) => window.applyTheme?.(event.target.checked));
    document.getElementById('dark-mode-toggle')?.addEventListener('click', () => window.toggleTheme?.());
});
