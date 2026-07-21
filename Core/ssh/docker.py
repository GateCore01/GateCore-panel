# Core/ssh/docker.py – Docker-Operationen via SSH
from ssh.client import SSHClient
import json
from typing import List, Dict, Optional


def list_containers(server: dict, all: bool = False) -> List[Dict]:
    with SSHClient(server) as ssh:
        cmd = f"docker ps {'-a' if all else ''} --format '{{{{json .}}}}'"
        result = ssh.execute(cmd)
        lines = result["stdout"].strip().splitlines()
        return [json.loads(line) for line in lines if line]


def inspect_container(server: dict, container_id: str) -> Dict:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker inspect {container_id}")
        return json.loads(result["stdout"])[0] if result["stdout"] else {}


def start_container(server: dict, container_id: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker start {container_id}")
        return result["stdout"]


def stop_container(server: dict, container_id: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker stop {container_id}")
        return result["stdout"]


def restart_container(server: dict, container_id: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker restart {container_id}")
        return result["stdout"]


def delete_container(server: dict, container_id: str, force: bool = False) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker rm {'-f' if force else ''} {container_id}")
        return result["stdout"]


def create_container(server: dict, name: str, image: str, command: str = "",
                     env: Optional[List[str]] = None,
                     volumes: Optional[List[str]] = None,
                     ports: Optional[List[str]] = None,
                     detach: bool = True) -> str:
    env = env or []
    volumes = volumes or []
    ports = ports or []
    env_str = " ".join([f"-e {e}" for e in env])
    vol_str = " ".join([f"-v {v}" for v in volumes])
    port_str = " ".join([f"-p {p}" for p in ports])
    detach_flag = "-d" if detach else ""
    with SSHClient(server) as ssh:
        cmd = f"docker run {detach_flag} --name {name} {env_str} {vol_str} {port_str} {image} {command}"
        result = ssh.execute(cmd)
        if result["stderr"]:
            raise Exception(result["stderr"])
        return result["stdout"].strip()


def pull_image(server: dict, image: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker pull {image}")
        return result["stdout"]


def list_images(server: dict) -> List[Dict]:
    with SSHClient(server) as ssh:
        result = ssh.execute("docker images --format '{{json .}}'")
        lines = result["stdout"].strip().splitlines()
        return [json.loads(line) for line in lines if line]


def list_volumes(server: dict) -> List[Dict]:
    with SSHClient(server) as ssh:
        result = ssh.execute("docker volume ls --format '{{json .}}'")
        lines = result["stdout"].strip().splitlines()
        return [json.loads(line) for line in lines if line]


def create_volume(server: dict, name: str, driver: str = "local") -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker volume create --driver {driver} {name}")
        return result["stdout"].strip()


def remove_volume(server: dict, name: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker volume rm {name}")
        return result["stdout"]


def list_networks(server: dict) -> List[Dict]:
    with SSHClient(server) as ssh:
        result = ssh.execute("docker network ls --format '{{json .}}'")
        lines = result["stdout"].strip().splitlines()
        return [json.loads(line) for line in lines if line]


def create_network(server: dict, name: str, driver: str = "bridge") -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker network create --driver {driver} {name}")
        return result["stdout"].strip()


def remove_network(server: dict, name: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker network rm {name}")
        return result["stdout"]


def container_logs(server: dict, container_id: str, tail: int = 100) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker logs --tail {tail} {container_id}")
        return result["stdout"] + ("\n" + result["stderr"] if result["stderr"] else "")


def exec_command(server: dict, container_id: str, command: str) -> str:
    with SSHClient(server) as ssh:
        result = ssh.execute(f"docker exec {container_id} {command}")
        return result["stdout"] + ("\n" + result["stderr"] if result["stderr"] else "")