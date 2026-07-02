const USERS_FILE = '/config/users.json';

function showUserMessage(message, isError = false) {
    const messageBox = document.getElementById('user-message');
    if (!messageBox) {
        return;
    }

    messageBox.textContent = message;
    messageBox.style.color = isError ? '#b91c1c' : '#166534';
}

async function loadUsers() {
    const response = await fetch(USERS_FILE, { credentials: 'include' });
    if (!response.ok) {
        return [];
    }
    return response.json();
}

async function saveUsers(users) {
    const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ users })
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.message || 'Fehler beim Speichern der Benutzer');
    }

    return data;
}

function renderUsers(users) {
    const tbody = document.getElementById('user-table-body');
    if (!tbody) {
        return;
    }

    tbody.innerHTML = '';
    users.forEach((user) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.username}</td>
            <td><input type="password" data-user-input="${user.username}" placeholder="Neues Passwort"></td>
            <td>
                <button type="button" data-action="set-password" data-username="${user.username}">Passwort setzen</button>
                <button type="button" data-action="delete" data-username="${user.username}">Löschen</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    tbody.querySelectorAll('button').forEach((button) => {
        button.addEventListener('click', async () => {
            const username = button.getAttribute('data-username');
            const action = button.getAttribute('data-action');
            const usersList = await loadUsers();

            if (action === 'delete') {
                const updatedUsers = usersList.filter((user) => user.username !== username);
                await saveUsers(updatedUsers);
                await refreshUsers();
                showUserMessage(`Benutzer ${username} gelöscht.`);
                return;
            }

            const passwordInput = document.querySelector(`input[data-user-input="${username}"]`);
            const password = passwordInput?.value || '';
            if (!password) {
                showUserMessage('Bitte ein Passwort eingeben.', true);
                return;
            }

            const updatedUsers = usersList.map((user) => {
                if (user.username === username) {
                    return { ...user, password };
                }
                return user;
            });

            await saveUsers(updatedUsers);
            await refreshUsers();
            showUserMessage(`Passwort für ${username} gesetzt.`);
        });
    });
}

async function refreshUsers() {
    const users = await loadUsers();
    renderUsers(users);
}

async function addUser() {
    const usernameInput = document.getElementById('new-username');
    const passwordInput = document.getElementById('new-password');
    if (!usernameInput || !passwordInput) {
        return;
    }

    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
        showUserMessage('Bitte Benutzername und Passwort angeben.', true);
        return;
    }

    const users = await loadUsers();
    if (users.some((user) => user.username === username)) {
        showUserMessage('Benutzer existiert bereits.', true);
        return;
    }

    await saveUsers([...users, { username, password }]);
    usernameInput.value = '';
    passwordInput.value = '';
    await refreshUsers();
    showUserMessage(`Benutzer ${username} erstellt.`);
}

document.addEventListener('DOMContentLoaded', async () => {
    const addButton = document.getElementById('add-user-button');
    if (addButton) {
        addButton.addEventListener('click', addUser);
    }
    await refreshUsers();
});
