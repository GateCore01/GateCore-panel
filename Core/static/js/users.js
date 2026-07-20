const form = document.getElementById("userForm");
const tbody = document.getElementById("userBody");
const status = document.getElementById("userStatus");

async function loadUsers() {
    tbody.innerHTML = `<tr><td colspan="3"><div class="loading-spinner"></div></td></tr>`;
    try {
        const response = await fetch("/api/users/list", { credentials: "include" });
        const users = await response.json();
        tbody.innerHTML = "";
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="empty-row" data-i18n="user.no_users">Keine Benutzer vorhanden.</td></tr>`;
            translatePage();
            return;
        }
        users.forEach(user => {
            tbody.innerHTML += `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-edit" data-i18n="user.change_password" onclick="changePassword(${user.id})">🔑</button>
                        <button class="btn-delete" data-i18n="user.delete" onclick="deleteUser(${user.id})">🗑️</button>
                    </div>
                </td>
            </tr>`;
        });
        translatePage();
    } catch (error) {
        console.error(error);
        tbody.innerHTML = `<tr><td colspan="3" class="empty-row">Fehler beim Laden der Benutzer.</td></tr>`;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const response = await fetch("/api/users/add", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    status.innerText = result.message;
    if (result.success) {
        form.reset();
        loadUsers();
    }
});

async function deleteUser(id) {
    if (!confirm("Benutzer wirklich löschen?")) return;
    const response = await fetch("/api/users/delete/" + id, { method: "DELETE", credentials: "include" });
    const result = await response.json();
    alert(result.message);
    loadUsers();
}

async function changePassword(id) {
    const password = prompt("Neues Passwort:");
    if (password === null) return;
    const response = await fetch("/api/users/password", {
        method: "PUT",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, password })
    });
    const result = await response.json();
    alert(result.message);
}

document.addEventListener("DOMContentLoaded", loadUsers);