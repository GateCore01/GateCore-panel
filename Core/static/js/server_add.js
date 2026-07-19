const form = document.getElementById("serverForm");
const statusBox = document.getElementById("status");
const testButton = document.getElementById("testButton");

function setStatus(message, success = true) {

    statusBox.innerText = message;

    if (success) {
        statusBox.className = "status-success";
    } else {
        statusBox.className = "status-error";
    }

}

async function getFormData() {

    return {

        hostname: document.getElementById("hostname").value,

        ip: document.getElementById("ip").value,

        port: parseInt(document.getElementById("port").value),

        username: document.getElementById("username").value,

        password: document.getElementById("password").value,

        private_key: document.getElementById("privateKey").value

    };

}

testButton.addEventListener("click", async () => {

    setStatus("Verbindung wird geprüft...", true);

    const response = await fetch("/api/server/test", {

        method: "POST",

        credentials: "include",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(await getFormData())

    });

    const result = await response.json();

    setStatus(result.message, result.success);

});

form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const response = await fetch("/api/server/add", {

        method: "POST",

        credentials: "include",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(await getFormData())

    });

    const result = await response.json();

    setStatus(result.message, result.success);

    if (result.success) {

        setTimeout(() => {

            window.location = "/panel/servers";

        }, 1000);

    }

});