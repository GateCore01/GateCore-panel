# Core/ssh/btrfs.py – BTRFS-Operationen via SSH
from ssh.client import SSHClient
from typing import List, Dict
import re


def btrfs_version(server: dict) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute("btrfs --version")
        return result["stdout"].strip()


def list_filesystems(server: dict) -> List[Dict]:
    """Listet alle BTRFS-Dateisysteme (Pools) – einfache Textparsing."""
    with SSHClient(server) as ssh:
        result = ssh.execute("btrfs filesystem show --raw")
        lines = result["stdout"].splitlines()
        fs_list = []
        current = {}
        for line in lines:
            if line.startswith("Label:"):
                if current:
                    fs_list.append(current)
                current = {"label": line.split(":", 1)[1].strip()}
            elif "uuid:" in line:
                current["uuid"] = line.split("uuid:", 1)[1].strip()
            elif "Total devices" in line:
                current["devices"] = line.split("Total devices", 1)[1].strip()
            elif "size" in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    current["device"] = parts[0]
                    current["size"] = parts[2]
        if current:
            fs_list.append(current)
        return fs_list


def pool_status(server: dict, mountpoint: str) -> Dict:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs filesystem df {mountpoint}")
        lines = result["stdout"].splitlines()
        usage = {}
        for line in lines:
            if "Data" in line:
                usage["data"] = line
            elif "System" in line:
                usage["system"] = line
            elif "Metadata" in line:
                usage["metadata"] = line
        usage_detail = ssh.execute(f"btrfs filesystem usage {mountpoint}")
        usage["details"] = usage_detail["stdout"]
        return usage


def create_pool(server: dict, devices: List[str], raid_level: str, mountpoint: str) -> str:
    """Erstellt BTRFS-Pool mit RAID. raid_level: single, raid0, raid1, raid10, raid5, raid6."""
    device_str = " ".join(devices)
    cmd = f"mkfs.btrfs -d {raid_level} -m {raid_level} -f {device_str}"
    with SSHClient(server) as ssh:
        result = ssh.execute(cmd)
        if result["stderr"]:
            raise Exception(result["stderr"])
        # Mounten
        mount_cmd = f"mount {devices[0]} {mountpoint}"
        result2 = ssh.execute(mount_cmd)
        if result2["stderr"]:
            raise Exception(result2["stderr"])
        return f"Pool erstellt und nach {mountpoint} gemountet."


def delete_pool(server: dict, mountpoint: str) -> str:
    """Löscht einen BTRFS-Pool (Achtung: Datenverlust!)."""
    with SSHClient(server) as ssh:
        # Unmount
        ssh.execute(f"umount {mountpoint}")
        # Geräte finden, die zum Pool gehören
        result = ssh.execute(f"btrfs filesystem show {mountpoint}")
        devices = re.findall(r'/dev/\S+', result["stdout"])
        if not devices:
            raise Exception("Keine Geräte gefunden.")
        # Geräte überschreiben (gefährlich) – hier nur Warnung.
        return "BTRFS-Pool nicht automatisch löschbar; bitte Geräte manuell überschreiben."


def add_device(server: dict, mountpoint: str, new_device: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs device add {new_device} {mountpoint}")
        if result["stderr"]:
            raise Exception(result["stderr"])
        return f"Gerät {new_device} hinzugefügt."


def remove_device(server: dict, mountpoint: str, device: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs device remove {device} {mountpoint}")
        if result["stderr"]:
            raise Exception(result["stderr"])
        return f"Gerät {device} entfernt."


def create_subvolume(server: dict, mountpoint: str, name: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs subvolume create {mountpoint}/{name}")
        if result["stderr"]:
            raise Exception(result["stderr"])
        return f"Subvolume {name} erstellt."


def delete_subvolume(server: dict, subvol_path: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs subvolume delete {subvol_path}")
        if result["stderr"]:
            raise Exception(result["stderr"])
        return f"Subvolume {subvol_path} gelöscht."


def list_subvolumes(server: dict, mountpoint: str) -> List[Dict]:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs subvolume list {mountpoint}")
        lines = result["stdout"].splitlines()
        subvols = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6:
                subvols.append({
                    "id": parts[1],
                    "path": parts[-1],
                    "uuid": parts[2] if len(parts) > 5 else ""
                })
        return subvols


def create_snapshot(server: dict, source_subvol: str, dest_snapshot: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs subvolume snapshot {source_subvol} {dest_snapshot}")
        if result["stderr"]:
            raise Exception(result["stderr"])
        return f"Snapshot {dest_snapshot} erstellt."


def delete_snapshot(server: dict, snapshot_path: str) -> str:
    return delete_subvolume(server, snapshot_path)


def list_snapshots(server: dict, mountpoint: str) -> List[Dict]:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs subvolume list -s {mountpoint}")
        lines = result["stdout"].splitlines()
        snaps = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6:
                snaps.append({
                    "id": parts[1],
                    "path": parts[-1],
                    "uuid": parts[2] if len(parts) > 5 else ""
                })
        return snaps


def scrub_start(server: dict, mountpoint: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs scrub start {mountpoint}")
        return result["stdout"]


def scrub_status(server: dict, mountpoint: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs scrub status {mountpoint}")
        return result["stdout"]


def scrub_stop(server: dict, mountpoint: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs scrub cancel {mountpoint}")
        return result["stdout"]


def balance_start(server: dict, mountpoint: str, filters: str = "") -> str:
    with SSHClient(server) as ssh:
        cmd = f"btrfs balance start {filters} {mountpoint}"
        result = ssh.execute(cmd)
        return result["stdout"]


def balance_status(server: dict, mountpoint: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"btrfs balance status {mountpoint}")
        return result["stdout"]