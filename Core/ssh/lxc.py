from ssh.client import SSHClient


# -------------------------------------------------
# Alle Container auflisten
# -------------------------------------------------

def list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Status aller Container
# -------------------------------------------------

def status(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Status eines Containers
# -------------------------------------------------

def status_id(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct status {vmid}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Konfiguration eines Containers
# -------------------------------------------------

def config(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct config {vmid}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Konfiguration aller Container
# -------------------------------------------------

def config_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "echo '=========='; "
        "echo $i; "
        "pct config $i; "
        "done"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container erstellen
# -------------------------------------------------

def create(server,
           vmid,
           template,
           hostname,
           storage,
           password,
           cores=2,
           memory=2048,
           disk=8,
           swap=512,
           bridge="vmbr0"):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"pct create {vmid} {template} "
        f"--hostname {hostname} "
        f"--storage {storage} "
        f"--rootfs {storage}:{disk} "
        f"--cores {cores} "
        f"--memory {memory} "
        f"--swap {swap} "
        f"--net0 name=eth0,bridge={bridge},ip=dhcp "
        f"--password '{password}' "
        "--unprivileged 1 "
        "--features nesting=1"
    )

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Container starten
# -------------------------------------------------

def start(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct start {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container starten
# -------------------------------------------------

def start_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct start $i; "
        "done"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container stoppen
# -------------------------------------------------

def stop(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct stop {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container stoppen
# -------------------------------------------------

def stop_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct stop $i; "
        "done"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container sauber herunterfahren
# -------------------------------------------------

def shutdown(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct shutdown {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container herunterfahren
# -------------------------------------------------

def shutdown_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct shutdown $i; "
        "done"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container neu starten
# -------------------------------------------------

def reboot(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct reboot {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container neu starten
# -------------------------------------------------

def reboot_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct reboot $i; "
        "done"
    )

    ssh.close()

    return result

# -------------------------------------------------
# Container pausieren
# -------------------------------------------------

def suspend(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct suspend {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container pausieren
# -------------------------------------------------

def suspend_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct suspend $i; "
        "done"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container fortsetzen
# -------------------------------------------------

def resume(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct resume {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Container fortsetzen
# -------------------------------------------------

def resume_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "for i in $(pct list | awk 'NR>1 {print $1}'); do "
        "pct resume $i; "
        "done"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container löschen
# -------------------------------------------------

def destroy(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct destroy {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Befehl im Container ausführen
# -------------------------------------------------

def exec(server, vmid, command):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct exec {vmid} -- {command}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bash im Container
# -------------------------------------------------

def bash(server, vmid):

    return exec(
        server,
        vmid,
        "/bin/bash"
    )


# -------------------------------------------------
# Shell im Container
# -------------------------------------------------

def shell(server, vmid):

    return exec(
        server,
        vmid,
        "/bin/sh"
    )


# -------------------------------------------------
# Container-Konsole
# -------------------------------------------------

def console(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct console {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container betreten
# -------------------------------------------------

def enter(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct enter {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container entsperren
# -------------------------------------------------

def unlock(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct unlock {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pending Änderungen
# -------------------------------------------------

def pending(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct pending {vmid}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Prüfen ob Container läuft
# -------------------------------------------------

def is_running(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct status {vmid}"
    )

    ssh.close()

    return "running" in result["stdout"]


# -------------------------------------------------
# Prüfen ob Container gestoppt ist
# -------------------------------------------------

def is_stopped(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct status {vmid}"
    )

    ssh.close()

    return "stopped" in result["stdout"]


# -------------------------------------------------
# Container existiert
# -------------------------------------------------

def exists(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list | awk 'NR>1 {print $1}'"
    )

    ssh.close()

    ids = result["stdout"].splitlines()

    return str(vmid) in ids


# -------------------------------------------------
# Anzahl Container
# -------------------------------------------------

def count(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list | tail -n +2 | wc -l"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# Laufende Container
# -------------------------------------------------

def running(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list | grep running"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Gestoppte Container
# -------------------------------------------------

def stopped(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "pct list | grep stopped"
    )

    ssh.close()

    return result["stdout"]

