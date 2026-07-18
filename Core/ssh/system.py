from ssh.client import SSHClient


# -------------------------------------------------
# Hostname
# -------------------------------------------------

def hostname(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("hostname")

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Betriebssystem
# -------------------------------------------------

def os(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "source /etc/os-release && echo \"$PRETTY_NAME\""
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Kernel
# -------------------------------------------------

def kernel(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("uname -r")

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Uptime
# -------------------------------------------------

def uptime(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "uptime -p"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Aktuelles Datum
# -------------------------------------------------

def date(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "date '+%d.%m.%Y %H:%M:%S'"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Zeitzone
# -------------------------------------------------

def timezone(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "timedatectl show --property=Timezone --value"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Laufzeit in Sekunden
# -------------------------------------------------

def uptime_seconds(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cut -d' ' -f1 /proc/uptime"
    )

    ssh.close()

    return float(result["stdout"])


# -------------------------------------------------
# Bootzeit
# -------------------------------------------------

def boot_time(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "who -b | awk '{print $3\" \"$4}'"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Eingeloggte Benutzer
# -------------------------------------------------

def logged_users(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "who"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Anzahl Benutzer
# -------------------------------------------------

def logged_users_count(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "who | wc -l"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# Host-ID
# -------------------------------------------------

def hostid(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "hostid"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Maschinen-ID
# -------------------------------------------------

def machine_id(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cat /etc/machine-id"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Architektur
# -------------------------------------------------

def architecture(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "uname -m"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Hostnamectl
# -------------------------------------------------

def hostnamectl(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "hostnamectl"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# CPU Kerne
# -------------------------------------------------

def cpu(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute("nproc")

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# CPU Modell
# -------------------------------------------------

def cpu_model(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lscpu | grep 'Model name' | cut -d':' -f2"
    )

    ssh.close()

    return result["stdout"].strip()


# -------------------------------------------------
# CPU Auslastung
# -------------------------------------------------

def cpu_usage(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "top -bn1 | grep 'Cpu(s)' | awk '{print 100-$8}'"
    )

    ssh.close()

    return float(result["stdout"])


# -------------------------------------------------
# CPU Frequenz
# -------------------------------------------------

def cpu_frequency(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lscpu | grep 'CPU MHz' | awk '{print $3}'"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# RAM
# -------------------------------------------------

def memory(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -h"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# RAM Gesamt
# -------------------------------------------------

def memory_total(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -b | awk '/Mem:/ {print $2}'"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# RAM Belegt
# -------------------------------------------------

def memory_used(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -b | awk '/Mem:/ {print $3}'"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# RAM Frei
# -------------------------------------------------

def memory_free(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -b | awk '/Mem:/ {print $4}'"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# RAM Auslastung
# -------------------------------------------------

def memory_usage(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free | awk '/Mem:/ {printf \"%.2f\", $3/$2*100}'"
    )

    ssh.close()

    return float(result["stdout"])


# -------------------------------------------------
# Swap
# -------------------------------------------------

def swap(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -h | grep Swap"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Swap Gesamt
# -------------------------------------------------

def swap_total(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -b | awk '/Swap:/ {print $2}'"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# Swap Belegt
# -------------------------------------------------

def swap_used(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free -b | awk '/Swap:/ {print $3}'"
    )

    ssh.close()

    return int(result["stdout"])


# -------------------------------------------------
# Swap Auslastung
# -------------------------------------------------

def swap_usage(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "free | awk '/Swap:/ { if($2==0) print 0; else printf \"%.2f\", $3/$2*100 }'"
    )

    ssh.close()

    return float(result["stdout"])


# -------------------------------------------------
# System Load
# -------------------------------------------------

def load(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cat /proc/loadavg"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Temperatur (lm-sensors)
# -------------------------------------------------

def temperature(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sensors 2>/dev/null"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Festplattenbelegung (df -h)
# -------------------------------------------------

def disk_usage(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "df -h"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Blockgeräte (lsblk)
# -------------------------------------------------

def lsblk(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Dateisysteme
# -------------------------------------------------

def filesystems(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "findmnt"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Mountpoints
# -------------------------------------------------

def mounts(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "mount"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# ZFS Pools
# -------------------------------------------------

def zpools(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool list"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# ZFS Status
# -------------------------------------------------

def zpool_status(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool status"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# ZFS Dateisysteme
# -------------------------------------------------

def zfs_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs list"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Netzwerkinterfaces
# -------------------------------------------------

def network_interfaces(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -br link"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# IP-Adressen
# -------------------------------------------------

def ip_addresses(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -br addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# IPv4-Adressen
# -------------------------------------------------

def ipv4_addresses(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -4 addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# IPv6-Adressen
# -------------------------------------------------

def ipv6_addresses(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -6 addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Routingtabelle
# -------------------------------------------------

def routes(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip route"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Standardgateway
# -------------------------------------------------

def default_gateway(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip route | grep default"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# DNS Server
# -------------------------------------------------

def dns_servers(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "grep nameserver /etc/resolv.conf"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Hostname auflösen
# -------------------------------------------------

def hostname_lookup(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "hostname -f"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Offene Ports
# -------------------------------------------------

def listening_ports(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ss -tuln"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Netzwerkstatistik
# -------------------------------------------------

def network_statistics(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -s link"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Laufende Prozesse
# -------------------------------------------------

def running_processes(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Top CPU Prozesse
# -------------------------------------------------

def top_cpu_processes(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -20"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Top RAM Prozesse
# -------------------------------------------------

def top_memory_processes(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ps -eo pid,user,%cpu,%mem,comm --sort=-%mem | head -20"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Dienste
# -------------------------------------------------

def services(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "systemctl list-units --type=service --all --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Laufende Dienste
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
# Service Status
# -------------------------------------------------

def service_status(server, service):

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

def start_service(server, service):

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

def stop_service(server, service):

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

def restart_service(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl restart {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Service aktivieren
# -------------------------------------------------

def enable_service(server, service):

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

def disable_service(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo systemctl disable {service}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Journal (letzte 100 Zeilen)
# -------------------------------------------------

def journal(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "journalctl -n 100 --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Journal eines Dienstes
# -------------------------------------------------

def service_journal(server, service):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"journalctl -u {service} -n 100 --no-pager"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Dmesg
# -------------------------------------------------

def dmesg(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "dmesg | tail -100"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Reboot
# -------------------------------------------------

def reboot(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo reboot"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Shutdown
# -------------------------------------------------

def shutdown(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo shutdown now"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Poweroff
# -------------------------------------------------

def poweroff(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo poweroff"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hostname ändern
# -------------------------------------------------

def set_hostname(server, hostname):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo hostnamectl set-hostname {hostname}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Zeitzone ändern
# -------------------------------------------------

def set_timezone(server, timezone):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo timedatectl set-timezone {timezone}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# System aktualisieren (Debian/Ubuntu)
# -------------------------------------------------

def apt_update(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo apt update && sudo apt upgrade -y"
    )

    ssh.close()

    return result


# -------------------------------------------------
# System aktualisieren (Rocky/Fedora)
# -------------------------------------------------

def dnf_update(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo dnf upgrade -y"
    )

    ssh.close()

    return result


# -------------------------------------------------
# System aktualisieren (openSUSE)
# -------------------------------------------------

def zypper_update(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zypper update -y"
    )

    ssh.close()

    return result