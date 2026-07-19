from ssh.client import SSHClient


# -------------------------------------------------
# Alle IP-Adressen
# -------------------------------------------------

def ip_addr(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Kurze Übersicht
# -------------------------------------------------

def ip_addr_brief(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip -br addr"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Einzelnes Interface
# -------------------------------------------------

def interface(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ip addr show {interface}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Interfaces
# -------------------------------------------------

def interfaces(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ls /sys/class/net"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Interface aktivieren
# -------------------------------------------------

def interface_up(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface deaktivieren
# -------------------------------------------------

def interface_down(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} down"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface Status
# -------------------------------------------------

def interface_status(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /sys/class/net/{interface}/operstate"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Interface Informationen
# -------------------------------------------------

def interface_info(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ip -d link show {interface}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Interface umbenennen
# -------------------------------------------------

def rename_interface(server, old_name, new_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {old_name} down && "
        f"sudo ip link set {old_name} name {new_name} && "
        f"sudo ip link set {new_name} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# MTU anzeigen
# -------------------------------------------------

def mtu(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /sys/class/net/{interface}/mtu"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# MTU ändern
# -------------------------------------------------

def set_mtu(server, interface, mtu):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set dev {interface} mtu {mtu}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# MAC-Adresse
# -------------------------------------------------

def mac(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /sys/class/net/{interface}/address"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# MAC-Adresse ändern
# -------------------------------------------------

def set_mac(server, interface, mac):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set dev {interface} address {mac}"
    )

    ssh.close()

    return result


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

def gateway(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip route | grep default"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Gateway ändern
# -------------------------------------------------

def set_gateway(server, gateway):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip route replace default via {gateway}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# IPv4 Adresse setzen
# -------------------------------------------------

def set_ipv4(server, interface, address, prefix):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip addr flush dev {interface} && "
        f"sudo ip addr add {address}/{prefix} dev {interface}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# DHCP aktivieren
# -------------------------------------------------

def dhcp(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo dhclient {interface}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Link Informationen
# -------------------------------------------------

def links(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "ip link"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Statistiken
# -------------------------------------------------

def statistics(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ip -s link show {interface}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Interface Geschwindigkeit
# -------------------------------------------------

def speed(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ethtool {interface} | grep Speed"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Duplex
# -------------------------------------------------

def duplex(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ethtool {interface} | grep Duplex"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Link erkannt?
# -------------------------------------------------

def carrier(server, interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /sys/class/net/{interface}/carrier"
    )

    ssh.close()

    return result["stdout"] == "1"

# -------------------------------------------------
# Bridges anzeigen
# -------------------------------------------------

def bridges(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "bridge link"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Bridge Übersicht
# -------------------------------------------------

def bridge_show(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "bridge link show"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Bridge erstellen
# -------------------------------------------------

def create_bridge(server, bridge):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link add name {bridge} type bridge && "
        f"sudo ip link set {bridge} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bridge löschen
# -------------------------------------------------

def delete_bridge(server, bridge):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {bridge} down && "
        f"sudo ip link delete {bridge} type bridge"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface zu Bridge hinzufügen
# -------------------------------------------------

def add_interface_to_bridge(server,
                            interface,
                            bridge):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} master {bridge}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface aus Bridge entfernen
# -------------------------------------------------

def remove_interface_from_bridge(server,
                                 interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} nomaster"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bridge Informationen
# -------------------------------------------------

def bridge_info(server,
                bridge):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"bridge link show master {bridge}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# VLANs anzeigen
# -------------------------------------------------

def vlan_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "bridge vlan show"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# VLAN eines Interfaces
# -------------------------------------------------

def vlan_interface(server,
                   interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"bridge vlan show dev {interface}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# VLAN Interface erstellen
# -------------------------------------------------

def create_vlan(server,
                interface,
                vlan):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link add link {interface} "
        f"name {interface}.{vlan} "
        f"type vlan id {vlan} && "
        f"sudo ip link set {interface}.{vlan} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN löschen
# -------------------------------------------------

def delete_vlan(server,
                interface,
                vlan):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link delete {interface}.{vlan}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN IP setzen
# -------------------------------------------------

def vlan_set_ip(server,
                interface,
                vlan,
                ip,
                prefix):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip addr add "
        f"{ip}/{prefix} "
        f"dev {interface}.{vlan}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN IP entfernen
# -------------------------------------------------

def vlan_remove_ip(server,
                   interface,
                   vlan,
                   ip,
                   prefix):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip addr del "
        f"{ip}/{prefix} "
        f"dev {interface}.{vlan}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN aktivieren
# -------------------------------------------------

def vlan_up(server,
            interface,
            vlan):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface}.{vlan} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN deaktivieren
# -------------------------------------------------

def vlan_down(server,
              interface,
              vlan):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface}.{vlan} down"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN Bridge hinzufügen
# -------------------------------------------------

def vlan_add_to_bridge(server,
                       interface,
                       vlan,
                       bridge):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set "
        f"{interface}.{vlan} "
        f"master {bridge}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# VLAN Bridge entfernen
# -------------------------------------------------

def vlan_remove_from_bridge(server,
                            interface,
                            vlan):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set "
        f"{interface}.{vlan} "
        f"nomaster"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bridge Forwarding Database
# -------------------------------------------------

def bridge_fdb(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "bridge fdb show"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Bridge Multicast
# -------------------------------------------------

def bridge_mdb(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "bridge mdb show"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Bonding anzeigen
# -------------------------------------------------

def bonds(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cat /proc/net/bonding/* 2>/dev/null"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Bond erstellen
# -------------------------------------------------

def create_bond(server,
                bond="bond0",
                mode="active-backup"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link add {bond} type bond mode {mode} && "
        f"sudo ip link set {bond} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bond löschen
# -------------------------------------------------

def delete_bond(server,
                bond):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link delete {bond}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface zum Bond hinzufügen
# -------------------------------------------------

def bond_add_interface(server,
                       bond,
                       interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} down && "
        f"sudo ip link set {interface} master {bond} && "
        f"sudo ip link set {interface} up"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Interface aus Bond entfernen
# -------------------------------------------------

def bond_remove_interface(server,
                          interface):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip link set {interface} nomaster"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bond Modus ändern
# -------------------------------------------------

def bond_mode(server,
              bond,
              mode):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo {mode} | sudo tee /sys/class/net/{bond}/bonding/mode"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Bond Informationen
# -------------------------------------------------

def bond_info(server,
              bond):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"cat /proc/net/bonding/{bond}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# DNS anzeigen
# -------------------------------------------------

def dns(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cat /etc/resolv.conf"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Nameserver setzen
# -------------------------------------------------

def set_dns(server,
            dns1,
            dns2=None):

    ssh = SSHClient(server)

    ssh.connect()

    command = (
        f"echo 'nameserver {dns1}' | sudo tee /etc/resolv.conf"
    )

    if dns2:
        command += (
            f" && echo 'nameserver {dns2}' | "
            f"sudo tee -a /etc/resolv.conf"
        )

    result = ssh.execute(command)

    ssh.close()

    return result


# -------------------------------------------------
# Suchdomäne setzen
# -------------------------------------------------

def set_search_domain(server,
                      domain):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo 'search {domain}' | "
        f"sudo tee -a /etc/resolv.conf"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hostname anzeigen
# -------------------------------------------------

def hostname(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "hostname"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Hostname ändern
# -------------------------------------------------

def set_hostname(server,
                 hostname):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo hostnamectl set-hostname {hostname}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hosts-Datei
# -------------------------------------------------

def hosts(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "cat /etc/hosts"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Eintrag zu /etc/hosts hinzufügen
# -------------------------------------------------

def hosts_add(server,
              ip,
              hostname):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"echo '{ip} {hostname}' | "
        f"sudo tee -a /etc/hosts"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Resolver Status
# -------------------------------------------------

def resolver(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "resolvectl status"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Gateway ändern
# -------------------------------------------------

def change_gateway(server,
                   gateway):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo ip route replace default via {gateway}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gateway entfernen
# -------------------------------------------------

def remove_gateway(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo ip route del default"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Netzwerk zusammenfassen
# -------------------------------------------------

def info(server):

    return {
        "hostname": hostname(server),
        "interfaces": interfaces(server),
        "routes": routes(server),
        "gateway": gateway(server),
        "dns": dns(server),
        "bridges": bridges(server),
        "vlans": vlan_list(server),
        "bonds": bonds(server)
    }