// ----------------------------
// Elemente
// ----------------------------

const form = document.getElementById("userForm");
const tbody = document.getElementById("userBody");
const status = document.getElementById("userStatus");

// ----------------------------
// Benutzer laden
// ----------------------------

async function loadUsers() {

    try {

        const response = await fetch("/api/users/list", {
            credentials: "include"
        });

        const users = await response.json();

        tbody.innerHTML = "";

        if (users.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="3" class="empty-row">
                        Keine Benutzer vorhanden.
                    </td>
                </tr>
            `;

            return;

        }

        users.forEach(user => {

            tbody.innerHTML += `

            <tr>

                <td>${user.id}</td>

                <td>${user.username}</td>

                <td>

                    <div class="action-buttons">

                        <button
                            class="btn-edit"
                            onclick="changePassword(${user.id})">

                            🔑

                        </button>

                        <button
                            class="btn-delete"
                            onclick="deleteUser(${user.id})">

                            🗑️

                        </button>

                    </div>

                </td>

            </tr>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}

// ----------------------------
// Benutzer hinzufügen
// ----------------------------

form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const username = document.getElementById("username").value;

    const password = document.getElementById("password").value;

    const response = await fetch("/api/users/add", {

        method: "POST",

        credentials: "include",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            username: username,

            password: password

        })

    });

    const result = await response.json();

    status.innerText = result.message;

    if(result.success){

        form.reset();

        loadUsers();

    }

});

// ----------------------------
// Benutzer löschen
// ----------------------------

async function deleteUser(id){

    if(!confirm("Benutzer wirklich löschen?")){

        return;

    }

    const response = await fetch(

        "/api/users/delete/" + id,

        {

            method:"DELETE",

            credentials:"include"

        }

    );

    const result = await response.json();

    alert(result.message);

    loadUsers();

}

// ----------------------------
// Passwort ändern
// ----------------------------

async function changePassword(id){

    const password = prompt("Neues Passwort:");

    if(password === null){

        return;

    }

    const response = await fetch(

        "/api/users/password",

        {

            method:"PUT",

            credentials:"include",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                id:id,

                password:password

            })

        }

    );

    const result = await response.json();

    alert(result.message);

}

// ----------------------------
// Beim Laden
// ----------------------------

loadUsers();