###########################################################################
# File: Core/database.py
# Database management for GateCore
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-19
# Communion: GateCore01
############################################################################
# !/bin/python

import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Any

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
DB_PATH_BACKUP = DATABASE_DIR / "backup.db"

# -------------------------------------------------
# Helfer: Verbindung mit WAL + synchronous=NORMAL
# -------------------------------------------------

def _connect_with_wal(db_path: Path) -> sqlite3.Connection:
    """
    Öffnet eine SQLite-Verbindung und aktiviert:
      - WAL-Modus (bessere Concurrency)
      - synchronous = NORMAL (performanter, aber immer noch sicher genug)
      - foreign_keys = ON (optional, für späteres Fremdschlüssel-Setup)
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Optimierungen für SQLite im lokalen Netz
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")      # Für spätere Erweiterungen
    conn.execute("PRAGMA cache_size=-20000")    # 20 MB Cache (beschleunigt Lesevorgänge)
    
    return conn


# -------------------------------------------------
# Verbindungen (für direkte Nutzung, z.B. in Migrations-Skripten)
# -------------------------------------------------

def user_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Benutzer-/Session-Datenbank."""
    return _connect_with_wal(USERS_DB)

def server_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Server-Datenbank."""
    return _connect_with_wal(SERVER_DB)

def lxc_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur LXC-Datenbank."""
    return _connect_with_wal(LXC_DB)

def logs_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Log-Datenbank."""
    return _connect_with_wal(DB_PATH_LOGS)

def storage_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Storage-Datenbank."""
    return _connect_with_wal(DB_PATH_STORAGE)

def backup_connection() -> sqlite3.Connection:
    """Erzeugt eine Verbindung zur Backup-Datenbank."""
    return _connect_with_wal(DB_PATH_BACKUP)


# -------------------------------------------------
# Dependency Injection für FastAPI (automatisches Schließen)
# -------------------------------------------------

@contextmanager
def get_db_connection(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Context-Manager für beliebige DB-Pfade."""
    conn = _connect_with_wal(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Spezifische Dependencies für FastAPI-Routen
def get_server_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(SERVER_DB) as conn:
        yield conn

def get_user_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(USERS_DB) as conn:
        yield conn

def get_lxc_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(LXC_DB) as conn:
        yield conn

def get_logs_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(DB_PATH_LOGS) as conn:
        yield conn

def get_storage_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(DB_PATH_STORAGE) as conn:
        yield conn

def get_backup_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(DB_PATH_BACKUP) as conn:
        yield conn


# -------------------------------------------------
# Datenbanken initialisieren
# -------------------------------------------------

def init_database() -> None:
    """Erstellt alle Datenbanken und Tabellen."""
    create_users_database()
    create_server_database()
    create_lxc_database()
    create_logs_database()
    create_storage_database()
    create_backup_database()


# -------------------------------------------------
# users.db
# -------------------------------------------------

def create_users_database() -> None:
    conn = user_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
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

    # Index für schnellere Session-Lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_username ON sessions(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires)")

    conn.commit()
    conn.close()


# -------------------------------------------------
# server.db
# -------------------------------------------------

def create_server_database() -> None:
    conn = server_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            host TEXT NOT NULL,
            port INTEGER DEFAULT 22,
            username TEXT NOT NULL,
            password TEXT,
            private_key TEXT,
            description TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Index für Namenssuche
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_servers_name ON servers(name)")

    conn.commit()
    conn.close()


# -------------------------------------------------
# lxc.db
# -------------------------------------------------

def create_lxc_database() -> None:
    conn = lxc_connection()
    cursor = conn.cursor()

    cursor.execute("""
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
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lxc_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT,
            type TEXT NOT NULL,
            repo_url TEXT,
            download_url TEXT,
            last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Indizes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lxc_server ON lxc(server)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lxc_status ON lxc(status)")

    # Sicherstellen, dass die 'template'-Spalte existiert (für bestehende DBs)
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(lxc)")]
    if "template" not in columns:
        cursor.execute("ALTER TABLE lxc ADD COLUMN template TEXT DEFAULT 'download'")

    conn.commit()
    conn.close()


# -------------------------------------------------
# logs.db
# -------------------------------------------------

def create_logs_database() -> None:
    conn = logs_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            server TEXT,
            username TEXT,
            level TEXT,
            action TEXT,
            details TEXT
        )
    """)

    # Indizes für schnelle Filterung
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_server ON logs(server)")

    conn.commit()
    conn.close()


def write_log(
    server: str | None,
    username: str | None,
    level: str,
    action: str,
    details: str,
) -> None:
    """Schreibt einen Logeintrag in die Log-Datenbank."""
    conn = logs_connection()
    try:
        conn.execute(
            """
            INSERT INTO logs (timestamp, server, username, level, action, details)
            VALUES (?, ?, ?, ?, ?, ?)
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
    finally:
        conn.close()


# -------------------------------------------------
# storage.db
# -------------------------------------------------

def create_storage_database() -> None:
    conn = storage_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server INTEGER NOT NULL,
            pool TEXT UNIQUE NOT NULL,
            filesystem TEXT,
            raid TEXT,
            mountpoint TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool TEXT,
            dataset TEXT,
            snapshot TEXT,
            created TEXT,
            used TEXT,
            referenced TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS smart_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disk TEXT,
            temperature INTEGER,
            health TEXT,
            created TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrub_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool TEXT,
            started TEXT,
            finished TEXT,
            duration TEXT,
            errors INTEGER,
            result TEXT
        )
    """)

    # Indizes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_storage_server ON storage(server)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_pool ON snapshots(pool)")

    conn.commit()
    conn.close()


# -------------------------------------------------
# backup.db
# -------------------------------------------------

def create_backup_database() -> None:
    conn = backup_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            size TEXT,
            status TEXT DEFAULT 'OK',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Index für schnelle Server-Filterung
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_backups_server ON backups(server_id)")

    conn.commit()
    conn.close()


# -------------------------------------------------
# Hilfsfunktionen für häufig verwendete DB-Operationen
# -------------------------------------------------

def get_server(server_id: int) -> sqlite3.Row | None:
    """Lädt einen Serverdatensatz anhand seiner ID."""
    conn = server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servers WHERE id=?", (server_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_server_by_name(name: str) -> sqlite3.Row | None:
    """Lädt einen Serverdatensatz anhand seines Namens."""
    conn = server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servers WHERE name=?", (name,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_all_servers() -> list[sqlite3.Row]:
    """Lädt alle Server."""
    conn = server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servers ORDER BY name")
        return cursor.fetchall()
    finally:
        conn.close()