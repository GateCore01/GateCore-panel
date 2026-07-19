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

# -------------------------------------------------
# Container klonen
# -------------------------------------------------

def clone(server,
          vmid,
          newid,
          hostname=None,
          full=True):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"pct clone {vmid} {newid}"
    )

    if hostname:
        command += f" --hostname {hostname}"

    if full:
        command += " --full 1"

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot erstellen
# -------------------------------------------------

def snapshot(server,
             vmid,
             name,
             description=""):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"pct snapshot {vmid} {name}"
    )

    if description:
        command += f' --description "{description}"'

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Snapshotliste
# -------------------------------------------------

def listsnapshot(server,
                 vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct listsnapshot {vmid}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshotnamen
# -------------------------------------------------

def snapshot_names(server,
                   vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct listsnapshot {vmid} | awk 'NR>1 {{print $2}}'"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Snapshot vorhanden?
# -------------------------------------------------

def snapshot_exists(server,
                    vmid,
                    name):

    return name in snapshot_names(
        server,
        vmid
    )


# -------------------------------------------------
# Anzahl Snapshots
# -------------------------------------------------

def snapshot_count(server,
                   vmid):

    return len(
        snapshot_names(
            server,
            vmid
        )
    )


# -------------------------------------------------
# Snapshot löschen
# -------------------------------------------------

def delsnapshot(server,
                vmid,
                name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct delsnapshot {vmid} {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rollback
# -------------------------------------------------

def rollback(server,
             vmid,
             snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct rollback {vmid} {snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot Beschreibung
# -------------------------------------------------

def snapshot_description(server,
                         vmid,
                         snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct listsnapshot {vmid}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Letzten Snapshot
# -------------------------------------------------

def latest_snapshot(server,
                    vmid):

    snapshots = snapshot_names(
        server,
        vmid
    )

    if len(snapshots) == 0:
        return None

    return snapshots[-1]


# -------------------------------------------------
# Ersten Snapshot
# -------------------------------------------------

def first_snapshot(server,
                   vmid):

    snapshots = snapshot_names(
        server,
        vmid
    )

    if len(snapshots) == 0:
        return None

    return snapshots[0]


# -------------------------------------------------
# Template erzeugen
# -------------------------------------------------

def template(server,
             vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct template {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Ist Template?
# -------------------------------------------------

def is_template(server,
                vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct config {vmid} | grep '^template:'"
    )

    ssh.close()

    return result["stdout"] != ""


# -------------------------------------------------
# Template klonen
# -------------------------------------------------

def clone_template(server,
                   template_id,
                   new_id,
                   hostname):

    return clone(
        server,
        template_id,
        new_id,
        hostname=hostname,
        full=True
    )


# -------------------------------------------------
# Snapshot Informationen
# -------------------------------------------------

def snapshot_info(server,
                  vmid,
                  snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct listsnapshot {vmid} | grep '{snapshot}'"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Snapshots löschen
# -------------------------------------------------

def delete_all_snapshots(server,
                         vmid):

    snapshots = snapshot_names(
        server,
        vmid
    )

    results = []

    for snap in snapshots:

        results.append(
            delsnapshot(
                server,
                vmid,
                snap
            )
        )

    return results

# -------------------------------------------------
# Backup erstellen (vzdump)
# -------------------------------------------------

def backup(server,
           vmid,
           storage="local",
           mode="snapshot",
           compress="zstd"):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"vzdump {vmid} "
        f"--storage {storage} "
        f"--mode {mode} "
        f"--compress {compress}"
    )

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Backup wiederherstellen
# -------------------------------------------------

def restore(server,
            backup_file,
            vmid,
            storage="local-lvm"):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"pct restore {vmid} "
        f"{backup_file} "
        f"--storage {storage}"
    )

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Backupdateien anzeigen
# -------------------------------------------------

def backup_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "find /var/lib/vz/dump -type f"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Backup löschen
# -------------------------------------------------

def backup_delete(server,
                  filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"rm -f {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backupgröße
# -------------------------------------------------

def backup_size(server,
                filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ls -lh {filename}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container migrieren
# -------------------------------------------------

def migrate(server,
            vmid,
            target):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct migrate {vmid} {target}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Live-Migration
# -------------------------------------------------

def migrate_online(server,
                   vmid,
                   target):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct migrate {vmid} {target} --online"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Mountpoint einhängen
# -------------------------------------------------

def mount(server,
          vmid,
          mp="mp0"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct mount {vmid} {mp}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Mountpoint aushängen
# -------------------------------------------------

def unmount(server,
            vmid,
            mp="mp0"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct unmount {vmid} {mp}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Datei in Container kopieren
# -------------------------------------------------

def push(server,
         vmid,
         source,
         target):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct push {vmid} {source} {target}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Datei aus Container kopieren
# -------------------------------------------------

def pull(server,
         vmid,
         source,
         target):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct pull {vmid} {source} {target}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dateisystem prüfen
# -------------------------------------------------

def fsck(server,
         vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct fsck {vmid}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup vorhanden?
# -------------------------------------------------

def backup_exists(server,
                  filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"test -f {filename} && echo YES || echo NO"
    )

    ssh.close()

    return result["stdout"] == "YES"


# -------------------------------------------------
# Backup Hash
# -------------------------------------------------

def backup_sha256(server,
                  filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sha256sum {filename}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Backup umbenennen
# -------------------------------------------------

def backup_rename(server,
                  old_name,
                  new_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"mv {old_name} {new_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup komprimieren
# -------------------------------------------------

def backup_compress(server,
                    filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"gzip -f {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup entpacken
# -------------------------------------------------

def backup_decompress(server,
                      filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"gunzip -f {filename}"
    )

    ssh.close()

    return result

# -------------------------------------------------
# CPU Kerne ändern
# -------------------------------------------------

def set_cpu(server, vmid, cores):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --cores {cores}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RAM ändern
# -------------------------------------------------

def set_memory(server, vmid, memory):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --memory {memory}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Swap ändern
# -------------------------------------------------

def set_swap(server, vmid, swap):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --swap {swap}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RootFS vergrößern
# -------------------------------------------------

def resize(server, vmid, size):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct resize {vmid} rootfs {size}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hostname ändern
# -------------------------------------------------

def set_hostname(server, vmid, hostname):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --hostname {hostname}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Beschreibung ändern
# -------------------------------------------------

def set_description(server, vmid, description):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f'pct set {vmid} --description "{description}"'
    )

    ssh.close()

    return result


# -------------------------------------------------
# Tags setzen
# -------------------------------------------------

def set_tags(server, vmid, tags):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f'pct set {vmid} --tags "{tags}"'
    )

    ssh.close()

    return result


# -------------------------------------------------
# DNS Server
# -------------------------------------------------

def set_dns(server, vmid, dns):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --nameserver {dns}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Search Domain
# -------------------------------------------------

def set_searchdomain(server, vmid, domain):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --searchdomain {domain}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Netzwerk ändern
# -------------------------------------------------

def set_network(server,
                vmid,
                bridge="vmbr0",
                ip="dhcp",
                gateway=None):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"pct set {vmid} "
        f"--net0 name=eth0,bridge={bridge},ip={ip}"
    )

    if gateway:
        command += f",gw={gateway}"

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Autostart aktivieren
# -------------------------------------------------

def enable_autostart(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --onboot 1"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Autostart deaktivieren
# -------------------------------------------------

def disable_autostart(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --onboot 0"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Firewall aktivieren
# -------------------------------------------------

def firewall_enable(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --features firewall=1"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Firewall deaktivieren
# -------------------------------------------------

def firewall_disable(server, vmid):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"pct set {vmid} --features firewall=0"
    )

    ssh.close()

    return result


# -------------------------------------------------
# CPU Auslastung
# -------------------------------------------------

def cpu_usage(server, vmid):

    return exec(
        server,
        vmid,
        "top -bn1 | head -5"
    )["stdout"]


# -------------------------------------------------
# RAM Auslastung
# -------------------------------------------------

def memory_usage(server, vmid):

    return exec(
        server,
        vmid,
        "free -h"
    )["stdout"]


# -------------------------------------------------
# Speicherbelegung
# -------------------------------------------------

def disk_usage(server, vmid):

    return exec(
        server,
        vmid,
        "df -h"
    )["stdout"]


# -------------------------------------------------
# Uptime
# -------------------------------------------------

def uptime(server, vmid):

    return exec(
        server,
        vmid,
        "uptime"
    )["stdout"]


# -------------------------------------------------
# IP-Adresse
# -------------------------------------------------

def ip_address(server, vmid):

    return exec(
        server,
        vmid,
        "hostname -I"
    )["stdout"]


# -------------------------------------------------
# Betriebssystem
# -------------------------------------------------

def os_release(server, vmid):

    return exec(
        server,
        vmid,
        "cat /etc/os-release"
    )["stdout"]


# -------------------------------------------------
# Kernel
# -------------------------------------------------

def kernel(server, vmid):

    return exec(
        server,
        vmid,
        "uname -r"
    )["stdout"]


# -------------------------------------------------
# Load Average
# -------------------------------------------------

def load(server, vmid):

    return exec(
        server,
        vmid,
        "cat /proc/loadavg"
    )["stdout"]


# -------------------------------------------------
# Prozesse
# -------------------------------------------------

def processes(server, vmid):

    return exec(
        server,
        vmid,
        "ps aux"
    )["stdout"]


# -------------------------------------------------
# Neustart erforderlich?
# -------------------------------------------------

def reboot_required(server, vmid):

    return exec(
        server,
        vmid,
        "test -f /run/reboot-required && echo YES || echo NO"
    )["stdout"] == "YES"


# -------------------------------------------------
# Container Informationen
# -------------------------------------------------

def info(server, vmid):

    return {
        "status": status_id(server, vmid),
        "config": config(server, vmid),
        "cpu": cpu_usage(server, vmid),
        "memory": memory_usage(server, vmid),
        "disk": disk_usage(server, vmid),
        "uptime": uptime(server, vmid),
        "ip": ip_address(server, vmid),
        "os": os_release(server, vmid),
        "kernel": kernel(server, vmid)
    }