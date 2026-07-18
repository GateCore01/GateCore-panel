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
    
# -------------------------------------------------
# Fehler eines Pools
# -------------------------------------------------

def zpool_errors(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep errors"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# I/O Statistik aller Pools
# -------------------------------------------------

def zpool_iostat(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool iostat"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# I/O Statistik eines Pools
# -------------------------------------------------

def zpool_iostat_pool(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool iostat {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# I/O Statistik (Live)
# -------------------------------------------------

def zpool_iostat_live(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"timeout 5 zpool iostat {pool} 1"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Geräte eines Pools
# -------------------------------------------------

def zpool_devices(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool GUID
# -------------------------------------------------

def zpool_guid(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get -H guid {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Features
# -------------------------------------------------

def zpool_features(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get all {pool} | grep feature@"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Scanstatus
# -------------------------------------------------

def zpool_scan_status(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep scan"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Läuft ein Resilver?
# -------------------------------------------------

def zpool_resilver(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep resilver"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Letzte ZFS Events
# -------------------------------------------------

def zpool_events(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool events -v | tail -100"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Verlauf
# -------------------------------------------------

def zpool_history(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zpool history"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Verlauf eines Pools
# -------------------------------------------------

def zpool_history_pool(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool history {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Properties
# -------------------------------------------------

def zpool_properties(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get all {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool Statistik
# -------------------------------------------------

def zpool_statistics(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool list {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Defekte Geräte
# -------------------------------------------------

def zpool_faulted_devices(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep FAULTED"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Offline Geräte
# -------------------------------------------------

def zpool_offline_devices(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep OFFLINE"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Degradierte Geräte
# -------------------------------------------------

def zpool_degraded_devices(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep DEGRADED"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# ZFS Mirror erstellen
# -------------------------------------------------

def zpool_create_mirror(server, pool, disk1, disk2):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool create {pool} mirror {disk1} {disk2}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RAIDZ1 erstellen
# -------------------------------------------------

def zpool_create_raidz1(server, pool, disks):

    ssh = SSHClient(server)

    ssh.connect()

    disk_list = " ".join(disks)

    result = ssh.execute(
        f"sudo zpool create {pool} raidz {disk_list}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# RAIDZ2 erstellen
# -------------------------------------------------

def zpool_create_raidz2(server, pool, disks):

    ssh = SSHClient(server)

    ssh.connect()

    disk_list = " ".join(disks)

    result = ssh.execute(
        f"sudo zpool create {pool} raidz2 {disk_list}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Stripe erstellen
# -------------------------------------------------

def zpool_create_stripe(server, pool, disks):

    ssh = SSHClient(server)

    ssh.connect()

    disk_list = " ".join(disks)

    result = ssh.execute(
        f"sudo zpool create {pool} {disk_list}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool löschen
# -------------------------------------------------

def zpool_destroy(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool destroy {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool exportieren
# -------------------------------------------------

def zpool_export(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool export {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle exportierten Pools anzeigen
# -------------------------------------------------

def zpool_import_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zpool import"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool importieren
# -------------------------------------------------

def zpool_import(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool import {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool unter anderem Namen importieren
# -------------------------------------------------

def zpool_import_as(server, old_name, new_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool import {old_name} {new_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool readonly importieren
# -------------------------------------------------

def zpool_import_readonly(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool import -o readonly=on {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool mit Altroot importieren
# -------------------------------------------------

def zpool_import_altroot(server, pool, path):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool import -R {path} {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool zwangsweise importieren
# -------------------------------------------------

def zpool_import_force(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool import -f {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool Cachefile deaktivieren
# -------------------------------------------------

def zpool_disable_cachefile(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool set cachefile=none {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool automatisch erweitern
# -------------------------------------------------

def zpool_enable_autoexpand(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool set autoexpand=on {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Autoexpand deaktivieren
# -------------------------------------------------

def zpool_disable_autoexpand(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool set autoexpand=off {pool}"
    )

    ssh.close()

    return result

# -------------------------------------------------
# Pool online schalten
# -------------------------------------------------

def zpool_online(server, pool, device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool online {pool} {device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool offline schalten
# -------------------------------------------------

def zpool_offline(server, pool, device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool offline {pool} {device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gerät an Mirror anhängen
# -------------------------------------------------

def zpool_attach(server, pool, old_device, new_device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool attach {pool} {old_device} {new_device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gerät aus Mirror entfernen
# -------------------------------------------------

def zpool_detach(server, pool, device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool detach {pool} {device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gerät ersetzen
# -------------------------------------------------

def zpool_replace(server, pool, old_device, new_device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool replace {pool} {old_device} {new_device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Gerät entfernen
# -------------------------------------------------

def zpool_remove(server, pool, device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool remove {pool} {device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# ZFS-Label entfernen
# -------------------------------------------------

def zpool_labelclear(server, device):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool labelclear -f {device}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool-Eigenschaft setzen
# -------------------------------------------------

def zpool_set_property(server, pool, key, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool set {key}={value} {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool-Eigenschaft lesen
# -------------------------------------------------

def zpool_get_property(server, pool, key):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get {key} {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Eigenschaften
# -------------------------------------------------

def zpool_get_all_properties(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool get all {pool}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool upgraden
# -------------------------------------------------

def zpool_upgrade(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool upgrade {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Pools upgraden
# -------------------------------------------------

def zpool_upgrade_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zpool upgrade -a"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool umbenennen
# -------------------------------------------------

def zpool_rename(server, old_name, new_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool export {old_name} && sudo zpool import {old_name} {new_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool synchronisieren
# -------------------------------------------------

def zpool_sync(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sync && sudo zpool sync {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Pool trimmen
# -------------------------------------------------

def zpool_trim(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool trim {pool}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Aktiven Trim anzeigen
# -------------------------------------------------

def zpool_trim_status(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zpool status {pool} | grep trim"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Pool löschen (mit Bestätigung)
# -------------------------------------------------

def zpool_destroy_force(server, pool):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zpool destroy -f {pool}"
    )

    ssh.close()

    return result

# -------------------------------------------------
# ZFS Datasets auflisten
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
# Dataset Namen
# -------------------------------------------------

def zfs_names(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs list -H -o name"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Dataset erstellen
# -------------------------------------------------

def zfs_create(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs create {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset löschen
# -------------------------------------------------

def zfs_destroy(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs destroy {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiv löschen
# -------------------------------------------------

def zfs_destroy_recursive(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs destroy -r {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset umbenennen
# -------------------------------------------------

def zfs_rename(server, old_name, new_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs rename {old_name} {new_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset mounten
# -------------------------------------------------

def zfs_mount(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs mount {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset aushängen
# -------------------------------------------------

def zfs_unmount(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs unmount {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Datasets mounten
# -------------------------------------------------

def zfs_mount_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zfs mount -a"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Datasets aushängen
# -------------------------------------------------

def zfs_unmount_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zfs unmount -a"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset Eigenschaften
# -------------------------------------------------

def zfs_properties(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get all {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Mountpoint
# -------------------------------------------------

def zfs_mountpoint(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value mountpoint {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Kompression
# -------------------------------------------------

def zfs_compression(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value compression {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Kompression setzen
# -------------------------------------------------

def zfs_set_compression(server, dataset, algorithm):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set compression={algorithm} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Deduplizierung
# -------------------------------------------------

def zfs_dedup(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value dedup {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Dedup setzen
# -------------------------------------------------

def zfs_set_dedup(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set dedup={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset Existiert?
# -------------------------------------------------

def zfs_exists(server, dataset):

    return dataset in zfs_names(server)


# -------------------------------------------------
# Anzahl Datasets
# -------------------------------------------------

def zfs_count(server):

    return len(
        zfs_names(server)
    )
    
# -------------------------------------------------
# Quota
# -------------------------------------------------

def zfs_quota(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value quota {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_quota(server, dataset, quota):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set quota={quota} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Reservation
# -------------------------------------------------

def zfs_reservation(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value reservation {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_reservation(server, dataset, reservation):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set reservation={reservation} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Recordsize
# -------------------------------------------------

def zfs_recordsize(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value recordsize {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_recordsize(server, dataset, size):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set recordsize={size} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Atime
# -------------------------------------------------

def zfs_atime(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value atime {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_atime(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set atime={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Sync
# -------------------------------------------------

def zfs_sync(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value sync {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_sync(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set sync={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Primary Cache
# -------------------------------------------------

def zfs_primarycache(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value primarycache {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_primarycache(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set primarycache={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Secondary Cache
# -------------------------------------------------

def zfs_secondarycache(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value secondarycache {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_secondarycache(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set secondarycache={value} {dataset}"
    )

    ssh.close()

    return result

# -------------------------------------------------
# ACL Type
# -------------------------------------------------

def zfs_acltype(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value acltype {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_acltype(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set acltype={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# ACL Inherit
# -------------------------------------------------

def zfs_aclinherit(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value aclinherit {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_set_aclinherit(server, dataset, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set aclinherit={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Encryption
# -------------------------------------------------

def zfs_encryption(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value encryption {dataset}"
    )

    ssh.close()

    return result["stdout"]


def zfs_key_status(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value keystatus {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Schlüssel laden
# -------------------------------------------------

def zfs_load_key(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs load-key {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Schlüssel entladen
# -------------------------------------------------

def zfs_unload_key(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs unload-key {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Schlüssel ändern
# -------------------------------------------------

def zfs_change_key(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs change-key {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Verschlüsselung aktivieren
# -------------------------------------------------

def zfs_enable_encryption(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set encryption=on {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Verschlüsselung deaktivieren
# -------------------------------------------------
# Hinweis:
# ZFS unterstützt kein direktes Deaktivieren der
# Verschlüsselung eines bestehenden Datasets.
# Die Funktion gibt daher einen Fehler zurück.
# -------------------------------------------------

def zfs_disable_encryption(server, dataset):

    return {
        "stdout": "",
        "stderr": (
            "Die Verschlüsselung eines bestehenden "
            "ZFS-Datasets kann nicht deaktiviert werden."
        )
    }


# -------------------------------------------------
# Dataset upgraden
# -------------------------------------------------

def zfs_upgrade(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs upgrade {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Datasets upgraden
# -------------------------------------------------

def zfs_upgrade_all(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "sudo zfs upgrade -a"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Dataset vererben
# -------------------------------------------------

def zfs_inherit(server, dataset, property_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs inherit {property_name} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Beliebige Property lesen
# -------------------------------------------------

def zfs_get_property(server, dataset, property_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value {property_name} {dataset}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Beliebige Property setzen
# -------------------------------------------------

def zfs_set_property(server, dataset, property_name, value):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs set {property_name}={value} {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Alle Properties
# -------------------------------------------------

def zfs_get_all_properties(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get all {dataset}"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Snapshots auflisten
# -------------------------------------------------

def zfs_snapshot_list(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs list -t snapshot"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot-Namen
# -------------------------------------------------

def zfs_snapshot_names(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs list -H -t snapshot -o name"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Snapshot erstellen
# -------------------------------------------------

def zfs_snapshot_create(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs snapshot {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiven Snapshot erstellen
# -------------------------------------------------

def zfs_snapshot_create_recursive(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs snapshot -r {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot löschen
# -------------------------------------------------

def zfs_snapshot_destroy(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs destroy {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiv löschen
# -------------------------------------------------

def zfs_snapshot_destroy_recursive(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs destroy -r {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot existiert
# -------------------------------------------------

def zfs_snapshot_exists(server, dataset, snapshot):

    snapshots = zfs_snapshot_names(server)

    return f"{dataset}@{snapshot}" in snapshots


# -------------------------------------------------
# Anzahl Snapshots
# -------------------------------------------------

def zfs_snapshot_count(server):

    return len(
        zfs_snapshot_names(server)
    )


# -------------------------------------------------
# Snapshots eines Datasets
# -------------------------------------------------

def zfs_dataset_snapshots(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs list -H -t snapshot -o name | grep '^{dataset}@'"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Letzter Snapshot
# -------------------------------------------------

def zfs_latest_snapshot(server, dataset):

    snapshots = zfs_dataset_snapshots(server, dataset)

    if len(snapshots) == 0:
        return None

    return snapshots[-1]


# -------------------------------------------------
# Erster Snapshot
# -------------------------------------------------

def zfs_first_snapshot(server, dataset):

    snapshots = zfs_dataset_snapshots(server, dataset)

    if len(snapshots) == 0:
        return None

    return snapshots[0]


# -------------------------------------------------
# Snapshot nach Name suchen
# -------------------------------------------------

def zfs_find_snapshot(server, name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs list -H -t snapshot -o name | grep '{name}'"
    )

    ssh.close()

    return result["stdout"].splitlines()


# -------------------------------------------------
# Snapshotgröße
# -------------------------------------------------

def zfs_snapshot_used(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value used {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Referenzierte Größe
# -------------------------------------------------

def zfs_snapshot_referenced(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value referenced {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]

# -------------------------------------------------
# Snapshot umbenennen
# -------------------------------------------------

def zfs_snapshot_rename(server, dataset, old_snapshot, new_snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs rename {dataset}@{old_snapshot} {dataset}@{new_snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot Rollback
# -------------------------------------------------

def zfs_snapshot_rollback(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs rollback {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiver Rollback
# -------------------------------------------------

def zfs_snapshot_rollback_recursive(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs rollback -r {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot klonen
# -------------------------------------------------

def zfs_snapshot_clone(server, dataset, snapshot, clone_name):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs clone {dataset}@{snapshot} {clone_name}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot Hold setzen
# -------------------------------------------------

def zfs_snapshot_hold(server, dataset, snapshot, tag):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs hold {tag} {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hold entfernen
# -------------------------------------------------

def zfs_snapshot_release(server, dataset, snapshot, tag):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs release {tag} {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Hold Informationen
# -------------------------------------------------

def zfs_snapshot_holds(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs holds {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot Eigenschaften
# -------------------------------------------------

def zfs_snapshot_properties(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get all {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot Erstellungszeit
# -------------------------------------------------

def zfs_snapshot_creation(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value creation {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot Kompression
# -------------------------------------------------

def zfs_snapshot_compressratio(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value compressratio {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot Speicherbedarf
# -------------------------------------------------

def zfs_snapshot_space(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs list -H -o used,refer {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Alle Holds anzeigen
# -------------------------------------------------

def zfs_snapshot_all_holds(server):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        "zfs list -H -t snapshot -o name | while read s; do zfs holds $s; done"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Klone eines Snapshots
# -------------------------------------------------

def zfs_snapshot_clones(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value clones {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot GUID
# -------------------------------------------------

def zfs_snapshot_guid(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value guid {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Snapshot User-Referenzen
# -------------------------------------------------

def zfs_snapshot_userrefs(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs get -H -o value userrefs {dataset}@{snapshot}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Rekursiv alle Snapshots löschen
# -------------------------------------------------

def zfs_destroy_all_snapshots(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"zfs list -H -t snapshot -o name | grep '^{dataset}@' | xargs -r -n1 sudo zfs destroy"
    )

    ssh.close()

    return result

# -------------------------------------------------
# Snapshot in Stream senden
# -------------------------------------------------

def zfs_send(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiv senden
# -------------------------------------------------

def zfs_send_recursive(server, dataset, snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send -R {dataset}@{snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Inkrementellen Stream senden
# -------------------------------------------------

def zfs_send_incremental(server,
                         dataset,
                         from_snapshot,
                         to_snapshot):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send -i "
        f"{dataset}@{from_snapshot} "
        f"{dataset}@{to_snapshot}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Stream empfangen
# -------------------------------------------------

def zfs_receive(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs receive {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Receive erzwingen
# -------------------------------------------------

def zfs_receive_force(server, dataset):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs receive -F {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot in Datei sichern
# -------------------------------------------------

def zfs_send_to_file(server,
                     dataset,
                     snapshot,
                     filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send {dataset}@{snapshot} "
        f"> {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Rekursiv in Datei sichern
# -------------------------------------------------

def zfs_send_recursive_to_file(server,
                               dataset,
                               snapshot,
                               filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send -R "
        f"{dataset}@{snapshot} "
        f"> {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Komprimierten Stream erzeugen
# -------------------------------------------------

def zfs_send_compressed(server,
                        dataset,
                        snapshot,
                        filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs send "
        f"{dataset}@{snapshot} | gzip > {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Stream aus Datei wiederherstellen
# -------------------------------------------------

def zfs_receive_from_file(server,
                          dataset,
                          filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"sudo zfs receive {dataset} < {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Komprimiertes Backup wiederherstellen
# -------------------------------------------------

def zfs_receive_compressed(server,
                           dataset,
                           filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"gunzip -c {filename} | sudo zfs receive {dataset}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backupgröße anzeigen
# -------------------------------------------------

def zfs_backup_size(server,
                    filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ls -lh {filename}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Backup löschen
# -------------------------------------------------

def zfs_delete_backup(server,
                      filename):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"rm -f {filename}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Backup-Dateien anzeigen
# -------------------------------------------------

def zfs_backup_files(server,
                     directory="/var/backups/zfs"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"ls -lh {directory}"
    )

    ssh.close()

    return result["stdout"]


# -------------------------------------------------
# Backup-Verzeichnis erstellen
# -------------------------------------------------

def zfs_backup_directory(server,
                         directory="/var/backups/zfs"):

    ssh = SSHClient(server)

    ssh.connect()

    result = ssh.execute(
        f"mkdir -p {directory}"
    )

    ssh.close()

    return result


# -------------------------------------------------
# Snapshot direkt als Backup speichern
# -------------------------------------------------

def zfs_backup_snapshot(server,
                        dataset,
                        snapshot,
                        directory="/var/backups/zfs"):

    ssh = SSHClient(server)

    ssh.connect()

    filename = (
        f"{directory}/"
        f"{dataset.replace('/', '_')}"
        f"_{snapshot}.zfs"
    )

    result = ssh.execute(
        f"mkdir -p {directory} && "
        f"sudo zfs send {dataset}@{snapshot} "
        f"> {filename}"
    )

    ssh.close()

    return result

