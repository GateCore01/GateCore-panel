const form = document.getElementById("loginForm");
const dialog = document.getElementById("errorDialog");
const errorText = document.getElementById("errorText");
const closeDialog = document.getElementById("closeDialog");

closeDialog.addEventListener("click", () => dialog.close());

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        if (response.ok) {
            window.location.replace("/panel");
        } else {
            errorText.textContent = result.detail ?? "Benutzername oder Passwort ist falsch.";
            dialog.showModal();
        }
    } catch (err) {
        errorText.textContent = "Backend nicht erreichbar.";
        dialog.showModal();
    }
});