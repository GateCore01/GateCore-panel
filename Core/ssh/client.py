import os
import socket
from collections.abc import Mapping
from typing import Any

import paramiko


class SSHClient:
    """Zentrale SSH-Verbindung für GateCore-Remote-Operationen.

    Die Klasse kapselt den Paramiko-Transport und stellt eine einfache,
    robustere Verbindung für Passwort- und SSH-Key-Authentifizierung bereit.
    """

    def __init__(self, server: Mapping[str, Any]):
        self.server = dict(server)
        self.client: paramiko.SSHClient | None = None

    def _validate_server_config(self) -> None:
        """Validiert die benötigten Serverdaten vor dem Verbindungsaufbau."""
        host = str(self.server.get("host", "")).strip()
        username = str(self.server.get("username", "")).strip()
        port = int(self.server.get("port", 22))

        if not host:
            raise ValueError("SSH-Host ist erforderlich.")

        if not username:
            raise ValueError("SSH-Benutzername ist erforderlich.")

        if not 1 <= port <= 65535:
            raise ValueError("SSH-Port muss zwischen 1 und 65535 liegen.")

    def connect(self) -> None:
        """Öffnet die SSH-Verbindung zum konfigurierten Host."""
        self._validate_server_config()

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connection_args: dict[str, Any] = {
            "hostname": str(self.server["host"]).strip(),
            "port": int(self.server["port"]),
            "username": str(self.server["username"]).strip(),
            "timeout": 10,
        }

        private_key = self.server.get("private_key")

        if private_key:
            private_key_path = str(private_key).strip()

            if not os.path.exists(private_key_path):
                raise FileNotFoundError(
                    f"SSH-Key-Datei nicht gefunden: {private_key_path}"
                )

            connection_args["key_filename"] = private_key_path
        elif self.server.get("password"):
            connection_args["password"] = str(self.server["password"])
        else:
            raise ValueError(
                "Für SSH muss entweder ein Passwort oder ein SSH-Key angegeben werden."
            )

        try:
            client.connect(**connection_args)
        except (paramiko.AuthenticationException, paramiko.SSHException, socket.error) as exc:
            client.close()
            raise RuntimeError(f"SSH-Verbindung fehlgeschlagen: {exc}") from exc

        self.client = client

    def execute(self, command: str) -> dict[str, str]:
        """Führt einen SSH-Befehl aus und liefert stdout/stderr zurück."""
        if not isinstance(command, str) or not command.strip():
            raise ValueError("Ein gültiger SSH-Befehl ist erforderlich.")

        if self.client is None:
            raise RuntimeError("SSH-Verbindung wurde noch nicht aufgebaut.")

        _, stdout, stderr = self.client.exec_command(command)

        return {
            "stdout": stdout.read().decode(errors="replace").strip(),
            "stderr": stderr.read().decode(errors="replace").strip(),
        }

    def close(self) -> None:
        """Schließt die SSH-Verbindung sicher und setzt den Zustand zurück."""
        if self.client is None:
            return

        try:
            self.client.close()
        finally:
            self.client = None

    def __enter__(self) -> "SSHClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()