document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("/api/auth/check", {
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