# GateCore Panel

GateCore Panel ist ein webbasiertes Panel zur Verwaltung von Hosts, Benutzern und Gameserver-Einträgen. Das Projekt besteht aus einem statischen Webinterface und zwei kleinen Python-Backends ohne externe Python-Abhängigkeiten.

## Features

- Login und Session-Prüfung
- Benutzerverwaltung
- Hostverwaltung
- Serververwaltung
- Datei-Upload, Download und Löschen über SSH/SCP
- JSON-basierte Konfiguration
- REST-API für Panel, Hosts, Benutzer und Server
- Installationsscript für Debian/Ubuntu, openSUSE, Rocky Linux/RHEL-kompatible Systeme und FreeBSD

## Screens und Einstieg

Nach der Installation läuft das Panel standardmäßig auf:

```text
http://SERVER-IP:8000
```

Standard-Login:

```text
Benutzer: admin
Passwort: admin123
```

Ändere die Standard-Zugangsdaten direkt nach der Installation.

## Projektstruktur

```text
GameServer-panel/
├── auth_server.py              # Webserver, Login, API und statische Dateien
├── control_backend.py          # internes Control-Backend auf Port 8001
├── install.sh                  # plattformübergreifender Installer
├── config/
│   ├── auth-config.json        # Login für den Auth-Server
│   ├── hosts.json              # gespeicherte Hosts
│   ├── servers.json            # gespeicherte Server
│   ├── settings-config.js      # Frontend Settings als JS
│   ├── settings-config.json    # Frontend Settings als JSON
│   └── users.json              # Benutzerliste
└── panel/
    ├── index.html              # Login-Seite
    ├── css/
    ├── js/
    └── login-portal/           # geschützte Panel-Seiten
```

## Unterstützte Systeme

Das Installationsscript erkennt das Betriebssystem automatisch.

| System | Paketmanager | Service-System |
| --- | --- | --- |
| Debian / Ubuntu | `apt` | `systemd` |
| openSUSE / SLES | `zypper` | `systemd` |
| Rocky Linux / RHEL / AlmaLinux / CentOS / Fedora | `dnf` oder `yum` | `systemd` |
| FreeBSD | `pkg` | `rc.d` |

## Voraussetzungen

Das Script installiert die benötigten Pakete automatisch:

- Python 3
- Git
- OpenSSH Client / SCP
- sshpass
- CA-Zertifikate

Optional, aber empfohlen:

- Firewall-Regeln für Port `8000`
- HTTPS über Reverse Proxy, z. B. Nginx, Apache oder Caddy

## Installation

```bash
git clone https://github.com/GateCore01/GameServer-panel.git
cd GameServer-panel
chmod +x install.sh
sudo ./install.sh
```

Das Script installiert nach `/opt/gatecore-panel`, erstellt den Benutzer `gatecore` und startet diese Dienste:

- `gatecore-auth` auf Port `8000`
- `gatecore-control` auf Port `8001`

## Installation ohne Paketinstallation

Wenn alle Pakete bereits vorhanden sind:

```bash
sudo SKIP_PACKAGES=1 ./install.sh
```

## Anderer Installationspfad

```bash
sudo PREFIX=/srv/gatecore-panel ./install.sh
```

## Konfiguration überschreiben

Vorhandene Konfigurationsdateien werden standardmäßig behalten. Wenn du sie bewusst mit den Repo-Dateien überschreiben willst:

```bash
sudo FORCE_CONFIG=1 ./install.sh
```

## Repository-URL ändern

Wenn du das Script einzeln ausführst oder einen Fork installieren willst:

```bash
sudo REPO_URL=https://github.com/DEIN-USER/DEIN-REPO.git ./install.sh
```

## Service-Befehle unter Linux

Status anzeigen:

```bash
sudo systemctl status gatecore-auth
sudo systemctl status gatecore-control
```

Neustarten:

```bash
sudo systemctl restart gatecore-auth gatecore-control
```

Logs ansehen:

```bash
sudo journalctl -u gatecore-auth -f
sudo journalctl -u gatecore-control -f
```

Autostart deaktivieren:

```bash
sudo systemctl disable gatecore-auth gatecore-control
```

## Service-Befehle unter FreeBSD

Status anzeigen:

```sh
service gatecore_auth status
service gatecore_control status
```

Neustarten:

```sh
service gatecore_control restart
service gatecore_auth restart
```

Autostart deaktivieren:

```sh
sysrc gatecore_auth_enable=NO
sysrc gatecore_control_enable=NO
```

## Konfiguration

Alle Konfigurationsdateien liegen nach der Installation hier:

```text
/opt/gatecore-panel/config/
```

Wichtige Dateien:

| Datei | Zweck |
| --- | --- |
| `auth-config.json` | Admin-Login für den Auth-Server |
| `users.json` | Benutzer im Panel |
| `hosts.json` | Hosts, SSH-Benutzer, SSH-Port und Speicherpfade |
| `servers.json` | verwaltete Server |
| `settings-config.json` | Einstellungen für die Settings-Seite |
| `settings-config.js` | Frontend-Konfiguration als JavaScript |

Nach Änderungen an `auth-config.json` sollte der Auth-Service neu gestartet werden:

```bash
sudo systemctl restart gatecore-auth
```

Auf FreeBSD:

```sh
service gatecore_auth restart
```

## API-Übersicht

Der Auth-Server stellt die API auf Port `8000` bereit.

| Methode | Pfad | Beschreibung |
| --- | --- | --- |
| `POST` | `/api/login` | Login |
| `GET` | `/api/auth/check` | Session prüfen |
| `GET` | `/api/logout` | Logout |
| `GET`, `POST`, `DELETE` | `/api/users` | Benutzer verwalten |
| `GET`, `POST`, `DELETE` | `/api/hosts` | Hosts verwalten |
| `GET`, `POST`, `DELETE` | `/api/servers` | Server verwalten |
| `GET` | `/api/servers/{id}/files` | Dateien eines Servers anzeigen |
| `POST` | `/api/servers/{id}/files/upload` | Datei hochladen |
| `GET` | `/api/servers/{id}/files/download` | Datei herunterladen |
| `DELETE` | `/api/servers/{id}/files/delete` | Datei löschen |

Das interne Control-Backend läuft lokal auf Port `8001` und wird vom Auth-Server verwendet.

## Firewall

Für Zugriff im Netzwerk muss Port `8000` erreichbar sein.

Debian/Ubuntu mit UFW:

```bash
sudo ufw allow 8000/tcp
```

Rocky Linux mit firewalld:

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

openSUSE mit firewalld:

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

FreeBSD mit pf muss die Regel in deiner `pf.conf` ergänzt werden.

## Sicherheit

- Standardpasswörter nach der Installation ändern.
- Port `8001` nicht öffentlich freigeben.
- Für produktive Nutzung HTTPS vor Port `8000` setzen.
- SSH-Zugänge für Hosts möglichst mit eingeschränkten Benutzern betreiben.
- `sshpass` nur nutzen, wenn Passwort-Login wirklich benötigt wird. SSH-Keys sind sicherer.
- Konfigurationsdateien enthalten sensible Daten und sollten nicht öffentlich geteilt werden.

## Manuell starten

Für Entwicklung oder Tests:

```bash
python3 control_backend.py
python3 auth_server.py
```

Danach im Browser öffnen:

```text
http://127.0.0.1:8000
```

## Update

Im Repository:

```bash
git pull
sudo ./install.sh
```

Vorhandene Konfigurationsdateien bleiben erhalten, solange `FORCE_CONFIG=1` nicht gesetzt ist.

## Deinstallation

Linux mit systemd:

```bash
sudo systemctl disable --now gatecore-auth gatecore-control
sudo rm -f /etc/systemd/system/gatecore-auth.service
sudo rm -f /etc/systemd/system/gatecore-control.service
sudo systemctl daemon-reload
sudo rm -rf /opt/gatecore-panel
```

FreeBSD:

```sh
service gatecore_auth stop
service gatecore_control stop
sysrc gatecore_auth_enable=NO
sysrc gatecore_control_enable=NO
rm -f /usr/local/etc/rc.d/gatecore_auth
rm -f /usr/local/etc/rc.d/gatecore_control
rm -rf /opt/gatecore-panel
```

## Troubleshooting

Panel nicht erreichbar:

- Prüfe, ob `gatecore-auth` läuft.
- Prüfe, ob Port `8000` in der Firewall offen ist.
- Prüfe die Logs mit `journalctl -u gatecore-auth -f`.

Serverliste oder Serveraktionen funktionieren nicht:

- Prüfe, ob `gatecore-control` läuft.
- Prüfe, ob Port `8001` lokal erreichbar ist.
- Prüfe die Datei `config/servers.json`.

SSH/SCP Aktionen funktionieren nicht:

- Prüfe Host, Benutzer und Port in `config/hosts.json`.
- Prüfe, ob der Zielhost per SSH erreichbar ist.
- Prüfe, ob `sshpass` installiert ist, falls Passwort-Login genutzt wird.

## Mitwirken

Pull Requests, Issues und Verbesserungsvorschläge sind willkommen.

1. Repository forken
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request öffnen

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Details stehen in [LICENSE](LICENSE).

## Autor

Korbinian Musch

GitHub: https://github.com/GateCore01
