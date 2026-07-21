// settings.js – erweitert um Docker-Root-Verzeichnis
document.addEventListener("DOMContentLoaded", function() {
    // ... bestehende Initialisierungen ...

    // Docker-Root-Pfad
    const dockerRootInput = document.getElementById('dockerRoot');
    if (dockerRootInput) {
        const savedRoot = window.getCookie('gatecore_docker_root') || '/var/lib/docker';
        dockerRootInput.value = savedRoot;
    }

    // Speichern erweitern
    document.getElementById('saveSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        // ... bestehende Speicherung ...

        // Docker-Root speichern
        const dockerRoot = document.getElementById('dockerRoot')?.value || '/var/lib/docker';
        window.setCookie('gatecore_docker_root', dockerRoot);

        // ... restliche Logik ...
        alert('Settings saved!');
    });

    // Reset
    document.getElementById('resetSettings')?.addEventListener('click', function(e) {
        e.preventDefault();
        // ... bestehendes Reset ...
        if (dockerRootInput) dockerRootInput.value = '/var/lib/docker';
    });
});