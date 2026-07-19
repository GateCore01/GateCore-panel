from ssh.client import SSHClient


# -------------------------------------------------
# Alle laufenden Services
# -------------------------------------------------

def list_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-units --type=service --all --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Installierte Services
# -------------------------------------------------

def list_unit_files(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-unit-files --type=service --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Status eines Services
# -------------------------------------------------

def status(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl status {service} --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service starten
# -------------------------------------------------

def start(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl start {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service stoppen
# -------------------------------------------------

def stop(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl stop {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service neustarten
# -------------------------------------------------

def restart(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl restart {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service neu laden
# -------------------------------------------------

def reload(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl reload {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Reload oder Restart
# -------------------------------------------------

def reload_or_restart(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl reload-or-restart {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Läuft der Service?
# -------------------------------------------------

def is_active(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl is-active {service}"
    )

    ssh.close()

    return result["stdout"] == "active"


# -------------------------------------------------
# Ist der Service aktiviert?
# -------------------------------------------------

def is_enabled(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl is-enabled {service}"
    )

    ssh.close()

    return result["stdout"] == "enabled"


# -------------------------------------------------
# Service gestartet?
# -------------------------------------------------

def is_running(server, service):

    return is_active(server, service)


# -------------------------------------------------
# Aktive Services
# -------------------------------------------------

def active_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-units --type=service --state=running --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Gestoppte Services
# -------------------------------------------------

def inactive_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-units --type=service --state=inactive --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Beschreibung
# -------------------------------------------------

def description(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} --property=Description"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Typ
# -------------------------------------------------

def service_type(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} --property=Type"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Datei
# -------------------------------------------------

def service_file(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} --property=FragmentPath"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Service aktivieren
# -------------------------------------------------

def enable(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl enable {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service deaktivieren
# -------------------------------------------------

def disable(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl disable {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service maskieren
# -------------------------------------------------

def mask(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl mask {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service demaskieren
# -------------------------------------------------

def unmask(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl unmask {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Systemd neu laden
# -------------------------------------------------

def daemon_reload(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo systemctl daemon-reload"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Systemd neu ausführen
# -------------------------------------------------

def daemon_reexec(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo systemctl daemon-reexec"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Fehlgeschlagene Services
# -------------------------------------------------

def failed_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl --failed --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Laufende Services
# -------------------------------------------------

def running_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-units --type=service --state=running --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service existiert?
# -------------------------------------------------

def service_exists(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl list-unit-files | grep '^{service}'"
    )

    ssh.close()

    return result["stdout"] != ""


# -------------------------------------------------
# Aktivierte Services
# -------------------------------------------------

def enabled_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-unit-files --state=enabled --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Deaktivierte Services
# -------------------------------------------------

def disabled_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-unit-files --state=disabled --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Maskierte Services
# -------------------------------------------------

def masked_services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-unit-files --state=masked --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service aktivieren + starten
# -------------------------------------------------

def enable_and_start(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl enable --now {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service stoppen + deaktivieren
# -------------------------------------------------

def disable_and_stop(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl disable --now {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service Konfiguration anzeigen
# -------------------------------------------------

def cat(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl cat {service}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Eigenschaften
# -------------------------------------------------

def properties(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service laden?
# -------------------------------------------------

def is_loaded(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} --property=LoadState"
    )

    ssh.close()

    return "loaded" in result["stdout"]


# -------------------------------------------------
# Boot-Zeit anzeigen
# -------------------------------------------------

def boot_time(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemd-analyze"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Journal eines Services
# -------------------------------------------------

def logs(server,
         service,
         lines=100):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        f"-n {lines} --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Logs verfolgen
# -------------------------------------------------

def logs_follow(server,
                service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} -f"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Logs seit Zeitpunkt
# -------------------------------------------------

def logs_since(server,
               service,
               since):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        f'--since "{since}" '
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Logs bis Zeitpunkt
# -------------------------------------------------

def logs_until(server,
               service,
               until):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        f'--until "{until}" '
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Letzter Boot
# -------------------------------------------------

def last_boot_logs(server,
                   service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        "-b --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service PID
# -------------------------------------------------

def service_pid(server,
                service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} "
        "--property=MainPID --value"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Laufzeit
# -------------------------------------------------

def service_uptime(server,
                   service):

    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return "Service läuft nicht"

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ps -p {pid} -o etime="
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Speicherverbrauch
# -------------------------------------------------

def memory_usage(server,
                 service):

    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ps -p {pid} -o rss="
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# CPU-Auslastung
# -------------------------------------------------

def cpu_usage(server,
              service):

    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ps -p {pid} -o %cpu="
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Startzeit
# -------------------------------------------------

def start_time(server,
               service):

    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ps -p {pid} -o lstart="
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Benutzer
# -------------------------------------------------

def service_user(server,
                 service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"systemctl show {service} "
        "--property=User"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Letzte 24 Stunden
# -------------------------------------------------

def logs_last_24h(server,
                  service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        "--since '24 hours ago' "
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Fehlerlogs
# -------------------------------------------------

def error_logs(server,
               service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        "-p err "
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Warnungen
# -------------------------------------------------

def warning_logs(server,
                 service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        "-p warning "
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Nur heutige Logs
# -------------------------------------------------

def today_logs(server,
               service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} "
        "--since today "
        "--no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Service Informationen
# -------------------------------------------------

def service_info(server,
                 service):

    return {
        "status": status(server, service),
        "enabled": is_enabled(server, service),
        "active": is_active(server, service),
        "pid": service_pid(server, service),
        "uptime": service_uptime(server, service),
        "cpu": cpu_usage(server, service),
        "memory": memory_usage(server, service),
        "logs": logs(server, service, 50)
    }