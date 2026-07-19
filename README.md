# GateCore Panel

GateCore Panel ist ein webbasiertes Linux-Server-Management-Frontend, das auf FastAPI basiert und die Administration von Servern, LXC-Containern, Storage-Pools, Logs und Benutzerkonten über eine zentrale Oberfläche ermöglicht.

Das Repository ist aktuell ein funktionaler Backend- und UI-Prototype mit SQLite-Datenbanken, Session-Login, Web-Panel-Routen und einer erweiterten REST-API für Server-, LXC- und Storage-Management.

## Überblick

Die Anwendung bietet eine kleine, modulare Verwaltungsschnittstelle für Linux-Umgebungen. Die Kernidee ist die Kombination aus:

- einer FastAPI-Weboberfläche
- einer Login-/Session-Authentifizierung
- mehreren SQLite-Datenbanken für Persistenz
- Verwaltung von Remote-Servern und Container-Instanzen
- Storage-Operations-APIs für Pools, Snapshots und SMART-Workflows

## Hauptfunktionen

### Benutzer- und Sessionverwaltung

- Login mit Session-Cookie
- Session-Validierung und Cleanup abgelaufener Sessions
- Benutzerverwaltung über Web-UI und API
- Passwortänderung über API-Endpunkte

### Serververwaltung

- Anlegen und Auflisten von Servereinträgen
- Host-, Port- und Benutzerkonfiguration
- Serverauswahl über API für weitere Module

### LXC-Verwaltung

- Übersicht über LXC-Container
- Container anlegen, löschen und auflisten
- Start-, Stop- und Restart-Endpunkte sind im Backend angelegt
- LXC-Konsole-Routen sind im Panel vorgesehen

### Storage- und Snapshotverwaltung

- Storage-Pools anlegen, anzeigen, aktualisieren und löschen
- SMART-Endpoints für Disk-Status, Attribute und Log-Auslesen
- SMART-Test-Start
- Scrub-Start/Stop-Endpunkte
- Snapshot-Create/Rename/Delete/Rollback/Clone-Endpoints

### Logs und Auditierung

- Logeinträge werden in `logs.db` geschrieben
- Server-, Benutzer- und Action-bezogene Einträge werden protokolliert

## Technologie-Stack

Das Projekt nutzt aktuell:

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- SQLite
- bcrypt
- SSH/Remote-Management-Module im `Core/ssh/`-bereich

## Repository-Struktur

```text
GateCore-panel/
├── Core/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   ├── ssh/
│   ├── static/
│   └── templates/
└── LICENSE
```

### Wichtige Dateien

- `Core/main.py` – Einstiegspunkt der FastAPI-Anwendung, registriert die Routen und API-Endpoints
- `Core/auth.py` – Authentifizierung, Session-Handling, Passwort-Hashing und Login-Logik
- `Core/database.py` – Erstellung und Verbindung zu SQLite-Datenbanken
- `Core/models.py` – Pydantic-Modelle für API-Requests/-Responses
- `Core/ssh/` – SSH- und Systembefehlslogik für entfernte Verwaltung
- `Core/templates/` – HTML-Templates für Login, Dashboard und Management-Seiten
- `Core/static/` – CSS/JS-Assets für das Frontend

## Weboberfläche

Die Benutzeroberfläche enthält derzeit folgende HTML-Bereiche:

- Login
- Panel-Dashboard
- Benutzerverwaltung
- Serververwaltung
- LXC-Übersicht
- Storage-Ansicht
- Logs

Die Routen sind in `Core/main.py` definiert und verwenden die Templates aus `Core/templates/panel/`.

## API-Übersicht

Die Anwendung stellt derzeit folgende API-Abschnitte bereit:

### Auth/Session

- `GET /api/user`

### Benutzer

- `GET /api/users/list`
- `POST /api/users/add`
- `DELETE /api/users/delete/{user_id}`
- `PUT /api/users/password`

### Server

- `POST /api/server/add`
- `GET /api/server/list`
- `GET /api/server/select`

### LXC

- `GET /api/lxc/count`
- `GET /api/lxc/list`
- `POST /api/lxc/start/{id}`
- `POST /api/lxc/stop/{id}`
- `POST /api/lxc/restart/{id}`
- `DELETE /api/lxc/delete/{id}`
- `POST /api/lxc/add`

### Storage

- `POST /api/storage/add`
- `GET /api/storage/list`
- `GET /api/storage/details/{pool}`
- `PUT /api/storage/update`
- `DELETE /api/storage/delete/{pool}`
- `GET /api/storage/smart/{disk}`
- `GET /api/storage/smart/attributes/{disk}`
- `GET /api/storage/smart/log/{disk}`
- `POST /api/storage/smart/test`
- `GET /api/storage/scrub/{pool}`
- `POST /api/storage/scrub/start`
- `POST /api/storage/scrub/stop`
- `GET /api/storage/snapshots/{pool}`
- `POST /api/storage/snapshot/create`
- `PUT /api/storage/snapshot/rename`
- `DELETE /api/storage/snapshot/delete`
- `POST /api/storage/snapshot/rollback`
- `POST /api/storage/snapshot/clone`

## Datenbanken

Die Anwendung nutzt SQLite-Dateien im Ordner `Core/database/`:

- `users.db` – Benutzer und Session-Daten
- `server.db` – Server-Verwaltung
- `lxc.db` – LXC-Konfigurationen und Statusdaten
- `logs.db` – Logeinträge
- `storage.db` – Storage- und Snapshot-Informationen

Beim Start der Anwendung werden die relevanten Tabellen automatisch erstellt, sofern sie noch nicht vorhanden sind.

## Installation

## Pflicht für install scripts ist Curl bitte installieren sie Curl für ihr System

### Debian/Ubuntu
```bash
apt update
apt install curl -y
```

### Rocky Linux/ Centos/ Redhat
```bash
dnf update -y
dnf install curl -y
```

### OpenSUSE 
```bash
zypper refresh
zypper install curl -y
``` 

## Installation der Software

### Um den Master/Panel zu installieren führen sie diesen Behfehl aus:
```bash
curl https://github.com/GateCore01/GateCore-panel/blob/main/install-master.sh | bash
```

Nach dem Start ist die App unter folgendem Pfad erreichbar:

```ip
http://localhost:8000
```

### Um den Hypervisor zu installieren führen sie diesen Behfehl aus:
```bash
curl https://github.com/GateCore01/GateCore-panel/blob/main/install-hypervisor.sh | bash
```

## Erster Zugriff

Nach dem Start steht die Loginseite zur Verfügung. Für den ersten Login muss ein Benutzer im System angelegt bzw. in der Datenbank vorhanden sein.

## Sicherheitsaspekte

Die Anwendung setzt aktuell auf:

- Passwort-Hashing mit `bcrypt`
- Session-Cookies für den Login-Mechanismus
- Datenpersistenz über lokale SQLite-Datenbanken

Für den produktiven Einsatz sind zusätzliche Sicherheitsebenen notwendig, z. B.:

- HTTPS/TLS
- Reverse Proxy mit Authentifizierung
- strenge Zugriffskontrollen
- Secrets-Handling außerhalb des Repositories

## Entwicklungsstatus

Das Projekt ist in aktiver Entwicklung. Es enthält bereits eine vollständige Basisstruktur mit:

- FastAPI-Backend
- HTML-Panel
- REST-API
- SQLite-Persistenz
- SSH/Remote-Management-Module

Einige Operationen wie Container-Start/Stop/Restart oder SMART-/Scrub-/Snapshot-Workflows sind derzeit als API-Endpunkte vorhanden, aber noch nicht mit vollständiger Backend-Logik für echte Remote-Ausführung verbunden. Das stellt eine gute Basis für die weitere Implementierung dar.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Die Details findest du in der Datei `LICENSE`.

## Beitrag

Beiträge sind willkommen. Du kannst das Projekt forken, eigene Änderungen entwickeln und anschließend einen Pull Request erstellen.
