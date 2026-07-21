###########################################################################
# File: Core/database.py
# Database management for GateCore
###########################################################################
import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
import glob
import os.path
import shutil

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

USERS_DB = DATABASE_DIR / "users.db"
SERVER_DB = DATABASE_DIR / "server.db"
DOCKER_DB = DATABASE_DIR / "docker.db"
LOGS_DB = DATABASE_DIR / "logs.db"
STORAGE_DB = DATABASE_DIR / "storage.db"
BACKUP_DB = DATABASE_DIR / "backup.db"

DATABASE_SRC_DIR = BASE_DIR / "database-source"
DATABASE_SRC_DIR.mkdir(exist_ok=True)

for file in glob.glob(os.path.join(DATABASE_SRC_DIR, "*")):
    if file not in glob.glob(os.path.join(DATABASE_DIR, "*")):
        shutil.copy(file,DATABASE_DIR)

def _connect_with_wal(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA cache_size=-20000")
    return conn

def user_connection() -> sqlite3.Connection:
    return _connect_with_wal(USERS_DB)

def server_connection() -> sqlite3.Connection:
    return _connect_with_wal(SERVER_DB)

def docker_connection() -> sqlite3.Connection:
    return _connect_with_wal(DOCKER_DB)

def logs_connection() -> sqlite3.Connection:
    return _connect_with_wal(LOGS_DB)

def storage_connection() -> sqlite3.Connection:
    return _connect_with_wal(STORAGE_DB)

def backup_connection() -> sqlite3.Connection:
    return _connect_with_wal(BACKUP_DB)

@contextmanager
def get_db_connection(db_path: Path) -> Generator[sqlite3.Connection, None, None]:
    conn = _connect_with_wal(db_path)
    try:
        yield conn
    finally:
        conn.close()

def get_server_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(SERVER_DB) as conn:
        yield conn

def get_user_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(USERS_DB) as conn:
        yield conn

def get_docker_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(DOCKER_DB) as conn:
        yield conn

def get_logs_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(LOGS_DB) as conn:
        yield conn

def get_storage_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(STORAGE_DB) as conn:
        yield conn

def get_backup_db() -> Generator[sqlite3.Connection, None, None]:
    with get_db_connection(BACKUP_DB) as conn:
        yield conn

def init_database() -> None:
    create_users_database()
    create_server_database()
    create_docker_database()
    create_logs_database()
    create_storage_database()
    create_backup_database()

def create_users_database() -> None:
    conn = user_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires INTEGER NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_username ON sessions(username)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires)")
    conn.commit()
    conn.close()

def create_server_database() -> None:
    conn = server_connection()
    conn.execute("""
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_servers_name ON servers(name)")
    conn.commit()
    conn.close()

def create_docker_database() -> None:
    conn = docker_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS docker_containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            image TEXT NOT NULL,
            status TEXT DEFAULT 'unknown',
            command TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_docker_server ON docker_containers(server_id)")
    conn.commit()
    conn.close()

def create_logs_database() -> None:
    conn = logs_connection()
    conn.execute("""
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_server ON logs(server)")
    conn.commit()
    conn.close()

def create_storage_database() -> None:
    conn = storage_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS storage_pools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            server_id INTEGER NOT NULL,
            mountpoint TEXT NOT NULL,
            raid_level TEXT NOT NULL,
            devices TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS btrfs_subvolumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            is_snapshot INTEGER DEFAULT 0,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pool_id) REFERENCES storage_pools(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS btrfs_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subvolume_id INTEGER NOT NULL,
            snapshot_name TEXT NOT NULL,
            path TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subvolume_id) REFERENCES btrfs_subvolumes(id) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_storage_pools_server ON storage_pools(server_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_btrfs_subvolumes_pool ON btrfs_subvolumes(pool_id)")
    conn.commit()
    conn.close()

def create_backup_database() -> None:
    conn = backup_connection()
    conn.execute("""
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_backups_server ON backups(server_id)")
    conn.commit()
    conn.close()

def write_log(server: str | None, username: str | None, level: str, action: str, details: str) -> None:
    conn = logs_connection()
    try:
        conn.execute(
            "INSERT INTO logs (timestamp, server, username, level, action, details) VALUES (?,?,?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), server, username, level, action, details)
        )
        conn.commit()
    finally:
        conn.close()

def get_server(server_id: int) -> sqlite3.Row | None:
    conn = server_connection()
    try:
        return conn.execute("SELECT * FROM servers WHERE id=?", (server_id,)).fetchone()
    finally:
        conn.close()

def get_server_by_name(name: str) -> sqlite3.Row | None:
    conn = server_connection()
    try:
        return conn.execute("SELECT * FROM servers WHERE name=?", (name,)).fetchone()
    finally:
        conn.close()

def get_all_servers() -> list[sqlite3.Row]:
    conn = server_connection()
    try:
        return conn.execute("SELECT * FROM servers ORDER BY name").fetchall()
    finally:
        conn.close()
