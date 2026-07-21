###########################################################################
# File: Core/main.py
# Main Code from GateCore Linux Server Management
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-20
# Communion: GateCore01
############################################################################

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from auth import cleanup_sessions, login, logout, get_user_info
from database import init_database, write_log, docker_connection
from routes import router

app = FastAPI(
    title="GateCore",
    description="GateCore Linux Server Management",
    version="0.0.4"
)

BASE_DIR = Path(__file__).resolve().parent

# Docker Image Sync (optionaler Hintergrundtask)
async def sync_docker_images():
    """Regelmäßiger Abgleich von Docker-Images (Platzhalter)."""
    # Hier könnte man z.B. `docker pull` für häufig genutzte Images ausführen
    pass

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(sync_docker_images())

# Datenbank & Sessions initialisieren
init_database()
cleanup_sessions()

# Auth‑Routen
login(app)
logout(app)
get_user_info(app)

# Statische Dateien
app.mount("/css", StaticFiles(directory=BASE_DIR / "static" / "css"), name="css")
app.mount("/js", StaticFiles(directory=BASE_DIR / "static" / "js"), name="js")
app.mount("/svg", StaticFiles(directory=BASE_DIR / "static" / "svg"), name="svg")
app.mount("/i18n", StaticFiles(directory=BASE_DIR / "static" / "i18n"), name="i18n")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

# Router einbinden
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )