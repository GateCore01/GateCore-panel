###########################################################################
# File: Core/routes.py – Alle Routen (Seiten & API)
###########################################################################
import sqlite3
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from auth import require_login, hash_password
from database import (
    get_server, get_server_db, get_docker_db, get_storage_db,
    get_logs_db, get_user_db, get_backup_db, write_log
)
from models import (
    AddDockerContainer, CreateBtrfsPool, CreateBtrfsSubvolume,
    CreateBtrfsSnapshot, AddServer, AddUser, ChangePassword
)
from ssh.client import SSHClient
from ssh.docker import (
    list_containers, start_container, stop_container,
    restart_container, delete_container, create_container,
    container_logs
)
from ssh.btrfs import (
    create_pool, delete_pool, create_subvolume, delete_subvolume,
    list_subvolumes, create_snapshot, delete_snapshot, list_snapshots,
    scrub_start, scrub_status
)

BASE_DIR = Path(__file__).resolve().parent
router = APIRouter()

# ===== SEITEN =====
@router.get("/")
def login_page(): return FileResponse(BASE_DIR / "templates" / "index.html")
@router.get("/login")
def login_alias(): return FileResponse(BASE_DIR / "templates" / "index.html")

@router.get("/panel")
def panel(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "index.html")
@router.get("/panel/backup")
def backup_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "backup.html")
@router.get("/panel/users")
def users_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "users.html")
@router.get("/panel/servers")
def servers_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "servers.html")
@router.get("/panel/server_add")
def server_add_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "server_add.html")
@router.get("/panel/settings")
def settings_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "settings.html")
@router.get("/panel/logs")
def logs_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "logs.html")
@router.get("/panel/docker")
def docker_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "docker.html")
@router.get("/panel/docker_add")
def docker_add_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "docker_add.html")
@router.get("/panel/storage")
def storage_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage.html")
@router.get("/panel/storage/add")
def storage_add_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-add.html")
@router.get("/panel/storage/details")
def storage_details_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-details.html")
@router.get("/panel/storage/edit")
def storage_edit_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-edit.html")
@router.get("/panel/storage/smart")
def storage_smart_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-smart.html")
@router.get("/panel/storage/snapshots")
def storage_snapshots_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-snapshots.html")
@router.get("/panel/storage/scrub")
def storage_scrub_page(user=Depends(require_login)): return FileResponse(BASE_DIR / "templates" / "panel" / "storage-scrub.html")

# ===== API – DOCKER =====
@router.get("/api/docker/containers")
def docker_list(user=Depends(require_login), conn=Depends(get_docker_db)):
    containers = conn.execute("SELECT * FROM docker_containers ORDER BY name").fetchall()
    result = []
    for c in containers:
        server = get_server(c["server_id"])
        status = "unknown"
        if server:
            try:
                with SSHClient(dict(server)) as ssh:
                    out = ssh.execute(f"docker inspect {c['name']} --format '{{{{.State.Status}}}}'")
                    status = out["stdout"].strip() or "unknown"
            except:
                pass
        result.append({**dict(c), "status": status})
    return result

@router.post("/api/docker/container/create")
def docker_create(data: AddDockerContainer, user=Depends(require_login), conn=Depends(get_docker_db)):
    server = get_server(data.server_id)
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        container_id = create_container(
            dict(server), data.name, data.image, data.command,
            data.env, data.volumes, data.ports, data.detach
        )
        conn.execute(
            "INSERT INTO docker_containers (name, server_id, image, command) VALUES (?,?,?,?)",
            (data.name, data.server_id, data.image, data.command)
        )
        conn.commit()
        write_log(server["name"], user.username, "INFO", "docker_create", f"Container {data.name} erstellt")
        return {"message": f"Container {data.name} erstellt", "container_id": container_id}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/api/docker/container/start/{container_id}")
def docker_start(container_id: int, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    server = get_server(container["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        start_container(dict(server), container["name"])
        write_log(server["name"], user.username, "INFO", "docker_start", f"Container {container['name']} gestartet")
        return {"message": f"Container {container['name']} gestartet"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/api/docker/container/stop/{container_id}")
def docker_stop(container_id: int, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    server = get_server(container["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        stop_container(dict(server), container["name"])
        write_log(server["name"], user.username, "INFO", "docker_stop", f"Container {container['name']} gestoppt")
        return {"message": f"Container {container['name']} gestoppt"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/api/docker/container/restart/{container_id}")
def docker_restart(container_id: int, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    server = get_server(container["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        restart_container(dict(server), container["name"])
        write_log(server["name"], user.username, "INFO", "docker_restart", f"Container {container['name']} neugestartet")
        return {"message": f"Container {container['name']} neugestartet"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/api/docker/container/delete/{container_id}")
def docker_delete(container_id: int, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    server = get_server(container["server_id"])
    try:
        if server:
            delete_container(dict(server), container["name"], force=True)
        conn.execute("DELETE FROM docker_containers WHERE id=?", (container_id,))
        conn.commit()
        write_log(server["name"] if server else "Unbekannt", user.username, "INFO", "docker_delete", f"Container {container['name']} gelöscht")
        return {"message": f"Container {container['name']} gelöscht"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/api/docker/container/logs/{container_id}")
def docker_logs(container_id: int, tail: int = 100, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    server = get_server(container["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        logs = container_logs(dict(server), container["name"], tail)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(500, str(e))

# ===== API – BTRFS STORAGE =====
@router.get("/api/storage/pools")
def btrfs_pools(user=Depends(require_login), conn=Depends(get_storage_db)):
    pools = conn.execute("SELECT * FROM storage_pools ORDER BY name").fetchall()
    return [dict(p) for p in pools]

@router.post("/api/storage/pool/create")
def btrfs_create_pool(data: CreateBtrfsPool, user=Depends(require_login), conn=Depends(get_storage_db)):
    server = get_server(data.server_id)
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        result = create_pool(dict(server), data.devices, data.raid_level, data.mountpoint)
        conn.execute(
            "INSERT INTO storage_pools (name, server_id, mountpoint, raid_level, devices) VALUES (?,?,?,?,?)",
            (data.name, data.server_id, data.mountpoint, data.raid_level, json.dumps(data.devices))
        )
        conn.commit()
        write_log(server["name"], user.username, "INFO", "btrfs_create_pool", f"Pool {data.name} erstellt")
        return {"message": result}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/api/storage/pool/{pool_id}")
def btrfs_delete_pool(pool_id: int, user=Depends(require_login), conn=Depends(get_storage_db)):
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (pool_id,)).fetchone()
    if not pool:
        raise HTTPException(404, "Pool nicht gefunden")
    server = get_server(pool["server_id"])
    if server:
        try:
            delete_pool(dict(server), pool["mountpoint"])
        except:
            pass
    conn.execute("DELETE FROM storage_pools WHERE id=?", (pool_id,))
    conn.commit()
    write_log(server["name"] if server else "Unbekannt", user.username, "INFO", "btrfs_delete_pool", f"Pool {pool['name']} gelöscht")
    return {"message": "Pool gelöscht"}

@router.get("/api/storage/subvolumes")
def btrfs_subvolumes(pool_id: int | None = None, user=Depends(require_login), conn=Depends(get_storage_db)):
    if pool_id:
        subvols = conn.execute("SELECT * FROM btrfs_subvolumes WHERE pool_id=?", (pool_id,)).fetchall()
    else:
        subvols = conn.execute("SELECT * FROM btrfs_subvolumes").fetchall()
    return [dict(s) for s in subvols]

@router.post("/api/storage/subvolume/create")
def btrfs_create_subvolume(data: CreateBtrfsSubvolume, user=Depends(require_login), conn=Depends(get_storage_db)):
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (data.pool_id,)).fetchone()
    if not pool:
        raise HTTPException(404, "Pool nicht gefunden")
    server = get_server(pool["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        result = create_subvolume(dict(server), pool["mountpoint"], data.name)
        conn.execute(
            "INSERT INTO btrfs_subvolumes (pool_id, name, path) VALUES (?,?,?)",
            (data.pool_id, data.name, f"{pool['mountpoint']}/{data.name}")
        )
        conn.commit()
        write_log(server["name"], user.username, "INFO", "btrfs_create_subvol", f"Subvolume {data.name} erstellt")
        return {"message": result}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/api/storage/subvolume/{subvol_id}")
def btrfs_delete_subvolume(subvol_id: int, user=Depends(require_login), conn=Depends(get_storage_db)):
    subvol = conn.execute("SELECT * FROM btrfs_subvolumes WHERE id=?", (subvol_id,)).fetchone()
    if not subvol:
        raise HTTPException(404, "Subvolume nicht gefunden")
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (subvol["pool_id"],)).fetchone()
    if pool:
        server = get_server(pool["server_id"])
        if server:
            try:
                delete_subvolume(dict(server), subvol["path"])
            except:
                pass
    conn.execute("DELETE FROM btrfs_subvolumes WHERE id=?", (subvol_id,))
    conn.commit()
    return {"message": "Subvolume gelöscht"}

@router.get("/api/storage/snapshots")
def btrfs_snapshots(pool_id: int | None = None, user=Depends(require_login), conn=Depends(get_storage_db)):
    if pool_id:
        snaps = conn.execute(
            "SELECT * FROM btrfs_snapshots WHERE subvolume_id IN (SELECT id FROM btrfs_subvolumes WHERE pool_id=?)",
            (pool_id,)
        ).fetchall()
    else:
        snaps = conn.execute("SELECT * FROM btrfs_snapshots").fetchall()
    return [dict(s) for s in snaps]

@router.post("/api/storage/snapshot/create")
def btrfs_create_snapshot(data: CreateBtrfsSnapshot, user=Depends(require_login), conn=Depends(get_storage_db)):
    subvol = conn.execute("SELECT * FROM btrfs_subvolumes WHERE id=?", (data.subvolume_id,)).fetchone()
    if not subvol:
        raise HTTPException(404, "Subvolume nicht gefunden")
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (subvol["pool_id"],)).fetchone()
    if not pool:
        raise HTTPException(404, "Pool nicht gefunden")
    server = get_server(pool["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    snapshot_path = f"{pool['mountpoint']}/{data.snapshot_name}"
    try:
        result = create_snapshot(dict(server), subvol["path"], snapshot_path)
        conn.execute(
            "INSERT INTO btrfs_snapshots (subvolume_id, snapshot_name, path) VALUES (?,?,?)",
            (data.subvolume_id, data.snapshot_name, snapshot_path)
        )
        conn.commit()
        write_log(server["name"], user.username, "INFO", "btrfs_create_snapshot", f"Snapshot {data.snapshot_name} erstellt")
        return {"message": result}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/api/storage/snapshot/{snapshot_id}")
def btrfs_delete_snapshot(snapshot_id: int, user=Depends(require_login), conn=Depends(get_storage_db)):
    snap = conn.execute("SELECT * FROM btrfs_snapshots WHERE id=?", (snapshot_id,)).fetchone()
    if not snap:
        raise HTTPException(404, "Snapshot nicht gefunden")
    subvol = conn.execute("SELECT * FROM btrfs_subvolumes WHERE id=?", (snap["subvolume_id"],)).fetchone()
    if subvol:
        pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (subvol["pool_id"],)).fetchone()
        if pool:
            server = get_server(pool["server_id"])
            if server:
                try:
                    delete_snapshot(dict(server), snap["path"])
                except:
                    pass
    conn.execute("DELETE FROM btrfs_snapshots WHERE id=?", (snapshot_id,))
    conn.commit()
    return {"message": "Snapshot gelöscht"}

@router.post("/api/storage/pool/{pool_id}/scrub/start")
def btrfs_scrub_start(pool_id: int, user=Depends(require_login), conn=Depends(get_storage_db)):
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (pool_id,)).fetchone()
    if not pool:
        raise HTTPException(404, "Pool nicht gefunden")
    server = get_server(pool["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        result = scrub_start(dict(server), pool["mountpoint"])
        return {"message": result}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/api/storage/pool/{pool_id}/scrub/status")
def btrfs_scrub_status(pool_id: int, user=Depends(require_login), conn=Depends(get_storage_db)):
    pool = conn.execute("SELECT * FROM storage_pools WHERE id=?", (pool_id,)).fetchone()
    if not pool:
        raise HTTPException(404, "Pool nicht gefunden")
    server = get_server(pool["server_id"])
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        status = scrub_status(dict(server), pool["mountpoint"])
        return {"status": status}
    except Exception as e:
        raise HTTPException(500, str(e))

# ===== API – SERVER (unverändert) =====
@router.post("/api/server/add")
def add_server(data: AddServer, user=Depends(require_login), conn=Depends(get_server_db)):
    try:
        conn.execute(
            "INSERT INTO servers (name, host, port, username, password, private_key) VALUES (?,?,?,?,?,?)",
            (data.hostname, data.ip, data.port, data.username, data.password, data.private_key)
        )
        conn.commit()
        return {"message": "Server gespeichert."}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Servername existiert bereits.")
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/api/server/test")
def test_server_connection(data: AddServer, user=Depends(require_login)):
    try:
        with SSHClient({
            "host": data.ip, "port": data.port, "username": data.username,
            "password": data.password, "private_key": data.private_key
        }) as ssh:
            result = ssh.execute("hostname")
        if result["stderr"]:
            raise HTTPException(400, result["stderr"])
        return {"message": f"Verbindung erfolgreich. Hostname: {result['stdout']}"}
    except Exception as e:
        raise HTTPException(500, f"Verbindung fehlgeschlagen: {e}")

@router.post("/api/server/test/{server_id}")
def test_server_connection_by_id(server_id: int, user=Depends(require_login), conn=Depends(get_server_db)):
    row = conn.execute("SELECT * FROM servers WHERE id=?", (server_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        with SSHClient(dict(row)) as ssh:
            result = ssh.execute("hostname")
        if result["stderr"]:
            raise HTTPException(400, result["stderr"])
        return {"message": f"Verbindung erfolgreich. Hostname: {result['stdout']}"}
    except Exception as e:
        raise HTTPException(500, f"Verbindung fehlgeschlagen: {e}")

@router.delete("/api/server/delete/{server_id}")
def delete_server(server_id: int, user=Depends(require_login), conn=Depends(get_server_db)):
    cursor = conn.execute("DELETE FROM servers WHERE id=?", (server_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(404, "Server nicht gefunden.")
    return {"message": "Server gelöscht."}

@router.get("/api/server/list")
def list_servers(user=Depends(require_login), conn=Depends(get_server_db)):
    rows = conn.execute("SELECT id, name, host, port, username FROM servers ORDER BY name").fetchall()
    return [dict(row) for row in rows]

@router.get("/api/server/select")
def server_select(user=Depends(require_login), conn=Depends(get_server_db)):
    rows = conn.execute("SELECT id, name FROM servers ORDER BY name").fetchall()
    return [dict(row) for row in rows]

# ===== API – BENUTZER (unverändert) =====
@router.get("/api/users/list")
def user_list(user=Depends(require_login), conn=Depends(get_user_db)):
    rows = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    return [dict(row) for row in rows]

@router.post("/api/users/add")
def add_user(data: AddUser, user=Depends(require_login), conn=Depends(get_user_db)):
    try:
        hashed = hash_password(data.password)
        conn.execute("INSERT INTO users (username, password) VALUES (?,?)", (data.username, hashed))
        conn.commit()
        return {"message": "Benutzer erstellt."}
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Benutzername existiert bereits.")
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete("/api/users/delete/{user_id}")
def delete_user(user_id: int, user=Depends(require_login), conn=Depends(get_user_db)):
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    return {"message": "Benutzer gelöscht."}

@router.put("/api/users/password")
def change_password(data: ChangePassword, user=Depends(require_login), conn=Depends(get_user_db)):
    hashed = hash_password(data.password)
    conn.execute("UPDATE users SET password=? WHERE id=?", (hashed, data.id))
    conn.commit()
    return {"message": "Passwort geändert."}

# ===== API – LOGS (unverändert) =====
@router.get("/api/logs/list")
def logs_list(level: str = "all", server: str = "all", user=Depends(require_login), conn=Depends(get_logs_db)):
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
def logs_clear(user=Depends(require_login), conn=Depends(get_logs_db)):
    conn.execute("DELETE FROM logs")
    conn.commit()
    write_log(None, user.username, "INFO", "logs_clear", "Alle Logs gelöscht")
    return {"message": "Alle Logs gelöscht."}

# ===== API – BACKUP (unverändert, aber angepasst) =====
@router.get("/api/backup/list")
def backup_list(user=Depends(require_login), backup_conn=Depends(get_backup_db), server_conn=Depends(get_server_db)):
    backups = backup_conn.execute("SELECT * FROM backups ORDER BY created DESC").fetchall()
    result = []
    for b in backups:
        server = server_conn.execute("SELECT name FROM servers WHERE id=?", (b["server_id"],)).fetchone()
        result.append({
            "id": b["id"], "name": b["name"], "server": server["name"] if server else "Unbekannt",
            "path": b["path"], "size": b["size"] or "-", "status": b["status"], "date": b["created"]
        })
    return result

@router.post("/api/backup/create")
def backup_create(user=Depends(require_login), server_conn=Depends(get_server_db), backup_conn=Depends(get_backup_db)):
    servers = server_conn.execute("SELECT * FROM servers").fetchall()
    if not servers:
        raise HTTPException(400, "Keine Server für Backups gefunden.")
    created = []
    errors = []
    for server in servers:
        try:
            backup_name = f"backup_{server['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
            backup_path = f"/tmp/{backup_name}"
            with SSHClient(dict(server)) as ssh:
                ssh.execute(f"sudo tar -czf {backup_path} /etc /var/log /home 2>/dev/null")
                size = ssh.execute(f"ls -lh {backup_path} | awk '{{print $5}}'")["stdout"].strip()
            backup_conn.execute(
                "INSERT INTO backups (name, server_id, path, size, status) VALUES (?,?,?,?,?)",
                (backup_name, server["id"], backup_path, size, "OK")
            )
            backup_conn.commit()
            created.append(backup_name)
            write_log(server["name"], user.username, "INFO", "backup_create", f"Backup {backup_name} erstellt")
        except Exception as e:
            errors.append(f"{server['name']}: {str(e)}")
    if created:
        msg = f"{len(created)} Backups erstellt: {', '.join(created)}"
        if errors:
            msg += f" (Fehler: {', '.join(errors)})"
        return {"message": msg}
    raise HTTPException(500, f"Keine Backups erstellt: {', '.join(errors)}")

@router.post("/api/backup/restore/{backup_id}")
def backup_restore(backup_id: int, user=Depends(require_login), backup_conn=Depends(get_backup_db), server_conn=Depends(get_server_db)):
    backup = backup_conn.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    if not backup:
        raise HTTPException(404, "Backup nicht gefunden")
    server = server_conn.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    if not server:
        raise HTTPException(404, "Server nicht gefunden")
    try:
        with SSHClient(dict(server)) as ssh:
            ssh.execute(f"sudo tar -xzf {backup['path']} -C /")
        write_log(server["name"], user.username, "INFO", "backup_restore", f"Backup {backup['name']} wiederhergestellt")
        return {"message": f"Backup {backup['name']} erfolgreich wiederhergestellt"}
    except Exception as e:
        write_log(server["name"], user.username, "ERROR", "backup_restore", str(e))
        raise HTTPException(500, str(e))

@router.delete("/api/backup/delete/{backup_id}")
def backup_delete(backup_id: int, user=Depends(require_login), backup_conn=Depends(get_backup_db), server_conn=Depends(get_server_db)):
    backup = backup_conn.execute("SELECT * FROM backups WHERE id=?", (backup_id,)).fetchone()
    if not backup:
        raise HTTPException(404, "Backup nicht gefunden")
    server = server_conn.execute("SELECT * FROM servers WHERE id=?", (backup["server_id"],)).fetchone()
    if server:
        try:
            with SSHClient(dict(server)) as ssh:
                ssh.execute(f"sudo rm -f {backup['path']}")
        except:
            pass
    backup_conn.execute("DELETE FROM backups WHERE id=?", (backup_id,))
    backup_conn.commit()
    write_log(server["name"] if server else "Unbekannt", user.username, "INFO", "backup_delete", f"Backup {backup['name']} gelöscht")
    return {"message": f"Backup {backup['name']} gelöscht"}

@router.get("/api/docker/container/{container_id}")
def docker_container_details(container_id: int, user=Depends(require_login), conn=Depends(get_docker_db)):
    container = conn.execute("SELECT * FROM docker_containers WHERE id=?", (container_id,)).fetchone()
    if not container:
        raise HTTPException(404, "Container nicht gefunden")
    return dict(container)