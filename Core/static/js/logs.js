// Server laden
async function loadServers(){

    const response = await fetch("/api/server/select",{

        credentials:"include"

    });

    const servers = await response.json();

    const select = document.getElementById("serverFilter");

    servers.forEach(server=>{

        select.innerHTML += `

            <option value="${server.id}">

                ${server.name}

            </option>

        `;

    });

}

// Logs Laden 
async function loadLogs(){

    const level = document.getElementById("logLevel").value;

    const server = document.getElementById("serverFilter").value;

    const response = await fetch(

        `/api/logs/list?level=${level}&server=${server}`,

        {

            credentials:"include"

        }

    );

    const logs = await response.json();

    // Tabelle füllen

}

// Filter anwenden
document
.getElementById("logLevel")
.addEventListener("change",loadLogs);

document
.getElementById("serverFilter")
.addEventListener("change",loadLogs);

loadServers();

loadLogs();