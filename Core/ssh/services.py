from typing import Any

from ssh.commands import run


def _run_text(server: dict[str, Any], command: str) -> str:
    """Führt einen SSH-Befehl aus und liefert stdout oder stderr als Text."""
    result = run(server, command)
    return result.get("stdout") or result.get("stderr", "")


def _run_action(server: dict[str, Any], command: str) -> dict[str, str]:
    """Führt einen SSH-Befehl aus und gibt das Ergebnis-Objekt zurück."""
    return run(server, command)


# -------------------------------------------------
# Alle laufenden Services
# -------------------------------------------------

def list_services(server):
    return _run_text(server, "systemctl list-units --type=service --all --no-pager")


# -------------------------------------------------
# Installierte Services
# -------------------------------------------------

def list_unit_files(server):
    return _run_text(server, "systemctl list-unit-files --type=service --no-pager")


# -------------------------------------------------
# Status eines Services
# -------------------------------------------------

def status(server, service):
    return _run_text(server, f"systemctl status {service} --no-pager")


# -------------------------------------------------
# Service starten
# -------------------------------------------------

def start(server, service):
    return _run_action(server, f"sudo systemctl start {service}")


# -------------------------------------------------
# Service stoppen
# -------------------------------------------------

def stop(server, service):
    return _run_action(server, f"sudo systemctl stop {service}")


# -------------------------------------------------
# Service neustarten
# -------------------------------------------------

def restart(server, service):
    return _run_action(server, f"sudo systemctl restart {service}")


# -------------------------------------------------
# Service neu laden
# -------------------------------------------------

def reload(server, service):
    return _run_action(server, f"sudo systemctl reload {service}")


# -------------------------------------------------
# Reload oder Restart
# -------------------------------------------------

def reload_or_restart(server, service):
    return _run_action(server, f"sudo systemctl reload-or-restart {service}")


# -------------------------------------------------
# Läuft der Service?
# -------------------------------------------------

def is_active(server, service):
    result = _run_action(server, f"systemctl is-active {service}")
    return result.get("stdout", "").strip() == "active"


# -------------------------------------------------
# Ist der Service aktiviert?
# -------------------------------------------------

def is_enabled(server, service):
    result = _run_action(server, f"systemctl is-enabled {service}")
    return result.get("stdout", "").strip() == "enabled"


# -------------------------------------------------
# Service gestartet?
# -------------------------------------------------

def is_running(server, service):
    return is_active(server, service)


# -------------------------------------------------
# Aktive Services
# -------------------------------------------------

def active_services(server):
    return _run_text(server, "systemctl list-units --type=service --state=running --no-pager")


# -------------------------------------------------
# Gestoppte Services
# -------------------------------------------------

def inactive_services(server):
    return _run_text(server, "systemctl list-units --type=service --state=inactive --no-pager")


# -------------------------------------------------
# Service Beschreibung
# -------------------------------------------------

def description(server, service):
    return _run_text(server, f"systemctl show {service} --property=Description")


# -------------------------------------------------
# Service Typ
# -------------------------------------------------

def service_type(server, service):
    return _run_text(server, f"systemctl show {service} --property=Type")


# -------------------------------------------------
# Service Datei
# -------------------------------------------------

def service_file(server, service):
    return _run_text(server, f"systemctl show {service} --property=FragmentPath")


# -------------------------------------------------
# Service aktivieren
# -------------------------------------------------

def enable(server, service):
    return _run_action(server, f"sudo systemctl enable {service}")


# -------------------------------------------------
# Service deaktivieren
# -------------------------------------------------

def disable(server, service):
    return _run_action(server, f"sudo systemctl disable {service}")


# -------------------------------------------------
# Service maskieren
# -------------------------------------------------

def mask(server, service):
    return _run_action(server, f"sudo systemctl mask {service}")


# -------------------------------------------------
# Service demaskieren
# -------------------------------------------------

def unmask(server, service):
    return _run_action(server, f"sudo systemctl unmask {service}")


# -------------------------------------------------
# Systemd neu laden
# -------------------------------------------------

def daemon_reload(server):
    return _run_action(server, "sudo systemctl daemon-reload")


# -------------------------------------------------
# Systemd neu ausführen
# -------------------------------------------------

def daemon_reexec(server):
    return _run_action(server, "sudo systemctl daemon-reexec")


# -------------------------------------------------
# Fehlgeschlagene Services
# -------------------------------------------------

def failed_services(server):
    return _run_text(server, "systemctl --failed --no-pager")


# -------------------------------------------------
# Laufende Services
# -------------------------------------------------

def running_services(server):
    return _run_text(server, "systemctl list-units --type=service --state=running --no-pager")


# -------------------------------------------------
# Service existiert?
# -------------------------------------------------

def service_exists(server, service):
    result = _run_action(server, f"systemctl list-unit-files | grep '^{service}'")
    return result.get("stdout", "") != ""


# -------------------------------------------------
# Aktivierte Services
# -------------------------------------------------

def enabled_services(server):
    return _run_text(server, "systemctl list-unit-files --state=enabled --no-pager")


# -------------------------------------------------
# Deaktivierte Services
# -------------------------------------------------

def disabled_services(server):
    return _run_text(server, "systemctl list-unit-files --state=disabled --no-pager")


# -------------------------------------------------
# Maskierte Services
# -------------------------------------------------

def masked_services(server):
    return _run_text(server, "systemctl list-unit-files --state=masked --no-pager")


# -------------------------------------------------
# Service aktivieren + starten
# -------------------------------------------------

def enable_and_start(server, service):
    return _run_action(server, f"sudo systemctl enable --now {service}")


# -------------------------------------------------
# Service stoppen + deaktivieren
# -------------------------------------------------

def disable_and_stop(server, service):
    return _run_action(server, f"sudo systemctl disable --now {service}")


# -------------------------------------------------
# Service Konfiguration anzeigen
# -------------------------------------------------

def cat(server, service):
    return _run_text(server, f"systemctl cat {service}")


# -------------------------------------------------
# Service Eigenschaften
# -------------------------------------------------

def properties(server, service):
    return _run_text(server, f"systemctl show {service}")


# -------------------------------------------------
# Service laden?
# -------------------------------------------------

def is_loaded(server, service):
    result = _run_action(server, f"systemctl show {service} --property=LoadState")
    return "loaded" in result.get("stdout", "")


# -------------------------------------------------
# Boot-Zeit anzeigen
# -------------------------------------------------

def boot_time(server):
    return _run_text(server, "systemd-analyze")


# -------------------------------------------------
# Journal eines Services
# -------------------------------------------------

def logs(server, service, lines=100):
    return _run_text(server, f"journalctl -u {service} -n {lines} --no-pager")


# -------------------------------------------------
# Logs verfolgen
# -------------------------------------------------

def logs_follow(server, service):
    return _run_action(server, f"journalctl -u {service} -f")


# -------------------------------------------------
# Logs seit Zeitpunkt
# -------------------------------------------------

def logs_since(server, service, since):
    return _run_text(server, f"journalctl -u {service} --since \"{since}\" --no-pager")


# -------------------------------------------------
# Logs bis Zeitpunkt
# -------------------------------------------------

def logs_until(server, service, until):
    return _run_text(server, f"journalctl -u {service} --until \"{until}\" --no-pager")


# -------------------------------------------------
# Letzter Boot
# -------------------------------------------------

def last_boot_logs(server, service):
    return _run_text(server, f"journalctl -u {service} -b --no-pager")


# -------------------------------------------------
# Service PID
# -------------------------------------------------

def service_pid(server, service):
    return _run_text(server, f"systemctl show {service} --property=MainPID --value")


# -------------------------------------------------
# Laufzeit
# -------------------------------------------------

def service_uptime(server, service):
    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return "Service läuft nicht"

    return _run_text(server, f"ps -p {pid} -o etime=")


# -------------------------------------------------
# Speicherverbrauch
# -------------------------------------------------

def memory_usage(server, service):
    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    return _run_text(server, f"ps -p {pid} -o rss=")


# -------------------------------------------------
# CPU-Auslastung
# -------------------------------------------------

def cpu_usage(server, service):
    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    return _run_text(server, f"ps -p {pid} -o %cpu=")


# -------------------------------------------------
# Startzeit
# -------------------------------------------------

def start_time(server, service):
    pid = service_pid(server, service)

    if pid == "0" or pid == "":
        return ""

    return _run_text(server, f"ps -p {pid} -o lstart=")


# -------------------------------------------------
# Service Benutzer
# -------------------------------------------------

def service_user(server, service):
    return _run_text(server, f"systemctl show {service} --property=User")


# -------------------------------------------------
# Letzte 24 Stunden
# -------------------------------------------------

def logs_last_24h(server, service):
    return _run_text(server, f"journalctl -u {service} --since '24 hours ago' --no-pager")


# -------------------------------------------------
# Fehlerlogs
# -------------------------------------------------

def error_logs(server, service):
    return _run_text(server, f"journalctl -u {service} -p err --no-pager")


# -------------------------------------------------
# Warnungen
# -------------------------------------------------

def warning_logs(server, service):
    return _run_text(server, f"journalctl -u {service} -p warning --no-pager")


# -------------------------------------------------
# Nur heutige Logs
# -------------------------------------------------

def today_logs(server, service):
    return _run_text(server, f"journalctl -u {service} --since today --no-pager")


# -------------------------------------------------
# Service Informationen
# -------------------------------------------------

def service_info(server, service):
    return {
        "status": status(server, service),
        "enabled": is_enabled(server, service),
        "active": is_active(server, service),
        "pid": service_pid(server, service),
        "uptime": service_uptime(server, service),
        "cpu": cpu_usage(server, service),
        "memory": memory_usage(server, service),
        "logs": logs(server, service, 50),
    }
