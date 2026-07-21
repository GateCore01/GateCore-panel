###########################################################################
# File: Core/ssh/client.py
# SSH-Client mit Timeouts und optimierten Verbindungen für lokale Netze
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-20
# Communion: GateCore01
############################################################################

import paramiko
import socket
from typing import Optional, Dict, Any, Union
from io import StringIO


class SSHClient:
    """
    SSH-Client für Verbindungen zu Remote-Servern.
    - Optimierte Timeouts für lokale Management-Netzwerke
    - Kein SSH-Agent (schneller)
    - Keine ~/.ssh/keys (schneller)
    - Auto-Reconnect bei Verbindungsabbruch
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialisiert den SSH-Client mit Server-Konfiguration.

        Args:
            config: Dictionary mit 'host', 'port', 'username', 'password', 'private_key'
        """
        self.host = config.get("host")
        self.port = int(config.get("port", 22))
        self.username = config.get("username")
        self.password = config.get("password")
        self.private_key = config.get("private_key")
        self.client: Optional[paramiko.SSHClient] = None
        self._connected = False

        # Timeout-Einstellungen für lokale Netze (schnellere Fehlermeldungen)
        self.connect_timeout = 10      # Verbindungsaufbau max. 10 Sekunden
        self.auth_timeout = 5          # Authentifizierung max. 5 Sekunden
        self.banner_timeout = 10       # Banner-Timeout
        self.command_timeout = 30      # Kommando-Timeout (Default, kann überschrieben werden)

    def connect(self) -> None:
        """Stellt die SSH-Verbindung her – mit optimierten Timeouts."""
        if self._connected and self.client:
            return

        if not self.host:
            raise ValueError("Host ist nicht gesetzt")
        if not self.username:
            raise ValueError("Username ist nicht gesetzt")

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Verbindung mit Timeouts aufbauen
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                pkey=self._load_private_key(),
                timeout=self.connect_timeout,
                auth_timeout=self.auth_timeout,
                banner_timeout=self.banner_timeout,
                allow_agent=False,           # Kein SSH-Agent (schneller)
                look_for_keys=False,         # Keine ~/.ssh/keys (schneller)
                compress=True,               # Komprimierung aktivieren (optional)
            )
            self._connected = True
        except paramiko.AuthenticationException as exc:
            raise Exception(f"Authentifizierung fehlgeschlagen: {exc}")
        except paramiko.SSHException as exc:
            raise Exception(f"SSH-Fehler: {exc}")
        except socket.timeout:
            raise Exception(f"Verbindungs-Timeout nach {self.connect_timeout}s")
        except Exception as exc:
            raise Exception(f"Verbindung fehlgeschlagen: {exc}")

    def _load_private_key(self) -> Optional[paramiko.PKey]:
        """
        Lädt den privaten SSH-Schlüssel (falls vorhanden) aus einem String.
        Unterstützt RSA und Ed25519.
        """
        if not self.private_key:
            return None

        try:
            # Versuche RSA zuerst
            key_file = StringIO(self.private_key)
            return paramiko.RSAKey.from_private_key(key_file)
        except paramiko.SSHException:
            try:
                # Fallback: Ed25519
                key_file = StringIO(self.private_key)
                return paramiko.Ed25519Key.from_private_key(key_file)
            except Exception:
                raise Exception("Ungültiger privater SSH-Schlüssel (weder RSA noch Ed25519)")

    def ensure_connected(self) -> None:
        """Stellt sicher, dass die Verbindung aktiv ist – versucht ggf. Reconnect."""
        if not self._connected or not self.client:
            self.connect()
            return

        # Prüfen, ob die Verbindung noch lebt (Send 'no-op')
        try:
            transport = self.client.get_transport()
            if transport is None or not transport.is_active():
                # Verbindung tot → Reconnect
                self.close()
                self.connect()
        except Exception:
            # Bei Fehlern → Reconnect
            self.close()
            self.connect()

    def execute(self, command: str, timeout: int = 30) -> Dict[str, str]:
        """
        Führt einen Befehl auf dem Remote-Server aus.

        Args:
            command: Der auszuführende Befehl
            timeout: Timeout in Sekunden (Default 30)

        Returns:
            Dictionary mit 'stdout' und 'stderr'
        """
        self.ensure_connected()

        # Type-Guard: self.client ist nach ensure_connected garantiert nicht None
        if self.client is None:
            raise Exception("SSH-Client nicht initialisiert")

        try:
            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=timeout,
                get_pty=False  # Kein Pseudo-Terminal (schneller)
            )

            # Ausgaben lesen
            stdout_text = stdout.read().decode('utf-8', errors='ignore').strip()
            stderr_text = stderr.read().decode('utf-8', errors='ignore').strip()

            return {
                "stdout": stdout_text,
                "stderr": stderr_text
            }
        except paramiko.SSHException as exc:
            # Bei SSH-Fehler → Verbindung schließen und neu aufbauen
            self.close()
            self._connected = False
            raise Exception(f"SSH-Kommando fehlgeschlagen: {exc}")
        except socket.timeout:
            raise Exception(f"Kommando-Timeout nach {timeout}s")
        except Exception as exc:
            raise Exception(f"Fehler bei Kommandoausführung: {exc}")

    def close(self) -> None:
        """Schließt die SSH-Verbindung."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
            self.client = None
        self._connected = False

    def __enter__(self):
        """Context-Manager Einstieg."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context-Manager Ausstieg – schließt Verbindung."""
        self.close()


# -------------------------------------------------
# Hilfsfunktion für schnelle Verbindungsprüfungen
# -------------------------------------------------

def test_connection(
    host: str,
    port: int = 22,
    username: str = "root",
    password: Optional[str] = None,
    private_key: Optional[str] = None,
    timeout: int = 5,
) -> bool:
    """
    Prüft, ob eine SSH-Verbindung hergestellt werden kann (schnell, mit kurzem Timeout).

    Args:
        host: Hostname oder IP
        port: SSH-Port (Default 22)
        username: Benutzername
        password: Passwort (optional)
        private_key: Privater Schlüssel (optional)
        timeout: Timeout in Sekunden (Default 5)

    Returns:
        True bei erfolgreicher Verbindung, sonst False
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        pkey = None
        if private_key:
            key_file = StringIO(private_key)
            # Versuche RSA, sonst Ed25519
            try:
                pkey = paramiko.RSAKey.from_private_key(key_file)
            except paramiko.SSHException:
                key_file = StringIO(private_key)
                pkey = paramiko.Ed25519Key.from_private_key(key_file)

        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            pkey=pkey,
            timeout=timeout,
            auth_timeout=timeout,
            allow_agent=False,
            look_for_keys=False,
        )
        client.close()
        return True
    except Exception:
        return False