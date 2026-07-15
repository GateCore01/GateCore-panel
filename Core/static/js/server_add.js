document
.getElementById("serverForm")
.addEventListener("submit", async function(e){

    e.preventDefault();

    const data = {

        hostname:
            document.getElementById("hostname").value,

        ip:
            document.getElementById("ip").value,

        username:
            document.getElementById("username").value,

        password:
            document.getElementById("password").value

    };

    const response = await fetch("/api/server/add",{

        method:"POST",

        credentials:"include",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify(data)

    });

    const result = await response.json();

    alert(result.message);

    if(result.success){

        window.location="/panel/server";

    }

});