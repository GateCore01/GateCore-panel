import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

# -------------------------------------------------
# Pfade
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

USERS_DB = DATABASE_DIR / "users.db"
SERVER_DB = DATABASE_DIR / "server.db"
LXC_DB = DATABASE_DIR / "lxc.db"
DB_PATH_LOGS = DATABASE_DIR / "logs.db"
DB_PATH_STORAGE = DATABASE_DIR / "storage.db"

# -------------------------------------------------
# Verbindungen
# -------------------------------------------------


def user_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Benutzer-/Session-Datenbank."""
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def server_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Server-Datenbank."""
    conn = sqlite3.connect(SERVER_DB)
    conn.row_factory = sqlite3.Row
    return conn


def lxc_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur LXC-Datenbank."""
    conn = sqlite3.connect(LXC_DB)
    conn.row_factory = sqlite3.Row
    return conn


def logs_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Log-Datenbank."""
    conn = sqlite3.connect(DB_PATH_LOGS)
    conn.row_factory = sqlite3.Row
    return conn


def storage_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Storage-Datenbank."""
    conn = sqlite3.connect(DB_PATH_STORAGE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------
# Datenbank initialisieren
# -------------------------------------------------


def init_database() -> None:
    """Initialisiert alle für GateCore benötigten SQLite-Datenbanken."""
    create_users_database()
    create_server_database()
    create_lxc_database()
    create_logs_database()
    create_storage_database()

# -------------------------------------------------
# users.db
# -------------------------------------------------

def create_users_database():

    conn = user_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'user',

            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (

            token TEXT PRIMARY KEY,

            username TEXT NOT NULL,

            expires INTEGER NOT NULL

        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# server.db
# -------------------------------------------------

def create_server_database() -> None:
    """Erstellt die Server-Tabelle für SSH-Verbindungen."""
    conn = server_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER DEFAULT 22,
            username TEXT NOT NULL,
            password TEXT,
            private_key TEXT,
            description TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# -------------------------------------------------
# lxc.db
# -------------------------------------------------

def create_lxc_database() -> None:
    """Erstellt die LXC-Tabelle mit Spalten, die von den APIs abgefragt werden."""
    conn = lxc_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lxc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server TEXT NOT NULL,
            vmid INTEGER NOT NULL,
            template TEXT DEFAULT 'download',
            status TEXT DEFAULT 'unknown',
            ip TEXT,
            cpu TEXT,
            ram TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lxc_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT,
            type TEXT NOT NULL,
            repo_url TEXT,
            download_url TEXT,
            last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor = conn.cursor()
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(lxc)")]

    if "template" not in columns:
        cursor.execute(
            "ALTER TABLE lxc ADD COLUMN template TEXT DEFAULT 'download'"
        )

    conn.commit()
    conn.close()
    
    
# Abfrage für get-server
def get_server(server_id: int) -> sqlite3.Row | None:
    """Lädt einen Serverdatensatz anhand seiner ID."""
    conn = server_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM servers WHERE id=?", (server_id,))
    server = cursor.fetchone()

    conn.close()
    return server


# -------------------------------------------------
# logs.db
# -------------------------------------------------


def create_logs_database() -> None:
    """Erstellt die Log-Tabelle."""
    conn = logs_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            server TEXT,
            username TEXT,
            level TEXT,
            action TEXT,
            details TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def write_log(
    server: str | None,
    username: str | None,
    level: str,
    action: str,
    details: str,
) -> None:
    """Schreibt einen Logeintrag in die passende SQLite-Tabelle."""
    conn = logs_connection()

    conn.execute(
        """
        INSERT INTO logs (
            timestamp,
            server,
            username,
            level,
            action,
            details
        )
        VALUES (?,?,?,?,?,?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            server,
            username,
            level,
            action,
            details,
        ),
    )

    conn.commit()
    conn.close()


# -------------------------------------------------
# storage.db
# -------------------------------------------------


def create_storage_database() -> None:
    """Erstellt die Tabellen für Storage, Snapshots und SMART-History."""
    conn = storage_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server INTEGER NOT NULL,
            pool TEXT UNIQUE NOT NULL,
            filesystem TEXT,
            raid TEXT,
            mountpoint TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool TEXT,
            dataset TEXT,
            snapshot TEXT,
            created TEXT,
            used TEXT,
            referenced TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS smart_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disk TEXT,
            temperature INTEGER,
            health TEXT,
            created TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scrub_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool TEXT,
            started TEXT,
            finished TEXT,
            duration TEXT,
            errors INTEGER,
            result TEXT
        )
        """
    )

    conn.commit()
    conn.close()