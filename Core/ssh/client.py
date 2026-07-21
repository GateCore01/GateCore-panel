###########################################################################
# File: Core/ssh/client.py
# SSH-Client mit Timeouts und optimierten Verbindungen für lokale Netze
###########################################################################
import paramiko
import socket
from typing import Optional, Dict, Any, Union
from io import StringIO

class SSHClient:
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get("host")
        self.port = int(config.get("port", 22))
        self.username = config.get("username")
        self.password = config.get("password")
        self.private_key = config.get("private_key")
        self.client: Optional[paramiko.SSHClient] = None
        self._connected = False
        self.connect_timeout = 10
        self.auth_timeout = 5
        self.banner_timeout = 10
        self.command_timeout = 30

    def connect(self) -> None:
        if self._connected and self.client:
            return
        if not self.host or not self.username:
            raise ValueError("Host oder Username fehlt")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(
                hostname=self.host, port=self.port, username=self.username,
                password=self.password, pkey=self._load_private_key(),
                timeout=self.connect_timeout, auth_timeout=self.auth_timeout,
                banner_timeout=self.banner_timeout,
                allow_agent=False, look_for_keys=False, compress=True
            )
            self._connected = True
        except Exception as e:
            raise Exception(f"Verbindung fehlgeschlagen: {e}")

    def _load_private_key(self) -> Optional[paramiko.PKey]:
        if not self.private_key:
            return None
        try:
            key_file = StringIO(self.private_key)
            return paramiko.RSAKey.from_private_key(key_file)
        except paramiko.SSHException:
            try:
                key_file = StringIO(self.private_key)
                return paramiko.Ed25519Key.from_private_key(key_file)
            except Exception:
                raise Exception("Ungültiger privater SSH-Schlüssel")

    def ensure_connected(self) -> None:
        if not self._connected or not self.client:
            self.connect()
            return
        try:
            transport = self.client.get_transport()
            if transport is None or not transport.is_active():
                self.close()
                self.connect()
        except:
            self.close()
            self.connect()

    def execute(self, command: str, timeout: int = 30) -> Dict[str, str]:
        self.ensure_connected()
        if self.client is None:
            raise Exception("SSH-Client nicht initialisiert")
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout, get_pty=False)
            return {
                "stdout": stdout.read().decode('utf-8', errors='ignore').strip(),
                "stderr": stderr.read().decode('utf-8', errors='ignore').strip()
            }
        except Exception as e:
            self.close()
            self._connected = False
            raise Exception(f"Kommando fehlgeschlagen: {e}")

    def close(self) -> None:
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def test_connection(host: str, port: int = 22, username: str = "root",
                    password: Optional[str] = None, private_key: Optional[str] = None,
                    timeout: int = 5) -> bool:
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = None
        if private_key:
            key_file = StringIO(private_key)
            try:
                pkey = paramiko.RSAKey.from_private_key(key_file)
            except paramiko.SSHException:
                key_file = StringIO(private_key)
                pkey = paramiko.Ed25519Key.from_private_key(key_file)
        client.connect(hostname=host, port=port, username=username,
                       password=password, pkey=pkey, timeout=timeout,
                       auth_timeout=timeout, allow_agent=False, look_for_keys=False)
        client.close()
        return True
    except:
        return False