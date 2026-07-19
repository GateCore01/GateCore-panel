from typing import Any

from ssh.client import SSHClient


def run(server: dict[str, Any], command: str) -> dict[str, str]:
    """Führt einen Remote-Befehl über SSH aus und schließt die Verbindung sauber.

    Args:
        server: Serverkonfiguration mit SSH-Zugangsdaten.
        command: Auszuführender Befehl auf dem Remote-Host.

    Returns:
        Wörterbuch mit stdout und stderr.
    """
    with SSHClient(server) as ssh:
        return ssh.execute(command)