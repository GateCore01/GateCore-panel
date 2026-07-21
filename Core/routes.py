###########################################################################
# File: Core/routes.py
# Alle Routen (Seiten & API) für GateCore
# - Jetzt synchron (def) → keine Thread-Probleme mit SQLite
# - Nutzt Dependency Injection für DB-Verbindungen
# - Einheitliche Fehlerbehandlung mit HTTPExceptions
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-20
# Communion: GateCore01
############################################################################

import sqlite3
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from auth import require_login, hash_password
from database import (
    get_server,
    get_server_db,
    get_user_db,
    get_lxc_db,
    get_storage_db,
    get_backup_db,
    get_logs_db,
    write_log,
)
from models import (
    AddLXC,
    AddServer,
    AddUser,
    ChangePassword,
    CreateStorage,
    UpdateStorage,
    StorageAction,
    SnapshotCreate,
    SnapshotRename,
    SnapshotClone,
)
from ssh.client import SSHClient
from ssh.lxc import create as create_lxc_container

BASE_DIR = Path(__file__).resolve().parent
router = APIRouter()


# =====================================================
# SEITEN-ROUTEN (HTML)
# =====================================================

@router.get("/")
def login_page():
    return FileResponse(BASE_DIR / "templates" / "index.html")

@router.get("/login")
def login_page_alias():
    return FileResponse(BASE_DIR / "templates" / "index.html")

@router.get("/panel")
def panel(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "index.html")

@router.get("/panel/")
def panel_slash(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "index.html")

@router.get("/panel/backup")
def backup_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "backup.html")

@router.get("/panel/users")
def user_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "users.html")

@router.get("/panel/servers")
def server_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "servers.html")

@router.get("/panel/server_add")
def server_add_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "server_add.html")

@router.get("/panel/settings")
def settings_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "settings.html")

@router.get("/panel/logs")
def logs_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "logs.html")

@router.get("/panel/lxc")
def lxc_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "lxc.html")

@router.get("/panel/lxc_add")
def lxc_add_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "lxc_add.html")

@router.get("/panel/lxc/console/{id}")
def lxc_console_page(id: int, user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "lxc_console.html")

@router.get("/panel/storage")
def storage_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage.html")

@router.get("/panel/storage/add")
def storage_add_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-add.html")

@router.get("/panel/storage/edit")
def storage_edit_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-edit.html")

@router.get("/panel/storage/details")
def storage_details_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-details.html")

@router.get("/panel/storage/smart")
def storage_smart_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-smart.html")

@router.get("/panel/storage/snapshots")
def storage_snapshots_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-snapshots.html")

@router.get("/panel/storage/scrub")
def storage_scrub_page(user=Depends(require_login)):
    return FileResponse(BASE_DIR / "templates" / "panel" / "storage" / "storage-scrub.html")


# =====================================================
# API-ROUTEN – LXC
# =====================================================

@router.get("/api/lxc/count")
def lxc_count(
    user=Depends(require_login),
    conn=Depends(get_lxc_db)
):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lxc")
    count = cursor.fetchone()[0]
    return {"count": count}


@router.get("/api/lxc/list")
def lxc_list(
    user=Depends(require_login),
    conn=Depends(get_lxc_db)
):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, server, template, status, ip, cpu, ram FROM lxc ORDER BY name"
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@router.post("/api/lxc/start/{id}")
def start_lxc(id: int, user=Depends(require_login)):
    # Platzhalter – später SSH-Befehl
    return {"message": "Container gestartet."}


@router.post("/api/lxc/stop/{id}")
def stop_lxc(id: int, user=Depends(require_login)):
    return {"message": "Container gestoppt."}


@router.post("/api/lxc/restart/{id}")
def restart_lxc(id: int, user=Depends(require_login)):
    return {"message": "Container neugestartet."}


@router.delete("/api/lxc/delete/{id}")
def delete_lxc(
    id: int,
    user=Depends(require_login),
    conn=Depends(get_lxc_db)
):
    conn.execute("DELETE FROM lxc WHERE id=?", (id,))
    conn.commit()
    return {"message": "Container gelöscht."}


@router.post("/api/lxc/add")
def add_lxc(
    data: AddLXC,
    user=Depends(require_login),
    conn=Depends(get_lxc_db)
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
        )

    conn.execute(
        "INSERT INTO lxc (name, vmid, server, template, status) VALUES (?,?,?,?,?)",
        (data.name, data.vmid, data.server, data.template, "creating")
    )
    conn.commit()
    return {"message": "Container gespeichert."}


@router.get("/api/lxc/templates")
def lxc_templates(
    user=Depends(require_login),
    conn=Depends(get_lxc_db)
):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, path, type, repo_url, download_url FROM lxc_templates ORDER BY name"
    )
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


# =====================================================
# API-ROUTEN – SERVER
# =====================================================

@router.post("/api/server/add")
def add_server(
    data: AddServer,
    user=Depends(require_login),
    conn=Depends(get_server_db)
):
    try:
        conn.execute(
            """
            INSERT INTO servers (name, host, port, username, password, private_key)
            VALUES (?,?,?,?,?,?)
            """,
            (data.hostname, data.ip, data.port, data.username, data.password, data.private_key),
        )
        conn.commit()
        return {"message": "Server gespeichert."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Servername existiert bereits.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Server konnte nicht gespeichert werden: {exc}")


@router.post("/api/server/test")
def test_server_connection(data: AddServer, user=Depends(require_login)):
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
            raise HTTPException(status_code=400, detail=result["stderr"])
        return {"message": f"Verbindung erfolgreich. Hostname: {result['stdout']}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verbindung fehlgeschlagen: {exc}")


@router.post("/api/server/test/{server_id}")
def test_server_connection_by_id(
    server_id: int,
    user=Depends(require_login),
    conn=Depends(get_server_db)
):
    row = conn.execute(
        "SELECT id, name, host, port, username, password, private_key FROM servers WHERE id=?",
        (server_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Server nicht gefunden")

    try:
        with SSHClient(dict(row)) as ssh:
            result = ssh.execute("hostname")
        if result["stderr"]:
            raise HTTPException(status_code=400, detail=result["stderr"])
        return {"message": f"Verbindung erfolgreich. Hostname: {result['stdout']}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verbindung fehlgeschlagen: {exc}")


@router.delete("/api/server/delete/{server_id}")
def delete_server(
    server_id: int,
    user=Depends(require_login),
    conn=Depends(get_server_db)
):
    cursor = conn.execute("DELETE FROM servers WHERE id=?", (server_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Server nicht gefunden.")
    return {"message": "Server gelöscht."}


@router.get("/api/server/list")
def list_servers(
    user=Depends(require_login),
    conn=Depends(get_server_db)
):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, host, port, username FROM servers ORDER BY name")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@router.get("/api/server/select")
def server_select(
    user=Depends(require_login),
    conn=Depends(get_server_db)
):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM servers ORDER BY name")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


# =====================================================
# API-ROUTEN – BENUTZER
# =====================================================

@router.get("/api/users/list")
def user_list(
    user=Depends(require_login),
    conn=Depends(get_user_db)
):
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users ORDER BY username")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


@router.post("/api/users/add")
def add_user(
    data: AddUser,
    user=Depends(require_login),
    conn=Depends(get_user_db)
):
    try:
        hashed_password = hash_password(data.password)
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (data.username, hashed_password),
        )
        conn.commit()
        return {"message": "Benutzer erstellt."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Benutzername existiert bereits.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/api/users/delete/{user_id}")
def delete_user(
    user_id: int,
    user=Depends(require_login),
    conn=Depends(get_user_db)
):
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return {"message": "Benutzer gelöscht."}


@router.put("/api/users/password")
def change_password(
    data: ChangePassword,
    user=Depends(require_login),
    conn=Depends(get_user_db)
):
    try:
        hashed_password = hash_password(data.password)
        conn.execute(
            "UPDATE users SET password=? WHERE id=?",
            (hashed_password, data.id),
        )
        conn.commit()
        return {"message": "Passwort geändert."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# =====================================================
# API-ROUTEN – STORAGE
# =====================================================

@router.post("/api/storage/add")
def storage_add(
    data: CreateStorage,
    user=Depends(require_login),
    conn=Depends(get_storage_db)
):
    try:
        conn.execute(
            """
            INSERT INTO storage (name, server, pool, filesystem, raid, mountpoint)
            VALUES (?,?,?,?,?,?)
            """,
            (data.name, data.server, data.pool, data.filesystem, data.raid, data.mountpoint)
        )
        conn.commit()
        return {"message": "Speicher angelegt."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Pool existiert bereits.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/storage/list")
def storage_list(
    user=Depends(require_login),
    conn=Depends(get_storage_db)
):
    rows = conn.execute("SELECT * FROM storage ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@router.get("/api/storage/details/{pool}")
def storage_details(
    pool: str,
    user=Depends(require_login),
    conn=Depends(get_storage_db)
):
    row = conn.execute("SELECT * FROM storage WHERE pool=?", (pool,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Pool nicht gefunden.")
    return dict(row)


@router.put("/api/storage/update")
def storage_update(
    data: UpdateStorage,
    user=Depends(require_login),
    conn=Depends(get_storage_db)
):
    conn.execute(
        """
        UPDATE storage
        SET name=?, filesystem=?, raid=?, mountpoint=?
        WHERE pool=?
        """,
        (data.new_name, data.filesystem, data.raid, data.mountpoint, data.name)
    )
    conn.commit()
    return {"message": "Gespeichert."}


@router.delete("/api/storage/delete/{pool}")
def storage_delete(
    pool: str,
    user=Depends(require_login),
    conn=Depends(get_storage_db)
):
    conn.execute("DELETE FROM storage WHERE pool=?", (pool,))
    conn.commit()
    return {"message": "Pool gelöscht."}


# Storage SMART (Platzhalter)
@router.get("/api/storage/smart/{disk}")
def storage_smart(disk: str, user=Depends(require_login)):
    return {}

@router.get("/api/storage/smart/attributes/{disk}")
def storage_smart_attributes(disk: str, user=Depends(require_login)):
    return []

@router.get("/api/storage/smart/log/{disk}")
def storage_smart_log(disk: str, user=Depends(require_login)):
    return {"log": ""}

@router.post("/api/storage/smart/test")
def storage_smart_test(data: StorageAction, user=Depends(require_login)):
    return {"message": "SMART-Test gestartet."}

# Storage Scrub (Platzhalter)
@router.get("/api/storage/scrub/{pool}")
def storage_scrub(pool: str, user=Depends(require_login)):
    return {}

@router.post("/api/storage/scrub/start")
def storage_scrub_start(data: StorageAction, user=Depends(require_login)):
    return {"message": "Scrub gestartet."}

@router.post("/api/storage/scrub/stop")
def storage_scrub_stop(data: StorageAction, user=Depends(require_login)):
    return {"message": "Scrub gestoppt."}

# Storage Snapshots (Platzhalter)
@router.get("/api/storage/snapshots/{pool}")
def snapshot_list(pool: str, user=Depends(require_login)):
    return []

@router.post("/api/storage/snapshot/create")
def snapshot_create(data: SnapshotCreate, user=Depends(require_login)):
    return {"message": "Snapshot erstellt."}

@router.put("/api/storage/snapshot/rename")
def snapshot_rename(data: SnapshotRename, user=Depends(require_login)):
    return {"message": "Snapshot umbenannt."}

@router.delete("/api/storage/snapshot/delete")
def snapshot_delete(data: StorageAction, user=Depends(require_login)):
    return {"message": "Snapshot gelöscht."}

@router.post("/api/storage/snapshot/rollback")
def snapshot_rollback(data: StorageAction, user=Depends(require_login)):
    return {"message": "Rollback erfolgreich."}

@router.post("/api/storage/snapshot/clone")
def snapshot_clone(data: SnapshotClone, user=Depends(require_login)):
    return {"message": "Snapshot geklont."}


# Storage Disks
@router.get("/api/storage/disks")
def storage_disks_all(
    user=Depends(require_login),
    server_conn=Depends(get_server_db)
):
    servers = server_conn.execute(
        "SELECT id, name, host, port, username, password, private_key FROM servers"
    ).fetchall()

    result = []
    for server in servers:
        try:
            with SSHClient(dict(server)) as ssh:
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
        except Exception:
            continue

    return result


@router.get("/api/storage/disks/{server_id}")
def storage_disks_by_server(
    server_id: int,
    user=Depends(require_login),
    server_conn=Depends(get_server_db)
):
    server = server_conn.execute(
        "SELECT id, name, host, port, username, password, private_key FROM servers WHERE id=?",
        (server_id,)
    ).fetchone()

    if not server:
        raise HTTPException(status_code=404, detail="Server nicht gefunden")

    try:
        with SSHClient(dict(server)) as ssh:
            cmd = "lsblk -J -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,SERIAL"
            out = ssh.execute(cmd)
            data = json.loads(out["stdout"])

        return [
            {
                "device": disk.get("name", ""),
                "size": disk.get("size", ""),
                "type": disk.get("type", ""),
                "filesystem": disk.get("fstype", ""),
                "mountpoint": disk.get("mountpoint", ""),
                "model": disk.get("model", ""),
                "serial": disk.get("serial", ""),
                "status": "online"
            }
            for disk in data.get("blockdevices", [])
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Festplatten: {exc}")


# =====================================================
# API-ROUTEN – BACKUP
# =====================================================

@router.get("/api/backup/list")
def backup_list(
    user=Depends(require_login),
    backup_conn=Depends(get_backup_db),
    server_conn=Depends(get_server_db)
):
    backups = backup_conn.execute("SELECT * FROM backups ORDER BY created DESC").fetchall()

    result = []
    for backup in backups:
        server = server_conn.execute(
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


@router.post("/api/backup/create")
def backup_create(
    user=Depends(require_login),
    server_conn=Depends(get_server_db),
    backup_conn=Depends(get_backup_db)
):
    servers = server_conn.execute("SELECT * FROM servers").fetchall()

    if not servers:
        raise HTTPException(status_code=400, detail="Keine Server für Backups gefunden.")

    created = []
    errors = []

    for server in servers:
        try:
            backup_name = f"backup_{server['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            backup_path = f"/tmp/{backup_name}"

            with SSHClient(dict(server)) as ssh:
                result = ssh.execute(
                    f"sudo tar -czf {backup_path} /etc /var/log /home 2>/dev/null || echo 'Backup created with warnings'"
                )
                if result["stderr"] and "Backup created" not in result["stderr"]:
                    raise Exception(result["stderr"])

                size_result = ssh.execute(f"ls -lh {backup_path} | awk '{{print $5}}'")
                size = size_result["stdout"].strip() or "unknown"

            backup_conn.execute(
                "INSERT INTO backups (name, server_id, path, size, status) VALUES (?, ?, ?, ?, ?)",
                (backup_name, server["id"], backup_path, size, "OK")
            )
            backup_conn.commit()
            created.append(backup_name)

            write_log(server["name"], user.username, "INFO", "backup_create", f"Backup {backup_name} erstellt")

        except Exception as exc:
            errors.append(f"{server['name']}: {str(exc)}")
            write_log(server["name"], user.username, "ERROR", "backup_create", str(exc))

    if created:
        msg = f"{len(created)} Backups erstellt: {', '.join(created)}"
        if errors:
            msg += f" (Fehler: {', '.join(errors)})"
        return {"message": msg}
    else:
        raise HTTPException(status_code=500, detail=f"Keine Backups erstellt: {', '.join(errors)}")


@router.post("/api/backup/restore/{backup_id}")
def backup_restore(
    backup_id: int,
    user=Depends(require_login),
    backup_conn=Depends(get_backup_db),
    server_conn=Depends(get_server_db)
):
    backup = backup_conn.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")

    server = server_conn.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    if not server:
        raise HTTPException(status_code=404, detail="Server nicht gefunden")

    try:
        with SSHClient(dict(server)) as ssh:
            check = ssh.execute(f"test -f {backup['path']} && echo 'exists'")
            if "exists" not in check["stdout"]:
                raise Exception(f"Backup-Datei {backup['path']} nicht gefunden")

            result = ssh.execute(f"sudo tar -xzf {backup['path']} -C / 2>/dev/null")
            if result["stderr"]:
                raise Exception(result["stderr"])

        write_log(server["name"], user.username, "INFO", "backup_restore", f"Backup {backup['name']} wiederhergestellt")
        return {"message": f"Backup {backup['name']} erfolgreich wiederhergestellt"}

    except Exception as exc:
        write_log(server["name"], user.username, "ERROR", "backup_restore", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/api/backup/delete/{backup_id}")
def backup_delete(
    backup_id: int,
    user=Depends(require_login),
    backup_conn=Depends(get_backup_db),
    server_conn=Depends(get_server_db)
):
    backup = backup_conn.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup nicht gefunden")

    # Datei löschen (falls vorhanden)
    server = server_conn.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    if server:
        try:
            with SSHClient(dict(server)) as ssh:
                ssh.execute(f"sudo rm -f {backup['path']}")
        except Exception:
            pass

    backup_conn.execute("DELETE FROM backups WHERE id=?", (backup_id,))
    backup_conn.commit()

    write_log(server["name"] if server else "Unbekannt", user.username, "INFO", "backup_delete", f"Backup {backup['name']} gelöscht")
    return {"message": f"Backup {backup['name']} gelöscht"}


# =====================================================
# API-ROUTEN – LOGS
# =====================================================

@router.get("/api/logs/list")
def logs_list(
    level: str = "all",
    server: str = "all",
    user=Depends(require_login),
    conn=Depends(get_logs_db)
):
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if level != "all":
        query += " AND level = ?"
        params.append(level)

    if server != "all":
        query += " AND server = ?"
        params.append(server)

    query += " ORDER BY timestamp DESC LIMIT 1000"

    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


@router.delete("/api/logs/clear")
def logs_clear(
    user=Depends(require_login),
    conn=Depends(get_logs_db)
):
    conn.execute("DELETE FROM logs")
    conn.commit()

    write_log(None, user.username, "INFO", "logs_clear", "Alle Logs wurden gelöscht")
    return {"message": "Alle Logs gelöscht."}