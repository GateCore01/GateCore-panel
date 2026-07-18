from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from models import AddUser
from models import ChangePassword
from database import lxc_connection

from database import user_connection

from auth import (
    require_login,
    login,
    logout,
    get_user_info,
    cleanup_sessions
)

from database import (
    init_database,
    lxc_connection,
    server_connection
)

from fastapi import Body

from models import (
    CreateStorage,
    UpdateStorage,
    StorageAction,
    SnapshotCreate,
    SnapshotRename,
    SnapshotClone
)

from database import storage_connection

from models import AddServer, AddLXC

from ssh.system import hostname

# -------------------------------------------------
# FastAPI
# -------------------------------------------------

app = FastAPI(
    title="GateCore",
    description="GateCore Linux Server Management",
    version="0.1.0"
)

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# Datenbank initialisieren
# -------------------------------------------------

init_database()

# Abgelaufene Sessions entfernen
cleanup_sessions()

# -------------------------------------------------
# Auth API registrieren
# -------------------------------------------------

login(app)
logout(app)
get_user_info(app)

# -------------------------------------------------
# Statische Dateien
# -------------------------------------------------

app.mount(
    "/css",
    StaticFiles(directory=BASE_DIR / "static" / "css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=BASE_DIR / "static" / "js"),
    name="js"
)

app.mount(
    "/svg",
    StaticFiles(directory=BASE_DIR / "static" / "svg"),
    name="svg"
)

app.mount(
    "/images",
    StaticFiles(directory=BASE_DIR / "static" / "images"),
    name="images"
)

# -------------------------------------------------
# Login
# -------------------------------------------------

@app.get("/")
async def login_page():
    return FileResponse(
        BASE_DIR / "templates" / "login.html"
    )


@app.get("/login")
async def login_page_alias():
    return FileResponse(
        BASE_DIR / "templates" / "login.html"
    )

# -------------------------------------------------
# Dashboard
# -------------------------------------------------

@app.get("/panel")
async def panel(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "index.html"
    )


@app.get("/panel/")
async def panel_slash(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "index.html"
    )

# -------------------------------------------------
# Benutzer
# -------------------------------------------------

@app.get("/panel/users")
async def user(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "users.html"
    )

# -------------------------------------------------
# Server
# -------------------------------------------------

@app.get("/panel/server")
async def server(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "server.html"
    )

@app.get("/panel/server/add")
async def server_add(user=Depends(require_login)):

    return FileResponse(

        BASE_DIR /
        "templates/panel/server_add.html"

    )

# -------------------------------------------------
# Einstellungen
# -------------------------------------------------

@app.get("/panel/settings")
async def settings(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "settings.html"
    )

# -------------------------------------------------
# Logs
# -------------------------------------------------

@app.get("/panel/logs")
async def logs(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "logs.html"
    )

# -------------------------------------------------
# LXC Übersicht
# -------------------------------------------------

@app.get("/panel/lxc")
async def lxc(user=Depends(require_login)):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "lxc.html"
    )


# -------------------------------------------------
# LXC hinzufügen
# -------------------------------------------------

@app.get("/panel/lxc_add")
async def lxc_add(user=Depends(require_login)):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "lxc_add.html"
    )


# -------------------------------------------------
# LXC Konsole
# -------------------------------------------------

@app.get("/panel/lxc/console/{id}")
async def lxc_console(
    id: int,
    user=Depends(require_login)
):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "lxc_console.html"
    )

# -------------------------------------------------
# Storage
# -------------------------------------------------
@app.get("/panel/storage")
async def storage_page(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "storage.html"
    )


@app.get("/panel/storage/add")
async def storage_add_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-add.html")


@app.get("/panel/storage/edit")
async def storage_edit_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-edit.html")


@app.get("/panel/storage/details")
async def storage_details_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-details.html")


@app.get("/panel/storage/smart")
async def storage_smart_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-smart.html")


@app.get("/panel/storage/snapshots")
async def storage_snapshots_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-snapshots.html")


@app.get("/panel/storage/scrub")
async def storage_scrub_page(user=Depends(require_login)):
    return FileResponse("templates/panel/storage/storage-scrub.html")

# -------------------------------------------------
# API
# -------------------------------------------------

@app.get("/api/lxc/count")
async def lxc_count(user=Depends(require_login)):

    conn = lxc_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM lxc")

        count = cursor.fetchone()[0]

        return {
            "count": count
        }

    finally:
        conn.close()

@app.post("/api/server/add")
async def add_server(
    data: AddServer,
    user=Depends(require_login)
):

    conn = server_connection()

    conn.execute(
        """
        INSERT INTO servers
        (
            name,
            host,
            port,
            username
        )

        VALUES
        (?,?,?)
        """,
        (
            data.hostname,
            data.ip,
            data.port,
            data.username
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Server gespeichert."
    }

@app.get("/api/server/list")
async def list_servers(user=Depends(require_login)):

    conn = server_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                host,
                port,
                username
            FROM servers
            ORDER BY name
            """
        )

        rows = cursor.fetchall()

        servers = []

        for row in rows:

            servers.append({

                "id": row["id"],

                "name": row["name"],

                "host": row["host"],

                "port": row["port"],

                "username": row["username"]

            })

        return servers

    finally:

        conn.close()
        
@app.get("/panel/servers")
async def servers_page(user=Depends(require_login)):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "servers.html"
    )
    
@app.get("/panel/server/add")
async def server_add_page(user=Depends(require_login)):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "server_add.html"
    )

# -------------------------------------------------
# Benutzerverwaltung
# -------------------------------------------------

@app.get("/panel/users")
async def users(user=Depends(require_login)):

    return FileResponse(
        BASE_DIR / "templates" / "panel" / "users.html"
    )
    
# -------------------------------------------------
# Starten
# -------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    
# -------------------------------------------------
# Benutzer auflisten
# -------------------------------------------------

@app.get("/api/users/list")
async def user_list(user=Depends(require_login)):

    conn = user_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            id,
            username

        FROM users

        ORDER BY username

    """)

    rows = cursor.fetchall()

    conn.close()

    users = []

    for row in rows:

        users.append({

            "id": row["id"],

            "username": row["username"]

        })

    return users

# -------------------------------------------------
# Benutzer hinzufügen
# -------------------------------------------------

@app.post("/api/users/add")
async def add_user(
    data: AddUser,
    user=Depends(require_login)
):

    conn = user_connection()

    try:

        conn.execute("""

            INSERT INTO users
            (
                username,
                password
            )

            VALUES
            (?,?)

        """,(

            data.username,

            data.password

        ))

        conn.commit()

        return {

            "success":True,

            "message":"Benutzer erstellt."

        }

    except Exception as e:

        return {

            "success":False,

            "message":str(e)

        }

    finally:

        conn.close()
        
# -------------------------------------------------
# Benutzer löschen
# -------------------------------------------------

@app.delete("/api/users/delete/{user_id}")
async def delete_user(
    user_id:int,
    user=Depends(require_login)
):

    conn = user_connection()

    conn.execute(

        "DELETE FROM users WHERE id=?",

        (user_id,)

    )

    conn.commit()

    conn.close()

    return {

        "success":True,

        "message":"Benutzer gelöscht."

    }
    

# -------------------------------------------------
# Passwort ändern
# -------------------------------------------------

@app.put("/api/users/password")
async def change_password(
    data: ChangePassword,
    user=Depends(require_login)
):

    conn = user_connection()

    conn.execute(

        """

        UPDATE users

        SET password=?

        WHERE id=?

        """,

        (

            data.password,

            data.id

        )

    )

    conn.commit()

    conn.close()

    return {

        "success":True,

        "message":"Passwort geändert."

    }
    
# -------------------------------------------------
# LXC Liste
# -------------------------------------------------

@app.get("/api/lxc/list")
async def lxc_list(user=Depends(require_login)):

    conn = lxc_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            id,
            name,
            server,
            status,
            ip,
            cpu,
            ram

        FROM lxc

        ORDER BY name

    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({

            "id": row["id"],
            "name": row["name"],
            "server": row["server"],
            "status": row["status"],
            "ip": row["ip"],
            "cpu": row["cpu"],
            "ram": row["ram"]

        })

    return data

@app.post("/api/lxc/start/{id}")
async def start_lxc(
    id: int,
    user=Depends(require_login)
):

    # SSH-Befehl kommt später

    return {

        "success": True,
        "message": "Container gestartet."

    }
    
@app.post("/api/lxc/stop/{id}")
async def stop_lxc(
    id: int,
    user=Depends(require_login)
):

    return {

        "success": True,
        "message": "Container gestoppt."

    }
    
@app.post("/api/lxc/restart/{id}")
async def restart_lxc(
    id: int,
    user=Depends(require_login)
):

    return {

        "success": True,
        "message": "Container neugestartet."

    }
    
@app.delete("/api/lxc/delete/{id}")
async def delete_lxc(
    id: int,
    user=Depends(require_login)
):

    conn = lxc_connection()

    conn.execute(

        "DELETE FROM lxc WHERE id=?",

        (id,)

    )

    conn.commit()

    conn.close()

    return {

        "success": True,
        "message": "Container gelöscht."

    }
    
@app.post("/api/lxc/add")
async def add_lxc(
    data: AddLXC,
    user=Depends(require_login)
):

    conn = lxc_connection()

    conn.execute("""

        INSERT INTO lxc
        (
            name,
            vmid,
            server
        )

        VALUES
        (?,?,?)

    """,(

        data.name,

        data.vmid,

        data.server

    ))

    conn.commit()

    conn.close()

    return {

        "success": True,

        "message": "Container gespeichert."

    }
    
@app.get("/api/server/select")
async def server_select(user=Depends(require_login)):

    conn = server_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT id,name

        FROM servers

        ORDER BY name

    """)

    rows = cursor.fetchall()

    conn.close()

    return [

        {

            "id": row["id"],

            "name": row["name"]

        }

        for row in rows

    ]
    
# -------------------------------------------------
# Storage API
# -------------------------------------------------
@app.post("/api/storage/add")
async def storage_add(
    data: CreateStorage,
    user=Depends(require_login)
):

    conn = storage_connection()

    conn.execute(
        """
        INSERT INTO storage
        (
            name,
            server,
            pool,
            filesystem,
            raid,
            mountpoint
        )

        VALUES
        (?,?,?,?,?,?)
        """,
        (
            data.name,
            data.server,
            data.pool,
            data.filesystem,
            data.raid,
            data.mountpoint
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Speicher angelegt."
    }
    
@app.get("/api/storage/list")
async def storage_list(
    user=Depends(require_login)
):

    conn = storage_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM storage
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]
    
@app.get("/api/storage/details/{pool}")
async def storage_details(
    pool: str,
    user=Depends(require_login)
):

    conn = storage_connection()

    row = conn.execute(
        """
        SELECT *
        FROM storage
        WHERE pool=?
        """,
        (pool,)
    ).fetchone()

    conn.close()

    if row is None:

        return {}

    return dict(row)

@app.put("/api/storage/update")
async def storage_update(
    data: UpdateStorage,
    user=Depends(require_login)
):

    conn = storage_connection()

    conn.execute(
        """
        UPDATE storage

        SET

        name=?,
        filesystem=?,
        raid=?,
        mountpoint=?

        WHERE pool=?
        """,
        (
            data.new_name,
            data.filesystem,
            data.raid,
            data.mountpoint,
            data.name
        )
    )

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Gespeichert."
    }
    
@app.delete("/api/storage/delete/{pool}")
async def storage_delete(
    pool: str,
    user=Depends(require_login)
):

    conn = storage_connection()

    conn.execute(
        """
        DELETE FROM storage
        WHERE pool=?
        """,
        (pool,)
    )

    conn.commit()

    conn.close()

    return {
        "success": True,
        "message": "Pool gelöscht."
    }
    
@app.get("/api/storage/smart/{disk}")
async def storage_smart(
    disk: str,
    user=Depends(require_login)
):

    return {}

@app.get("/api/storage/smart/attributes/{disk}")
async def storage_smart_attributes(
    disk: str,
    user=Depends(require_login)
):

    return []

@app.get("/api/storage/smart/log/{disk}")
async def storage_smart_log(
    disk: str,
    user=Depends(require_login)
):

    return {
        "log": ""
    }
    
@app.post("/api/storage/smart/test")
async def storage_smart_test(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "SMART-Test gestartet."
    }
    
@app.get("/api/storage/scrub/{pool}")
async def storage_scrub(
    pool: str,
    user=Depends(require_login)
):

    return {}

@app.post("/api/storage/scrub/start")
async def storage_scrub_start(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Scrub gestartet."
    }
    
@app.post("/api/storage/scrub/stop")
async def storage_scrub_stop(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Scrub gestoppt."
    }
    
@app.get("/api/storage/snapshots/{pool}")
async def snapshot_list(
    pool: str,
    user=Depends(require_login)
):

    return []

@app.post("/api/storage/snapshot/create")
async def snapshot_create(
    data: SnapshotCreate,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot erstellt."
    }
    
@app.put("/api/storage/snapshot/rename")
async def snapshot_rename(
    data: SnapshotRename,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot umbenannt."
    }
    
@app.delete("/api/storage/snapshot/delete")
async def snapshot_delete(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot gelöscht."
    }
    
@app.post("/api/storage/snapshot/rollback")
async def snapshot_rollback(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Rollback erfolgreich."
    }
    
@app.post("/api/storage/snapshot/clone")
async def snapshot_clone(
    data: SnapshotClone,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot geklont."
    }