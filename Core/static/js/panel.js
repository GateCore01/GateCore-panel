async function loadLXCCount() {

    try {

        const response = await fetch("/api/lxc/count", {
            credentials: "include"
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        document.getElementById("lxc-count").textContent = data.count;

    } catch (error) {
        console.error(error);
    }

}

// Wird einmal beim Laden der Seite ausgeführt
document.addEventListener("DOMContentLoaded", () => {

    loadLXCCount();

    // Alle 5 Sekunden aktualisieren
    setInterval(loadLXCCount, 5000);

});