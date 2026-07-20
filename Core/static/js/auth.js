// auth.js – Authentifizierung, Theme & Logout
document.addEventListener("DOMContentLoaded", async () => {
    // 1. Authentifizierung prüfen
    try {
        const response = await fetch("/api/user", {
            method: "GET",
            credentials: "include"
        });
        if (!response.ok) {
            window.location.replace("/");
        }
    } catch {
        window.location.replace("/");
    }

    // 2. Theme anwenden (global)
    applyStoredTheme();

    // 3. Logout-Button verbinden
    const logoutBtn = document.getElementById("logoutButton");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", window.logout);
    }

    // 4. Auf Theme-Änderungen im System reagieren
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        applyStoredTheme();
    });
});

// Zentrale Logout-Funktion
window.logout = async function() {
    try {
        await fetch("/api/logout", {
            method: "POST",
            credentials: "include"
        });
    } catch (e) {
        console.warn("Logout-Fehler (ignoriert)");
    }
    window.location.replace("/");
};

// Theme aus Cookie anwenden
function applyStoredTheme() {
    const theme = getCookie('gatecore_theme') || 'system';
    applyTheme(theme);
}

// Theme anwenden (wie in settings.js)
function applyTheme(theme) {
    document.body.classList.remove('light-theme', 'dark-theme');
    if (theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.body.classList.add(prefersDark ? 'dark-theme' : 'light-theme');
    } else if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else if (theme === 'light') {
        document.body.classList.add('light-theme');
    }
}

// Cookie-Hilfsfunktionen (für auth.js und alle anderen)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days = 365) {
    const d = new Date();
    d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + "=" + value + ";expires=" + d.toUTCString() + ";path=/";
}