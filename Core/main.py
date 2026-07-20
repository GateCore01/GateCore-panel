###########################################################################
# File: Core/main.py
# Main Code from GateCore Linux Server Management
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-20
# Communion: GateCore01
############################################################################
# !/bin/python

# import required modules
import asyncio
import json
import urllib.request
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import (
    cleanup_sessions,
    get_user_info,
    hash_password,
    login,
    logout,
    require_login,
)
from database import (
    get_server,
    init_database,
    lxc_connection,
    server_connection,
    storage_connection,
    user_connection,
    write_log,
    backup_connection,
    logs_connection,
)
from models import (
    AddLXC,
    AddServer,
    AddUser,
    ChangePassword,
    CreateStorage,
    SnapshotClone,
    SnapshotCreate,
    SnapshotRename,
    StorageAction,
    UpdateStorage,
)
from ssh.client import SSHClient
from ssh.lxc import create as create_lxc_container
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
# Template 
# -------------------------------------------------

# Template Repo
TEMPLATE_REPO = (
    "https://git.code.sf.net/p/gatecore-template/container-templates"
)

# Template Path
TEMPLATE_PATH = BASE_DIR / "cache" / "templates"

# -------------------------------------------------
# soucreforge Template Sync
# -------------------------------------------------
async def sync_github_templates():

    try:

        if TEMPLATE_PATH.exists():

            subprocess.run(
                ["git", "-C", str(TEMPLATE_PATH), "pull"],
                check=True,
                capture_output=True
            )

        else:

            TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)

            subprocess.run(
                [
                    "git",
                    "clone",
                    TEMPLATE_REPO,
                    str(TEMPLATE_PATH)
                ],
                check=True,
                capture_output=True
            )

    except Exception as exc:

        write_log(
            None,
            None,
            "error",
            "template_sync",
            f"Repository konnte nicht synchronisiert werden: {exc}"
        )

        return

    templates = []

    for file in TEMPLATE_PATH.rglob("*"):

        if not file.is_file():
            continue

        relative = file.relative_to(TEMPLATE_PATH)

        templates.append({

            "name": file.stem,

            "path": str(relative),

            "type": "file",

            "repo_url": TEMPLATE_REPO,

            "download_url": str(file)

        })

    conn = lxc_connection()

    cursor = conn.cursor()

    names = []

    for template in templates:

        names.append(template["name"])

        cursor.execute(
            """
            INSERT INTO lxc_templates
            (
                name,
                path,
                type,
                repo_url,
                download_url,
                last_synced
            )
            VALUES
            (?,?,?,?,?,?)

            ON CONFLICT(name)
            DO UPDATE SET

                path=excluded.path,
                type=excluded.type,
                repo_url=excluded.repo_url,
                download_url=excluded.download_url,
                last_synced=excluded.last_synced
            """,
            (
                template["name"],
                template["path"],
                template["type"],
                template["repo_url"],
                template["download_url"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

    if names:

        cursor.execute(
            f"DELETE FROM lxc_templates WHERE name NOT IN ({','.join('?' * len(names))})",
            tuple(names)
        )

    conn.commit()

    conn.close()

# -------------------------------------------------
# Template Sync Loop(24h)
# -------------------------------------------------
async def sync_github_templates_loop() -> None:
    """Hält den GitHub-Template-Sync im Hintergrund laufend auf 24 Stunden."""
    await sync_github_templates()

    while True:
        await asyncio.sleep(24 * 60 * 60)
        await sync_github_templates()


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


@app.on_event("startup")
async def start_template_sync_tasks() -> None:
    asyncio.create_task(sync_github_templates_loop())

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
    "/i18n",
    StaticFiles(directory=BASE_DIR / "static" / "i18n"),
    name="i18n"
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

# -------------------------------------------------
# Login
# -------------------------------------------------

@app.get("/")
async def login_page():
    return FileResponse(
        BASE_DIR / "templates" / "index.html"
    )


@app.get("/login")
async def login_page_alias():
    return FileResponse(
        BASE_DIR / "templates" / "index.html"
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
# Backup
# -------------------------------------------------
@app.get("/panel/backup")
async def backup_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "backup.html")

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
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-add.html")


@app.get("/panel/storage/edit")
async def storage_edit_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-edit.html")


@app.get("/panel/storage/details")
async def storage_details_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-details.html")


@app.get("/panel/storage/smart")
async def storage_smart_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-smart.html")


@app.get("/panel/storage/snapshots")
async def storage_snapshots_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-snapshots.html")


@app.get("/panel/storage/scrub")
async def storage_scrub_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-scrub.html")

# -------------------------------------------------
# API
# -------------------------------------------------

# LXC Count
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

# Server add
@app.post("/api/server/add")
async def add_server(
    data: AddServer,
    user=Depends(require_login)
):
    """Speichert einen SSH-Zugriff auf einen Remote-Server in SQLite."""
    conn = server_connection()

    try:
        conn.execute(
            """
            INSERT INTO servers
            (
                name,
                host,
                port,
                username,
                password,
                private_key
            )

            VALUES
            (?,?,?,?,?,?)
            """,
            (
                data.hostname,
                data.ip,
                data.port,
                data.username,
                data.password,
                data.private_key,
            ),
        )
        conn.commit()

        return {
            "success": True,
            "message": "Server gespeichert."
        }
    except Exception as exc:
        return {
            "success": False,
            "message": f"Server konnte nicht gespeichert werden: {exc}",
        }
    finally:
        conn.close()


# Server Test
@app.post("/api/server/test")
async def test_server_connection(
    data: AddServer,
    user=Depends(require_login)
):
    """Prüft die SSH-Verbindung für einen neu eingetragenen Server."""
    try:
        with SSHClient({
            "host": data.ip,
            "port": data.port,
            "username": data.username,
            "password": data.password,
            "private_key": data.private_key,
        }) as ssh:
            result = ssh.execute("hostname")

        if result["stderr"]:
            return {
                "success": False,
                "message": result["stderr"],
            }

        return {
            "success": True,
            "message": f"Verbindung erfolgreich. Hostname: {result['stdout']}",
        }
    except Exception as exc:
        return {
            "success": False,
            "message": f"Verbindung fehlgeschlagen: {exc}",
        }


# Test Connextion by ID
@app.post("/api/server/test/{server_id}")
async def test_server_connection_by_id(
    server_id: int,
    user=Depends(require_login)
):
    """Prüft die SSH-Verbindung für einen bereits gespeicherten Server."""
    conn = server_connection()

    try:
        row = conn.execute(
            "SELECT id, name, host, port, username, password, private_key FROM servers WHERE id=?",
            (server_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Server nicht gefunden")

        with SSHClient(dict(row)) as ssh:
            result = ssh.execute("hostname")

        if result["stderr"]:
            return {
                "success": False,
                "message": result["stderr"],
            }

        return {
            "success": True,
            "message": f"Verbindung erfolgreich. Hostname: {result['stdout']}",
        }
    except HTTPException:
        raise
    except Exception as exc:
        return {
            "success": False,
            "message": f"Verbindung fehlgeschlagen: {exc}",
        }
    finally:
        conn.close()

# Server Delete 
@app.delete("/api/server/delete/{server_id}")
async def delete_server(
    server_id: int,
    user=Depends(require_login)
):
    """Löscht einen gespeicherten Server aus der SQLite-Datenbank."""
    conn = server_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM servers WHERE id=?",
            (server_id,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "Server nicht gefunden.",
            }

        return {
            "success": True,
            "message": "Server gelöscht.",
        }
    finally:
        conn.close()

# Server List 
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

# -------------------------------------------------
# Panel Seiten (Server)
# -------------------------------------------------        
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
    """Erzeugt einen Benutzer mit bcrypt-gehashtem Passwort."""
    conn = user_connection()

    try:
        hashed_password = hash_password(data.password)

        conn.execute(
            """
            INSERT INTO users
            (
                username,
                password
            )
            VALUES
            (?,?)
            """,
            (
                data.username,
                hashed_password,
            ),
        )
        conn.commit()

        return {
            "success": True,
            "message": "Benutzer erstellt.",
        }
    except Exception as exc:
        return {
            "success": False,
            "message": str(exc),
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
    """Aktualisiert das Passwort eines Benutzers mit bcrypt-Hashing."""
    conn = user_connection()

    try:
        hashed_password = hash_password(data.password)

        conn.execute(
            """
            UPDATE users
            SET password=?
            WHERE id=?
            """,
            (
                hashed_password,
                data.id,
            ),
        )
        conn.commit()

        return {
            "success": True,
            "message": "Passwort geändert.",
        }
    finally:
        conn.close()
    
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
            template,
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
            "template": row["template"],
            "status": row["status"],
            "ip": row["ip"],
            "cpu": row["cpu"],
            "ram": row["ram"]

        })

    return data

# LXC Start 
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
    
# LXC Stop
@app.post("/api/lxc/stop/{id}")
async def stop_lxc(
    id: int,
    user=Depends(require_login)
):

    return {

        "success": True,
        "message": "Container gestoppt."

    }

# LXC Restart
@app.post("/api/lxc/restart/{id}")
async def restart_lxc(
    id: int,
    user=Depends(require_login)
):

    return {

        "success": True,
        "message": "Container neugestartet."

    }
    
#LXC Restart
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
    
# LXC Add 
@app.post("/api/lxc/add")
async def add_lxc(
    data: AddLXC,
    user=Depends(require_login)
):

    server_row = get_server(int(data.server))

    if server_row is None:
        raise HTTPException(status_code=404, detail="Server nicht gefunden.")

    remote_server = {
        "host": server_row["host"],
        "port": server_row["port"],
        "username": server_row["username"],
        "password": server_row["password"],
        "private_key": server_row["private_key"],
    }

    try:
        create_result = create_lxc_container(
            remote_server,
            data.name,
            data.template,
            backing_store="dir",
        )

        if create_result.get("stderr"):
            raise RuntimeError(create_result["stderr"])
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Container konnte nicht erstellt werden: {exc}"
        ) from exc

    conn = lxc_connection()

    conn.execute("""

        INSERT INTO lxc
        (
            name,
            vmid,
            server,
            template,
            status
        )

        VALUES
        (?,?,?,?,?)

    """,(

        data.name,

        data.vmid,

        data.server,

        data.template,

        "creating"

    ))

    conn.commit()

    conn.close()

    return {

        "success": True,

        "message": "Container gespeichert."

    }

# LXC Templates
@app.get("/api/lxc/templates")
async def lxc_templates(user=Depends(require_login)):

    conn = lxc_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, path, type, repo_url, download_url
        FROM lxc_templates
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "path": row["path"],
            "type": row["type"],
            "repo_url": row["repo_url"],
            "download_url": row["download_url"],
        }
        for row in rows
    ]

# Server Select
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

# Storage add
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

# Storage List
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
    
# Storage Details 
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

# Storage Update 
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
    
# Storage Delete
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
    
# Storage Smart 
@app.get("/api/storage/smart/{disk}")
async def storage_smart(
    disk: str,
    user=Depends(require_login)
):

    return {}

# Storage Smart Attributes
@app.get("/api/storage/smart/attributes/{disk}")
async def storage_smart_attributes(
    disk: str,
    user=Depends(require_login)
):

    return []

# Storage Smart Log
@app.get("/api/storage/smart/log/{disk}")
async def storage_smart_log(
    disk: str,
    user=Depends(require_login)
):

    return {
        "log": ""
    }

# Storage Smart Test  
@app.post("/api/storage/smart/test")
async def storage_smart_test(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "SMART-Test gestartet."
    }

# Storage Scrub    
@app.get("/api/storage/scrub/{pool}")
async def storage_scrub(
    pool: str,
    user=Depends(require_login)
):

    return {}

# Storage Scrub Start
@app.post("/api/storage/scrub/start")
async def storage_scrub_start(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Scrub gestartet."
    }
    
# Storage Scrub Stop 
@app.post("/api/storage/scrub/stop")
async def storage_scrub_stop(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Scrub gestoppt."
    }
    
# Storage Snapshots
@app.get("/api/storage/snapshots/{pool}")
async def snapshot_list(
    pool: str,
    user=Depends(require_login)
):

    return []

# Storage Snapshots Create
@app.post("/api/storage/snapshot/create")
async def snapshot_create(
    data: SnapshotCreate,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot erstellt."
    }
    
# Storage Snapshots Rename
@app.put("/api/storage/snapshot/rename")
async def snapshot_rename(
    data: SnapshotRename,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot umbenannt."
    }
    
# Storage Snapshots Delete
@app.delete("/api/storage/snapshot/delete")
async def snapshot_delete(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot gelöscht."
    }
    
# Storage Snapshots Rollback
@app.post("/api/storage/snapshot/rollback")
async def snapshot_rollback(
    data: StorageAction,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Rollback erfolgreich."
    }
    
# Storage Snapshots Clone
@app.post("/api/storage/snapshot/clone")
async def snapshot_clone(
    data: SnapshotClone,
    user=Depends(require_login)
):

    return {
        "success": True,
        "message": "Snapshot geklont."
    }

# -------------------------------------------------
# Storage – Disks auflisten
# -------------------------------------------------
@app.get("/api/storage/disks")
async def storage_disks_all(user=Depends(require_login)):
    """Listet alle Festplatten aller Server auf."""
    conn = server_connection()
    servers = conn.execute("SELECT id, name, host, port, username, password, private_key FROM servers").fetchall()
    conn.close()
    
    result = []
    for server in servers:
        try:
            with SSHClient(dict(server)) as ssh:
                # lsblk im JSON-Format abfragen
                cmd = "lsblk -J -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL"
                out = ssh.execute(cmd)
                data = json.loads(out["stdout"])
                for disk in data.get("blockdevices", []):
                    result.append({
                        "server": server["name"],
                        "device": disk.get("name", ""),
                        "size": disk.get("size", ""),
                        "type": disk.get("type", ""),
                        "filesystem": disk.get("fstype", ""),
                        "mountpoint": disk.get("mountpoint", ""),
                        "model": disk.get("model", ""),
                        "serial": disk.get("serial", ""),
                        "status": "online"
                    })
        except Exception as e:
            # Server nicht erreichbar
            pass
    return result

@app.get("/api/storage/disks/{server_id}")
async def storage_disks_by_server(server_id: int, user=Depends(require_login)):
    """Listet Festplatten eines bestimmten Servers auf."""
    conn = server_connection()
    server = conn.execute(
        "SELECT id, name, host, port, username, password, private_key FROM servers WHERE id=?",
        (server_id,)
    ).fetchone()
    conn.close()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server nicht gefunden")
    
    result = []
    try:
        with SSHClient(dict(server)) as ssh:
            cmd = "lsblk -J -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL"
            out = ssh.execute(cmd)
            data = json.loads(out["stdout"])
            for disk in data.get("blockdevices", []):
                result.append({
                    "device": disk.get("name", ""),
                    "size": disk.get("size", ""),
                    "type": disk.get("type", ""),
                    "filesystem": disk.get("fstype", ""),
                    "mountpoint": disk.get("mountpoint", ""),
                    "model": disk.get("model", ""),
                    "serial": disk.get("serial", ""),
                    "status": "online"
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Festplatten: {e}")
    
    return result

# -------------------------------------------------
# Backup-API
# -------------------------------------------------
@app.get("/api/backup/list")
async def backup_list(user=Depends(require_login)):
    """Listet alle vorhandenen Backups auf – mit Server-Namen aus server.db."""
    conn_b = backup_connection()
    conn_s = server_connection()
    
    try:
        # Alle Backups laden
        backups = conn_b.execute("SELECT * FROM backups ORDER BY created DESC").fetchall()
        
        # Server-Namen nachladen (separat, da in anderer DB)
        result = []
        for backup in backups:
            server = conn_s.execute(
                "SELECT name FROM servers WHERE id = ?",
                (backup["server_id"],)
            ).fetchone()
            
            result.append({
                "id": backup["id"],
                "name": backup["name"],
                "server": server["name"] if server else "Unbekannt",
                "path": backup["path"],
                "size": backup["size"] or "-",
                "status": backup["status"],
                "date": backup["created"]
            })
        
        return result
    finally:
        conn_b.close()
        conn_s.close()

@app.post("/api/backup/create")
async def backup_create(user=Depends(require_login)):
    """Erstellt ein neues Backup aller Server/Container."""
    conn = server_connection()
    servers = conn.execute("SELECT * FROM servers").fetchall()
    conn.close()
    
    if not servers:
        return {"success": False, "message": "Keine Server für Backups gefunden."}
    
    created = []
    errors = []
    
    for server in servers:
        try:
            backup_name = f"backup_{server['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            backup_path = f"/tmp/{backup_name}"
            
            with SSHClient(dict(server)) as ssh:
                # Backup von wichtigen Verzeichnissen
                result = ssh.execute(
                    f"sudo tar -czf {backup_path} "
                    f"/etc /var/log /home 2>/dev/null || "
                    f"echo 'Backup created with warnings'"
                )
                
                if result["stderr"] and "Backup created" not in result["stderr"]:
                    raise Exception(result["stderr"])
                
                # Größe ermitteln
                size_result = ssh.execute(f"ls -lh {backup_path} | awk '{{print $5}}'")
                size = size_result["stdout"].strip() or "unknown"
            
            # In Datenbank speichern
            conn_b = backup_connection()
            conn_b.execute(
                "INSERT INTO backups (name, server_id, path, size, status) VALUES (?, ?, ?, ?, ?)",
                (backup_name, server["id"], backup_path, size, "OK")
            )
            conn_b.commit()
            conn_b.close()
            created.append(backup_name)
            
            # Log-Eintrag
            write_log(server["name"], user.username, "INFO", "backup_create", f"Backup {backup_name} erstellt")
            
        except Exception as e:
            errors.append(f"{server['name']}: {str(e)}")
            write_log(server["name"], user.username, "ERROR", "backup_create", str(e))
    
    if created:
        return {
            "success": True,
            "message": f"{len(created)} Backups erstellt: {', '.join(created)}" + 
                      (f" (Fehler: {', '.join(errors)})" if errors else "")
        }
    else:
        return {
            "success": False,
            "message": f"Keine Backups erstellt: {', '.join(errors)}"
        }

@app.post("/api/backup/restore/{backup_id}")
async def backup_restore(backup_id: int, user=Depends(require_login)):
    """Stellt ein Backup auf dem ursprünglichen Server wieder her."""
    conn_b = backup_connection()
    backup = conn_b.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    conn_b.close()
    
    if not backup:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    
    # Server laden
    conn_s = server_connection()
    server = conn_s.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    conn_s.close()
    
    if not server:
        raise HTTPException(status_code=404, detail="Server nicht gefunden")
    
    try:
        with SSHClient(dict(server)) as ssh:
            # Prüfen ob Backup-Datei existiert
            check = ssh.execute(f"test -f {backup['path']} && echo 'exists'")
            if "exists" not in check["stdout"]:
                raise Exception(f"Backup-Datei {backup['path']} nicht gefunden")
            
            # Backup wiederherstellen (Achtung: überschreibt Systemdateien!)
            result = ssh.execute(f"sudo tar -xzf {backup['path']} -C / 2>/dev/null")
            if result["stderr"]:
                raise Exception(result["stderr"])
        
        write_log(server["name"], user.username, "INFO", "backup_restore", f"Backup {backup['name']} wiederhergestellt")
        return {"success": True, "message": f"Backup {backup['name']} erfolgreich wiederhergestellt"}
        
    except Exception as e:
        write_log(server["name"], user.username, "ERROR", "backup_restore", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/backup/delete/{backup_id}")
async def backup_delete(backup_id: int, user=Depends(require_login)):
    """Löscht ein Backup von der Festplatte und aus der Datenbank."""
    conn_b = backup_connection()
    backup = conn_b.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    
    if not backup:
        conn_b.close()
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")
    
    server_name = "Unbekannt"
    
    # Server laden (für Logging und Löschen der Datei)
    conn_s = server_connection()
    server = conn_s.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    conn_s.close()
    
    if server:
        server_name = server["name"]
        try:
            with SSHClient(dict(server)) as ssh:
                ssh.execute(f"sudo rm -f {backup['path']}")
        except Exception as e:
            # Datei existiert vielleicht nicht mehr – ignorieren
            pass
    
    # Aus Datenbank löschen
    conn_b.execute("DELETE FROM backups WHERE id=?", (backup_id,))
    conn_b.commit()
    conn_b.close()
    
    write_log(server_name, user.username, "INFO", "backup_delete", f"Backup {backup['name']} gelöscht")
    return {"success": True, "message": f"Backup {backup['name']} gelöscht"}

# -------------------------------------------------
# Logs API
# -------------------------------------------------
@app.get("/api/logs/list")
async def logs_list(
    level: str = "all",
    server: str = "all",
    user=Depends(require_login)
):
    """Gibt gefilterte Logs aus der Datenbank zurück."""
    conn = logs_connection()
    try:
        query = "SELECT * FROM logs WHERE 1=1"
        params = []
        
        if level != "all":
            query += " AND level = ?"
            params.append(level)
        
        if server != "all":
            query += " AND server = ?"
            params.append(server)
        
        query += " ORDER BY timestamp DESC LIMIT 1000"  # Begrenzung auf 1000 Einträge
        
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.delete("/api/logs/clear")
async def logs_clear(user=Depends(require_login)):
    """Löscht alle Logs aus der Datenbank."""
    conn = logs_connection()
    try:
        conn.execute("DELETE FROM logs")
        conn.commit()
        write_log(None, user.username, "INFO", "logs_clear", "Alle Logs wurden gelöscht")
        return {"success": True, "message": "Alle Logs gelöscht."}
    finally:
        conn.close()