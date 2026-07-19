document.addEventListener("DOMContentLoaded", async () => {
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
});