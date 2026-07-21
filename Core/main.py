###########################################################################
# File: Core/main.py
# Main Code from GateCore Linux Server Management
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-20
# Communion: GateCore01
############################################################################
# !/bin/python

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from auth import cleanup_sessions, login, logout, get_user_info
from database import init_database, write_log, lxc_connection
from routes import router  # ← der neue Router aus routes.py

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="GateCore",
    description="GateCore Linux Server Management",
    version="0.0.3"
)

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# Template Konfiguration
# -------------------------------------------------
TEMPLATE_REPO = "git://git.code.sf.net/p/gatecore-template/gatecore-template gatecore-template-gatecore-template"
TEMPLATE_PATH = BASE_DIR / "cache" / "templates"

# -------------------------------------------------
# Template Sync (asynchron – blockiert nicht mehr!)
# -------------------------------------------------
async def sync_github_templates():
    """Synchronisiert Templates von GitHub – jetzt asynchron mit to_thread."""
    try:
        # Git-Kommando in separatem Thread ausführen (blockiert nicht den Event-Loop)
        if TEMPLATE_PATH.exists():
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", "-C", str(TEMPLATE_PATH), "pull"],
                check=True,
                capture_output=True,
                text=True
            )
        else:
            TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", "clone", TEMPLATE_REPO, str(TEMPLATE_PATH)],
                check=True,
                capture_output=True,
                text=True
            )
    except Exception as exc:
        write_log(
            None,
            None,
            "error",
            "template_sync",
            f"Repository konnte nicht synchronisiert werden: {exc}"
        )
        return

    # Templates aus Verzeichnis lesen (diese Operation ist schnell und kann synchron bleiben)
    templates = []
    for file in TEMPLATE_PATH.rglob("*"):
        if not file.is_file():
            continue
        relative = file.relative_to(TEMPLATE_PATH)
        templates.append({
            "name": file.stem,
            "path": str(relative),
            "type": "file",
            "repo_url": TEMPLATE_REPO,
            "download_url": str(file)
        })

    # Datenbank-Update mit Context-Manager (automatisches Schließen)
    with lxc_connection() as conn:
        cursor = conn.cursor()
        names = []
        for template in templates:
            names.append(template["name"])
            cursor.execute(
                """
                INSERT INTO lxc_templates
                (name, path, type, repo_url, download_url, last_synced)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET
                    path=excluded.path,
                    type=excluded.type,
                    repo_url=excluded.repo_url,
                    download_url=excluded.download_url,
                    last_synced=excluded.last_synced
                """,
                (
                    template["name"],
                    template["path"],
                    template["type"],
                    template["repo_url"],
                    template["download_url"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        if names:
            cursor.execute(
                f"DELETE FROM lxc_templates WHERE name NOT IN ({','.join('?' * len(names))})",
                tuple(names)
            )
        conn.commit()
        # conn.close() entfällt – Context-Manager macht das automatisch!


async def sync_github_templates_loop() -> None:
    """Hält den GitHub-Template-Sync im Hintergrund laufend (alle 24 Stunden)."""
    await sync_github_templates()
    while True:
        await asyncio.sleep(24 * 60 * 60)
        await sync_github_templates()


# -------------------------------------------------
# Datenbank & Sessions initialisieren
# -------------------------------------------------
init_database()
cleanup_sessions()


# -------------------------------------------------
# Auth‑Routen registrieren
# -------------------------------------------------
login(app)
logout(app)
get_user_info(app)


# -------------------------------------------------
# Hintergrund‑Task starten
# -------------------------------------------------
@app.on_event("startup")
async def start_template_sync_tasks() -> None:
    """Startet den Hintergrund-Task für Template-Sync."""
    asyncio.create_task(sync_github_templates_loop())


# -------------------------------------------------
# Statische Dateien
# -------------------------------------------------
app.mount("/css", StaticFiles(directory=BASE_DIR / "static" / "css"), name="css")
app.mount("/js", StaticFiles(directory=BASE_DIR / "static" / "js"), name="js")
app.mount("/svg", StaticFiles(directory=BASE_DIR / "static" / "svg"), name="svg")
app.mount("/i18n", StaticFiles(directory=BASE_DIR / "static" / "i18n"), name="i18n")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


# -------------------------------------------------
# Router einbinden (alle Seiten & API‑Routen)
# -------------------------------------------------
app.include_router(router)


# -------------------------------------------------
# Start (für direkte Ausführung)
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )