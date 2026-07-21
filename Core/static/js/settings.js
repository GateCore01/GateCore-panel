// settings.js – Einstellungen speichern & Theme anwenden
document.addEventListener("DOMContentLoaded", function() {
    const themeSelect = document.getElementById('theme');
    const langSelect = document.getElementById('language');
    const animSelect = document.getElementById('animations');
    const sidebarSelect = document.getElementById('sidebar');

    // ---- Sprach-Dropdown dynamisch befüllen ----
    if (langSelect && window.LANGUAGES) {
        const currentLang = window.getCookie('gatecore_language') || 'en';
        langSelect.innerHTML = '';
        for (const [code, name] of Object.entries(window.LANGUAGES)) {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            if (code === currentLang) {
                option.selected = true;
            }
            langSelect.appendChild(option);
        }
    }

    // ---- Gespeicherte Werte laden ----
    const theme = window.getCookie('gatecore_theme') || 'system';
    const language = window.getCookie('gatecore_language') || 'en';
    const animations = window.getCookie('gatecore_animations') || 'true';
    const sidebarState = window.getCookie('gatecore_sidebar') || 'expanded';

    if (themeSelect) themeSelect.value = theme;
    if (langSelect) langSelect.value = language;
    if (animSelect) animSelect.value = animations;
    if (sidebarSelect) sidebarSelect.value = sidebarState;

    // ---- Speichern ----
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
        
        // Animationen global steuern
        if (newAnimations === 'false') {
            document.body.classList.add('no-animations');
        } else {
            document.body.classList.remove('no-animations');
        }

        // Sidebar-Status
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            if (newSidebar === 'collapsed') {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        }

        alert('Settings saved!');
    });

        // Reset
    document.getElementById('resetSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        // ... bestehendes Reset ...
        if (dockerRootInput) dockerRootInput.value = '/var/lib/docker';
    });

    // ---- Zurücksetzen ----
    document.getElementById('resetSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        if (themeSelect) themeSelect.value = 'system';
        if (langSelect) {
            // Standardmäßig Englisch
            for (const opt of langSelect.options) {
                if (opt.value === 'en') {
                    opt.selected = true;
                    break;
                }
            }
        }
        if (animSelect) animSelect.value = 'true';
        if (sidebarSelect) sidebarSelect.value = 'expanded';
    });

    // ---- Theme anwenden ----
    applyTheme(theme);

    // ---- Animationen global ----
    if (animations === 'false') {
        document.body.classList.add('no-animations');
    }

    // ---- Sidebar-Status ----
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