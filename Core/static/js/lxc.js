// ----------------------------------------------------
// LXC laden
// ----------------------------------------------------

async function loadLXC() {

    const response = await fetch("/api/lxc/list", {
        credentials: "include"
    });

    const containers = await response.json();

    const tbody = document.getElementById("serverBody");

    tbody.innerHTML = "";

    if (containers.length === 0) {

        tbody.innerHTML = `

        <tr>

            <td colspan="8">

                Keine LXC-Container vorhanden.

            </td>

        </tr>

        `;

        return;

    }

    containers.forEach(container => {

        tbody.innerHTML += `

        <tr>

            <td>${container.id}</td>

            <td>${container.name}</td>

            <td>${container.server}</td>

            <td>${container.status}</td>

            <td>${container.ip}</td>

            <td>${container.cpu}</td>

            <td>${container.ram}</td>

            <td>

                <div class="action-buttons">

                    <button
                        class="btn-start"
                        onclick="startLXC(${container.id})">

                        Start

                    </button>

                    <button
                        class="btn-stop"
                        onclick="stopLXC(${container.id})">

                        Stop

                    </button>

                    <button
                        class="btn-restart"
                        onclick="restartLXC(${container.id})">

                        Neustart

                    </button>

                    <button
                        class="btn-console"
                        onclick="consoleLXC(${container.id})">

                        Konsole

                    </button>

                    <button
                        class="btn-delete"
                        onclick="deleteLXC(${container.id})">

                        Löschen

                    </button>

                </div>

            </td>

        </tr>

        `;

    });

}

// ----------------------------------------------------
// Start
// ----------------------------------------------------

async function startLXC(id){

    const response = await fetch(`/api/lxc/start/${id}`,{

        method:"POST",

        credentials:"include"

    });

    const result = await response.json();

    alert(result.message);

    loadLXC();

}

// ----------------------------------------------------
// Stop
// ----------------------------------------------------

async function stopLXC(id){

    const response = await fetch(`/api/lxc/stop/${id}`,{

        method:"POST",

        credentials:"include"

    });

    const result = await response.json();

    alert(result.message);

    loadLXC();

}

// ----------------------------------------------------
// Neustart
// ----------------------------------------------------

async function restartLXC(id){

    const response = await fetch(`/api/lxc/restart/${id}`,{

        method:"POST",

        credentials:"include"

    });

    const result = await response.json();

    alert(result.message);

    loadLXC();

}

// ----------------------------------------------------
// Konsole
// ----------------------------------------------------

function consoleLXC(id){

    window.location = "/panel/lxc/console/" + id;

}

// ----------------------------------------------------
// Löschen
// ----------------------------------------------------

async function deleteLXC(id){

    if(!confirm("Container wirklich löschen?")){

        return;

    }

    const response = await fetch(`/api/lxc/delete/${id}`,{

        method:"DELETE",

        credentials:"include"

    });

    const result = await response.json();

    alert(result.message);

    loadLXC();

}

// ----------------------------------------------------
// Logout
// ----------------------------------------------------

document.getElementById("logoutButton").onclick = async function(){

    await fetch("/api/logout",{

        method:"POST",

        credentials:"include"

    });

    window.location="/";

}

// ----------------------------------------------------
// Laden
// ----------------------------------------------------

loadLXC();

setInterval(loadLXC,10000);