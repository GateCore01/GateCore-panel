// settings.js – Einstellungen speichern & Theme anwenden
document.addEventListener("DOMContentLoaded", function() {
    const theme = window.getCookie('gatecore_theme') || 'system';
    const language = window.getCookie('gatecore_language') || 'en';
    const animations = window.getCookie('gatecore_animations') || 'true';
    const sidebarState = window.getCookie('gatecore_sidebar') || 'expanded';

    const themeSelect = document.getElementById('theme');
    const langSelect = document.getElementById('language');
    const animSelect = document.getElementById('animations');
    const sidebarSelect = document.getElementById('sidebar');

    if (themeSelect) themeSelect.value = theme;
    if (langSelect) langSelect.value = language;
    if (animSelect) animSelect.value = animations;
    if (sidebarSelect) sidebarSelect.value = sidebarState;

    // Speichern
    document.getElementById('saveSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        const newTheme = themeSelect ? themeSelect.value : 'system';
        const newLanguage = langSelect ? langSelect.value : 'en';
        const newAnimations = animSelect ? animSelect.value : 'true';
        const newSidebar = sidebarSelect ? sidebarSelect.value : 'expanded';

        window.setCookie('gatecore_theme', newTheme);
        window.setCookie('gatecore_language', newLanguage);
        window.setCookie('gatecore_animations', newAnimations);
        window.setCookie('gatecore_sidebar', newSidebar);

        applyTheme(newTheme);
        if (window.setLanguage) window.setLanguage(newLanguage);
        alert('Settings saved!');
    });

    // Zurücksetzen
    document.getElementById('resetSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        if (themeSelect) themeSelect.value = 'system';
        if (langSelect) langSelect.value = 'en';
        if (animSelect) animSelect.value = 'true';
        if (sidebarSelect) sidebarSelect.value = 'expanded';
    });

    // Theme anwenden
    applyTheme(theme);

    // Animationen global steuern
    if (animations === 'false') {
        document.body.classList.add('no-animations');
    }

    // Sidebar-Status anwenden
    if (sidebarState === 'collapsed') {
        document.querySelector('.sidebar')?.classList.add('collapsed');
    }
});

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