from ssh.client import SSHClient


# -------------------------------------------------
# Alle Container anzeigen
# -------------------------------------------------

def list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lxc-ls --fancy"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Nur Containernamen
# -------------------------------------------------

def names(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lxc-ls"
    )

    ssh.close()

    return result["stdout"].split()


# -------------------------------------------------
# Existiert Container?
# -------------------------------------------------

def exists(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name}"
    )

    ssh.close()

    return result["stderr"] == ""


# -------------------------------------------------
# Status
# -------------------------------------------------

def status(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Läuft Container?
# -------------------------------------------------

def running(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name} | grep State"
    )

    ssh.close()

    return "RUNNING" in result["stdout"]


# -------------------------------------------------
# Starten
# -------------------------------------------------

def start(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-start -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Stoppen
# -------------------------------------------------

def stop(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-stop -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Neustarten
# -------------------------------------------------

def restart(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    ssh.execute(
        f"sudo lxc-stop -n {name}"
    )

    result = ssh.execute(
        f"sudo lxc-start -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container pausieren
# -------------------------------------------------

def freeze(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-freeze -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pause aufheben
# -------------------------------------------------

def unfreeze(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-unfreeze -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Auf Status warten
# -------------------------------------------------

def wait(server,
         name,
         state="RUNNING"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-wait -n {name} -s {state}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container Informationen
# -------------------------------------------------

def info(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Ausführliche Informationen
# -------------------------------------------------

def info_full(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name} -H"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Prozess-ID
# -------------------------------------------------

def pid(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name} -pH"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# IP-Adresse
# -------------------------------------------------

def ip(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"lxc-info -n {name} -iH"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# RAM Nutzung
# -------------------------------------------------

def memory(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    pid_result = ssh.execute(
        f"lxc-info -n {name} -pH"
    )

    pid = pid_result["stdout"].strip()

    if pid == "":
        ssh.close()
        return ""

    result = ssh.execute(
        f"ps -p {pid} -o rss="
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# CPU Nutzung
# -------------------------------------------------

def cpu(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    pid_result = ssh.execute(
        f"lxc-info -n {name} -pH"
    )

    pid = pid_result["stdout"].strip()

    if pid == "":
        ssh.close()
        return ""

    result = ssh.execute(
        f"ps -p {pid} -o %cpu="
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Container erstellen
# -------------------------------------------------

def create(server,
           name,
           template,
           backing_store="dir"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t {template} "
        f"-B {backing_store}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container löschen
# -------------------------------------------------

def destroy(server,
            name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-destroy -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container klonen
# -------------------------------------------------

def copy(server,
         source,
         target,
         snapshot=False):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"sudo lxc-copy "
        f"-n {source} "
        f"-N {target}"
    )

    if snapshot:
        command += " -s"

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot erstellen
# -------------------------------------------------

def snapshot(server,
             name,
             snapshot_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-snapshot "
        f"-n {name} "
        f"-N {snapshot_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshots anzeigen
# -------------------------------------------------

def snapshots(server,
              name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-snapshot "
        f"-n {name} "
        "-L"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot wiederherstellen
# -------------------------------------------------

def restore_snapshot(server,
                     name,
                     snapshot_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-snapshot "
        f"-n {name} "
        f"-r {snapshot_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot löschen
# -------------------------------------------------

def delete_snapshot(server,
                    name,
                    snapshot_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-snapshot "
        f"-n {name} "
        f"-d {snapshot_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Konfiguration anzeigen
# -------------------------------------------------

def config(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Konfiguration sichern
# -------------------------------------------------

def backup_config(server,
                  name,
                  destination):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cp "
        f"/var/lib/lxc/{name}/config "
        f"{destination}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Konfiguration ersetzen
# -------------------------------------------------

def restore_config(server,
                   name,
                   source):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cp "
        f"{source} "
        f"/var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RootFS Pfad
# -------------------------------------------------

def rootfs(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"grep '^lxc.rootfs.path' "
        f"/var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container Pfad
# -------------------------------------------------

def path(server,
         name):

    return f"/var/lib/lxc/{name}"


# -------------------------------------------------
# Containergröße
# -------------------------------------------------

def size(server,
         name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"du -sh /var/lib/lxc/{name}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container exportieren
# -------------------------------------------------

def export(server,
           name,
           archive):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"tar -czf {archive} "
        f"/var/lib/lxc/{name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container importieren
# -------------------------------------------------

def import_container(server,
                     archive):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"tar -xzf {archive} "
        f"-C /var/lib/lxc/"
    )

    ssh.close()

    return result

# -------------------------------------------------
# Kommando im Container ausführen
# -------------------------------------------------

def attach(server,
           name,
           command="/bin/bash"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- {command}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Shell öffnen
# -------------------------------------------------

def shell(server,
          name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Konsole öffnen
# -------------------------------------------------

def console(server,
            name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-console -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Container überwachen
# -------------------------------------------------

def monitor(server,
            name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-monitor -n {name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Top (alle Container)
# -------------------------------------------------

def top(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo lxc-top"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# CGroup Informationen
# -------------------------------------------------

def cgroup(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Einzelnen CGroup Wert lesen
# -------------------------------------------------

def cgroup_get(server,
               name,
               key):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} {key}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# CGroup Wert setzen
# -------------------------------------------------

def cgroup_set(server,
               name,
               key,
               value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} {key} {value}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gerät hinzufügen
# -------------------------------------------------

def add_device(server,
               name,
               host_path,
               container_path):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo 'lxc.mount.entry = "
        f"{host_path} {container_path} none bind,create=file 0 0' "
        f"| sudo tee -a /var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result


# -------------------------------------------------
# USB Gerät durchreichen
# -------------------------------------------------

def usb_device(server,
               name,
               device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo 'lxc.mount.entry = "
        f"{device} {device} none bind,optional,create=file 0 0' "
        f"| sudo tee -a /var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Ordner mounten
# -------------------------------------------------

def mount_directory(server,
                    name,
                    host_dir,
                    container_dir):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo 'lxc.mount.entry = "
        f"{host_dir} {container_dir} none bind,create=dir 0 0' "
        f"| sudo tee -a /var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Mount entfernen
# -------------------------------------------------

def unmount(server,
            name,
            path):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo sed -i '\\|{path}|d' "
        f"/var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Mounts anzeigen
# -------------------------------------------------

def mounts(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"grep '^lxc.mount.entry' "
        f"/var/lib/lxc/{name}/config"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container Log
# -------------------------------------------------

def log(server,
        name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /var/log/lxc/{name}.log"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Live Log
# -------------------------------------------------

def log_follow(server,
               name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"tail -f /var/log/lxc/{name}.log"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Prozessliste im Container
# -------------------------------------------------

def processes(server,
              name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- ps aux"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Container Statistiken
# -------------------------------------------------

def stats(server,
          name):

    return {
        "status": status(server, name),
        "pid": pid(server, name),
        "ip": ip(server, name),
        "cpu": cpu(server, name),
        "memory": memory(server, name),
        "mounts": mounts(server, name)
    }

# -------------------------------------------------
# CPU Limit setzen
# -------------------------------------------------

def set_cpu_limit(server,
                  name,
                  cores):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} cpuset.cpus {cores}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# CPU Shares setzen
# -------------------------------------------------

def set_cpu_shares(server,
                   name,
                   shares):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} cpu.shares {shares}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RAM Limit setzen
# -------------------------------------------------

def set_memory_limit(server,
                     name,
                     memory):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} memory.limit_in_bytes {memory}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Swap Limit setzen
# -------------------------------------------------

def set_swap_limit(server,
                   name,
                   swap):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} memory.memsw.limit_in_bytes {swap}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# PID Limit
# -------------------------------------------------

def set_pid_limit(server,
                  name,
                  limit):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} pids.max {limit}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Block-I/O Gewicht
# -------------------------------------------------

def set_io_weight(server,
                  name,
                  weight):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-cgroup -n {name} blkio.weight {weight}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Netzwerkinterfaces
# -------------------------------------------------

def network(server,
            name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- ip addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Routingtabelle
# -------------------------------------------------

def routes(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- ip route"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Hostname
# -------------------------------------------------

def hostname(server,
             name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- hostname"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# DNS
# -------------------------------------------------

def dns(server,
        name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- cat /etc/resolv.conf"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Betriebssystem
# -------------------------------------------------

def os(server,
       name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- cat /etc/os-release"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Kernel
# -------------------------------------------------

def kernel(server,
           name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- uname -r"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Festplatten
# -------------------------------------------------

def disks(server,
          name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- lsblk"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Dateisystem
# -------------------------------------------------

def filesystem(server,
               name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- df -h"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Netzwerkkonfiguration ändern
# -------------------------------------------------

def set_ip(server,
           name,
           interface,
           ip,
           prefix):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- "
        f"ip addr add {ip}/{prefix} dev {interface}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gateway setzen
# -------------------------------------------------

def set_gateway(server,
                name,
                gateway):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-attach -n {name} -- "
        f"ip route replace default via {gateway}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Ressourcenübersicht
# -------------------------------------------------

def resources(server,
              name):

    return {
        "cpu": cpu(server, name),
        "memory": memory(server, name),
        "filesystem": filesystem(server, name),
        "network": network(server, name),
        "routes": routes(server, name),
        "hostname": hostname(server, name),
        "dns": dns(server, name)
    }

# -------------------------------------------------
# Verfügbare Templates
# -------------------------------------------------

def templates(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ls /usr/share/lxc/templates"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Downloadbare Images (distrobuilder)
# -------------------------------------------------

def images(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lxc-create -t download --help"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Debian Container erstellen
# -------------------------------------------------

def create_debian(server,
                  name,
                  release="bookworm",
                  arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist debian "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Ubuntu Container erstellen
# -------------------------------------------------

def create_ubuntu(server,
                  name,
                  release="24.04",
                  arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist ubuntu "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rocky Linux Container
# -------------------------------------------------

def create_rocky(server,
                 name,
                 release="9",
                 arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist rocky "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# openSUSE Leap
# -------------------------------------------------

def create_opensuse(server,
                    name,
                    release="15.6",
                    arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist opensuse "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alpine Linux
# -------------------------------------------------

def create_alpine(server,
                  name,
                  release="3.22",
                  arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist alpine "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Arch Linux
# -------------------------------------------------

def create_arch(server,
                name,
                release="current",
                arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist archlinux "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Fedora
# -------------------------------------------------

def create_fedora(server,
                  name,
                  release="42",
                  arch="amd64"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo lxc-create "
        f"-n {name} "
        f"-t download -- "
        f"--dist fedora "
        f"--release {release} "
        f"--arch {arch}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup erstellen
# -------------------------------------------------

def backup(server,
           name,
           destination):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo tar -czpf "
        f"{destination}/{name}.tar.gz "
        f"/var/lib/lxc/{name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup wiederherstellen
# -------------------------------------------------

def restore(server,
            archive):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo tar -xzpf {archive} "
        f"-C /var/lib/lxc/"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Backups anzeigen
# -------------------------------------------------

def backups(server,
            directory):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ls -lh {directory}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# LXC Version
# -------------------------------------------------

def version(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lxc-info --version"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Host Informationen
# -------------------------------------------------

def host_info(server):

    return {
        "version": version(server),
        "templates": templates(server),
        "containers": names(server)
    }


# -------------------------------------------------
# Gesamtübersicht
# -------------------------------------------------

def overview(server):

    return {
        "containers": list(server),
        "templates": templates(server),
        "host": host_info(server)
    }