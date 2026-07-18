import sqlite3
from pathlib import Path

# -------------------------------------------------
# Pfade
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

USERS_DB = DATABASE_DIR / "users.db"
SERVER_DB = DATABASE_DIR / "server.db"
LXC_DB = DATABASE_DIR / "lxc.db"
DB_PATH_LOGS = BASE_DIR / "database" / "logs.db"
DB_PATH_STORAGE = BASE_DIR / "database" / "storage.db"

# -------------------------------------------------
# Verbindungen
# -------------------------------------------------

def user_connection():
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    return conn


def server_connection():
    conn = sqlite3.connect(SERVER_DB)
    conn.row_factory = sqlite3.Row
    return conn


def lxc_connection():
    conn = sqlite3.connect(LXC_DB)
    conn.row_factory = sqlite3.Row
    return conn

def storage_connection():

    conn = sqlite3.connect(DB_PATH_STORAGE)

    conn.row_factory = sqlite3.Row

    return conn

# -------------------------------------------------
# Datenbank erstellen
# -------------------------------------------------

def init_database():

    create_users_database()
    create_server_database()
    create_lxc_database()

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

def create_server_database():

    conn = server_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            host TEXT NOT NULL,

            port INTEGER DEFAULT 22,

            username TEXT NOT NULL,

            description TEXT,

            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# lxc.db
# -------------------------------------------------

def create_lxc_database():

    conn = lxc_connection()

    conn.execute("""

    CREATE TABLE IF NOT EXISTS lxc (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        server TEXT NOT NULL,

        vmid INTEGER NOT NULL,

    )

    """)

    conn.commit()

    conn.close()
    
    
# Abfrage für get-server
def get_server(server_id: int):

    conn = server_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM servers WHERE id=?",
        (server_id,)
    )

    server = cursor.fetchone()

    conn.close()

    return server

# -------------------------------------------------
# logs.db
# -------------------------------------------------
def logs_connection():

    conn = sqlite3.connect(DB_PATH_LOGS)

    conn.row_factory = sqlite3.Row

    return conn

conn = logs_connection()

conn.execute("""

CREATE TABLE IF NOT EXISTS logs(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    timestamp TEXT NOT NULL,

    server TEXT,

    username TEXT,

    level TEXT,

    action TEXT,

    details TEXT

)

""")

conn.commit()

conn.close()

from datetime import datetime

def write_log(server, username, level, action, details):

    conn = logs_connection()

    conn.execute("""

        INSERT INTO logs
        (

            timestamp,

            server,

            username,

            level,

            action,

            details

        )

        VALUES

        (?,?,?,?,?,?)

    """,(

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        server,

        username,

        level,

        action,

        details

    ))

    conn.commit()

    conn.close()
    
# -------------------------------------------------
# storage.db
# -------------------------------------------------
conn = storage_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS storage(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    server INTEGER NOT NULL,

    pool TEXT UNIQUE NOT NULL,

    filesystem TEXT,

    raid TEXT,

    mountpoint TEXT

)
""")

conn.commit()

conn.close()

# -------------------------------------------------
# Snapshots
# -------------------------------------------------
conn = storage_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS snapshots(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    pool TEXT,

    dataset TEXT,

    snapshot TEXT,

    created TEXT,

    used TEXT,

    referenced TEXT

)
""")

conn.commit()

conn.close()

# -------------------------------------------------
# SMART History
# -------------------------------------------------
conn = storage_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS smart_history(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    disk TEXT,

    temperature INTEGER,

    health TEXT,

    created TEXT

)
""")

conn.commit()

conn.close()

# -------------------------------------------------
# Scrub History
# -------------------------------------------------
conn = storage_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS scrub_history(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    pool TEXT,

    started TEXT,

    finished TEXT,

    duration TEXT,

    errors INTEGER,

    result TEXT

)
""")

conn.commit()

conn.close()