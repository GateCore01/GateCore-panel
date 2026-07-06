# GateCore Panel

> Ein modernes, webbasiertes Server- und Host-Management-Panel mit Python-Backend.

## Funktionen

* Modernes Webinterface
* Benutzeranmeldung
* Benutzerverwaltung
* Serververwaltung
* Hostverwaltung
* Einstellungsverwaltung
* Passwortverwaltung
* REST-API
* Authentifizierungsserver
* Optimiert für Linux

## Projektstruktur

```text
GateCore-panel/
├── auth_server.py          # Authentifizierungsserver
├── control_backend.py      # Backend
├── install.sh              # Installationsscript
├── config/                 # Konfiguration
│   ├── auth-config.json
│   ├── hosts.json
│   ├── servers.json
│   ├── settings-config.json
│   └── users.json
└── panel/
    ├── index.html
    ├── css/
    ├── js/
    └── login-portal/
```

## Voraussetzungen

* Debian oder Ubuntu
* Python 3.12 oder neuer
* Apache2
* Docker
* Docker Compose
* Git
* OpenSSL

## Installation

```bash
git clone https://github.com/Korbinian0/GateCore-panel.git
cd GateCore-panel

chmod +x install.sh
sudo ./install.sh
```

## Konfiguration

Die Konfigurationsdateien befinden sich im Ordner:

```text
config/
```

Dort können Benutzer, Hosts, Server und allgemeine Einstellungen angepasst werden.

## API

Die Dokumentation der API befindet sich in

```text
API_SETTINGS_DOCU.md
```

## Sicherheit

* Passwortverwaltung
* Getrennte Authentifizierung
* JSON-basierte Konfiguration
* Für eine produktive Umgebung sollten HTTPS und ein Reverse Proxy (z. B. Nginx oder Apache) verwendet werden.

## Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**.

Weitere Informationen befinden sich in der Datei `LICENSE`.

## Mitwirken

Pull Requests und Verbesserungsvorschläge sind willkommen.

1. Repository forken
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request eröffnen

## Autor

**Korbinian Musch**

GitHub: https://github.com/GateCore01

---

Wenn dir GateCore Panel gefällt, freue ich mich über einen Star auf GitHub.
