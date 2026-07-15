from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from auth import (
    require_login,
    login,
    logout,
    get_user_info,
    cleanup_sessions
)

from database import (
    init_database,
    lxc_connection,
    server_connection
)

from models import AddServer

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

# Abgelaufene Sessions entfernen
cleanup_sessions()

# -------------------------------------------------
# Auth API registrieren
# -------------------------------------------------

login(app)
logout(app)
get_user_info(app)

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
# Login
# -------------------------------------------------

@app.get("/")
async def login_page():
    return FileResponse(
        BASE_DIR / "templates" / "login.html"
    )


@app.get("/login")
async def login_page_alias():
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


@app.get("/panel/")
async def panel_slash(user=Depends(require_login)):
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

@app.get("/panel/server/add")
async def server_add(user=Depends(require_login)):

    return FileResponse(

        BASE_DIR /
        "templates/panel/server_add.html"

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
# API
# -------------------------------------------------

@app.get("/api/lxc/count")
async def lxc_count(user=Depends(require_login)):

    conn = lxc_connection()

    try:

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM lxc")

        count = cursor.fetchone()[0]

        return {
            "count": count
        }

    finally:
        conn.close()

@app.post("/api/server/add")
async def add_server(
    data: AddServer,
    user=Depends(require_login)
):

    conn = server_connection()

    conn.execute(
        """
        INSERT INTO servers
        (
            name,
            host,
            port,
            username
        )

        VALUES
        (?,?,?)
        """,
        (
            data.hostname,
            data.ip,
            data.port,
            data.username
        )
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Server gespeichert."
    }

# -------------------------------------------------
# Starten
# -------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )