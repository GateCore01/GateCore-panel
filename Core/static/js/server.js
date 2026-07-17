async function loadServers() {

    const response = await fetch("/api/server/list", {

        credentials: "include"

    });

    const servers = await response.json();

    const tbody = document.getElementById("serverBody");

    tbody.innerHTML = "";

    if (servers.length === 0) {

        tbody.innerHTML = `

        <tr>

            <td colspan="6" class="empty-row">

                Keine Server vorhanden.

            </td>

        </tr>

        `;

        return;

    }

    servers.forEach(server => {

        tbody.innerHTML += `

        <tr>

            <td>${server.id}</td>

            <td>${server.name}</td>

            <td>${server.host}</td>

            <td>${server.port}</td>

            <td>${server.username}</td>

            <td>

                <div class="action-buttons">

                    <button
                        class="btn-test"
                        onclick="testServer(${server.id})">

                        🔌

                    </button>

                    <button
                        class="btn-edit"
                        onclick="editServer(${server.id})">

                        ✏️

                    </button>

                    <button
                        class="btn-delete"
                        onclick="deleteServer(${server.id})">

                        🗑️

                    </button>

                </div>

            </td>

        </tr>

        `;

    });

}

async function deleteServer(id) {

    if (!confirm("Server wirklich löschen?")) {
        return;
    }

    const response = await fetch(`/api/server/delete/${id}`, {

        method: "DELETE",

        credentials: "include"

    });

    const result = await response.json();

    alert(result.message);

    loadServers();

}

async function testServer(id) {

    const response = await fetch(`/api/server/test/${id}`, {

        credentials: "include"

    });

    const result = await response.json();

    alert(result.message);

}

function editServer(id) {

    window.location = "/panel/server/edit/" + id;

}

loadServers();