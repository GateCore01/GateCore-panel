from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth import require_login
from database import init_database

from database import lxc_connection

# -------------------------------------------------
# FastAPI
# -------------------------------------------------

app = FastAPI(
    title="GateCore",
    description="GateCore Linux Server Management",
    version="0.1.0"
)

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# Datenbank initialisieren
# -------------------------------------------------

init_database()

# -------------------------------------------------
# Statische Dateien
# -------------------------------------------------

app.mount(
    "/css",
    StaticFiles(directory=BASE_DIR / "static" / "css"),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=BASE_DIR / "static" / "js"),
    name="js"
)

app.mount(
    "/svg",
    StaticFiles(directory=BASE_DIR / "static" / "svg"),
    name="svg"
)

app.mount(
    "/images",
    StaticFiles(directory=BASE_DIR / "static" / "images"),
    name="images"
)

# -------------------------------------------------
# Loginseite
# -------------------------------------------------

@app.get("/")
async def login_page():
    return FileResponse(
        BASE_DIR / "templates" / "login.html"
    )

# -------------------------------------------------
# Dashboard
# -------------------------------------------------

@app.get("/panel")
async def panel(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "index.html"
    )

# -------------------------------------------------
# Benutzer
# -------------------------------------------------

@app.get("/panel/users")
async def users(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "users.html"
    )

# -------------------------------------------------
# Server
# -------------------------------------------------

@app.get("/panel/server")
async def server(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "server.html"
    )

# -------------------------------------------------
# Einstellungen
# -------------------------------------------------

@app.get("/panel/settings")
async def settings(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "settings.html"
    )

# -------------------------------------------------
# Logs
# -------------------------------------------------

@app.get("/panel/logs")
async def logs(user=Depends(require_login)):
    return FileResponse(
        BASE_DIR / "templates" / "panel" / "logs.html"
    )
    
# -------------------------------------------------
# LXC
# -------------------------------------------------
@app.get("/api/lxc/count")
async def lxc_count(user=Depends(require_login)):

    conn = lxc_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM lxc")

    count = cursor.fetchone()[0]

    conn.close()

    return {
        "count": count
    }