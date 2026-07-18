from ssh.client import SSHClient


# -------------------------------------------------
# ZFS Pool Liste
# -------------------------------------------------

def zpool_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool list -H -o name,size,alloc,free,frag,cap,health"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# ZFS Pool Status
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
# Status eines Pools
# -------------------------------------------------

def zpool_status_pool(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Health
# -------------------------------------------------

def zpool_health(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o health {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Größe
# -------------------------------------------------

def zpool_size(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o size {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Belegter Speicher
# -------------------------------------------------

def zpool_allocated(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o alloc {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Freier Speicher
# -------------------------------------------------

def zpool_free(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o free {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Auslastung
# -------------------------------------------------

def zpool_capacity(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o cap {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Fragmentierung
# -------------------------------------------------

def zpool_fragmentation(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list -H -o frag {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Expandiert?
# -------------------------------------------------

def zpool_expand_size(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get -H autoexpand {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Version
# -------------------------------------------------

def zpool_version(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool upgrade"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# ZFS Version
# -------------------------------------------------

def zfs_version(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs version"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Pools als Python-Liste
# -------------------------------------------------

def zpool_names(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool list -H -o name"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Existiert Pool?
# -------------------------------------------------

def zpool_exists(server, pool):

    pools = zpool_names(server)

    return pool in pools


# -------------------------------------------------
# Anzahl Pools
# -------------------------------------------------

def zpool_count(server):

    return len(
        zpool_names(server)
    )