async function login() {
    const username = document.getElementById('username')?.value || '';
    const password = document.getElementById('password')?.value || '';

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok && data.success) {
            window.location.href = '/panel.html';
        } else {
            alert(data.message || 'Login fehlgeschlagen.');
        }
    } catch (error) {
        alert(error.message || 'Login fehlgeschlagen.');
    }
}

async function isAuthenticated() {
    try {
        const response = await fetch('/api/auth/check', { credentials: 'include' });
        const data = await response.json();
        return Boolean(data.authenticated);
    } catch (error) {
        return false;
    }
}

async function requireAuth() {
    if (!await isAuthenticated()) {
        window.location.href = '/index.html';
    }
}

async function logout() {
    await fetch('/api/logout', { credentials: 'include' });
    window.location.href = '/index.html';
}

function attachLogoutButton() {
    const topbar = document.querySelector('.topbar');
    if (!topbar || document.getElementById('global-logout-button')) {
        return;
    }

    const button = document.createElement('button');
    button.id = 'global-logout-button';
    button.type = 'button';
    button.textContent = 'Logout';
    button.style.marginLeft = 'auto';
    button.style.marginRight = '12px';
    button.addEventListener('click', () => logout());

    const userElement = topbar.querySelector('.user');
    if (userElement) {
        topbar.insertBefore(button, userElement.nextSibling);
    } else {
        topbar.appendChild(button);
    }
}

async function guardPanelNavigation(targetUrl) {
    const authenticated = await isAuthenticated();
    if (!authenticated) {
        window.location.href = '/index.html';
        return;
    }
    window.location.href = targetUrl;
}

window.guardPanelNavigation = guardPanelNavigation;
window.addEventListener('DOMContentLoaded', attachLogoutButton);
