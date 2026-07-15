import secrets
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi.responses import JSONResponse

from http.cookies import SimpleCookie

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
import bcrypt

from database import users_connection

# --- Konfiguration ---
# Pfad zur Datenbank (relativ zum Projektroot)
BASE_DIR = Path(__file__).resolve().parent

# Session Konfiguration
SESSION_COOKIE_NAME = "gatecore_session"
SESSION_EXPIRY_SECONDS = 86400  # 24 Stunden
SESSION_EXPIRY_MILLIS = 86400000

# --- Typen ---

from models import (
    LoginData,
    User,
    CurrentUser
)

# --- Passwort-Management ---

def hash_password(password: str) -> str:
    """
    Hashen eines Passworts mit bcrypt.
    
    Args:
        password: Klartextpasswort.
    
    Returns:
        Hash-Wert (str).
    """
    # Salt-Faktor 12 ist ein guter Standard für Sicherheit vs. Performance
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Prüfen ob ein Passwort zu einem Hash passt.
    
    Args:
        plain_password: Klartextpasswort.
        hashed_password: Hash-Wert.
    
    Returns:
        True wenn es passt, sonst False.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- Datenbank-Hilfsfunktionen ---

def get_db_connection(db_path: Path) -> sqlite3.Connection:
    """
    Erzeugt eine Verbindung zur SQLite-Datenbank.
    
    Args:
        db_path: Pfad zur Datenbankdatei.
    
    Returns:
        sqlite3.Connection Objekt.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Ermöglicht row['column'] Zugriff
    return conn

def execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> sqlite3.Cursor:
    """
    Führt eine SQL-Abfrage aus.
    
    Args:
        conn: Datenbankverbindung.
        query: SQL-Statement.
        params: Parameter für die Abfrage.
    
    Returns:
        sqlite3.Cursor.
    """
    cursor = conn.execute(query, params)
    return cursor

def fetch_one(conn: sqlite3.Connection, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    """
    Führt eine Abfrage aus und gibt die erste Zeile zurück.
    
    Args:
        conn: Datenbankverbindung.
        query: SQL-Statement.
        params: Parameter.
    
    Returns:
        sqlite3.Row oder None.
    """
    cursor = execute_query(conn, query, params)
    return cursor.fetchone()

def fetch_all(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[sqlite3.Row]:
    cursor = conn.execute(query, params)
    return cursor.fetchall()

# --- Session-Management ---

def create_session(username: str, token: str) -> bool:
    """
    Erstellt eine neue Session in der sessions.db.
    
    Args:
        username: Benutzername der Session.
        token: Einzigartiger Session-Token.
    
    Returns:
        True wenn erfolgreich, False sonst.
    """
    conn = users_connection()
    try:
        # Prüfen ob Token existiert (Race Condition vermeiden)
        existing = fetch_one(conn, "SELECT * FROM sessions WHERE token = ?", (token,))
        if existing:
            # Token existiert bereits, wir überschreiben es (Rolling Session)
            # oder wir löschen und neu erstellen. Hier überschreiben wir einfach.
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))

        now = int(time.time())
        expires = now + SESSION_EXPIRY_SECONDS
        
        conn.execute(
            "INSERT INTO sessions (token, username, expires) VALUES (?, ?, ?)",
            (token, username, expires)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def delete_session(token: str) -> bool:
    """
    Löscht eine Session basierend auf dem Token.
    
    Args:
        token: Der Session-Token.
    
    Returns:
        True wenn gelöscht, False wenn nicht gefunden.
    """
    conn = users_connection()
    try:
        cursor = conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count > 0
    finally:
        conn.close()

def cleanup_sessions() -> int:
    """
    Entfernt alle abgelaufenen Sessions aus der Datenbank.
    
    Returns:
        Anzahl der gelöschten Einträge.
    """
    conn = users_connection()
    try:
        # Abfrage für abgelaufene Sessions
        now = int(time.time())
        cursor = conn.execute(
            "DELETE FROM sessions WHERE expires < ?",
            (now,)
        )
        count = cursor.rowcount
        conn.commit()
        return count
    finally:
        conn.close()

# --- Benutzer-Management ---

def create_user(username: str, password: str, role: str) -> bool:
    """
    Erstellt einen neuen Benutzer in users.db.
    
    Args:
        username: Benutzername.
        password: Passwort (wird automatisch gehasht).
        role: Rolle (z.B. 'Administrator', 'User').
    
    Returns:
        True wenn erfolgreich, False bei Duplikat.
    """
    conn = users_connection()
    try:
        # Passwort hashen
        hashed_pw = hash_password(password)
        
        # Prüfen ob Benutzer existiert
        existing = fetch_one(conn, "SELECT * FROM users WHERE username = ?", (username,))
        if existing:
            return False
        
        # Benutzer erstellen
        conn.execute(
            """
            INSERT INTO users
            (username,password,role)
            VALUES (?,?,?)
            """,
            (username, hashed_pw, role)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_current_user(token: str) -> Optional[CurrentUser]:
    """
    Validiert ein Session-Token und gibt den Benutzer zurück.
    
    Args:
        token: Der Session-Token.
    
    Returns:
        CurrentUser Objekt oder None.
    """
    conn = users_connection()
    try:
        # Session prüfen
        session = fetch_one(conn, "SELECT * FROM sessions WHERE token = ?", (token,))
        if not session:
            return None
        
        # Ablaufzeit prüfen
        if session['expires'] < int(time.time()):
            return None
        
        # Benutzer laden
        user = fetch_one(conn, "SELECT * FROM users WHERE username = ?", (session['username'],))
        if not user:
            # Benutzer existiert nicht mehr (z.B. gelöscht)
            # Optional: Session hier auch löschen
            return None
        
        return CurrentUser(username=user['username'], role=user['role'])
    finally:
        conn.close()

# --- API Endpoints ---

def login(app: FastAPI) -> None:
    """
    Endpoint für das Login.
    
    POST /api/login
    """
    @app.post("/api/login", response_model=Dict[str, Any])
    async def api_login(request_data: LoginData):
        # Datenbank Verbindung
        conn = users_connection()
        try:
            # Benutzer suchen
            user = fetch_one(conn, "SELECT * FROM users WHERE username = ?", (request_data.username,))
            if not user:
                raise HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")
            
            # Passwort prüfen
            if not verify_password(request_data.password, user['password']):
                raise HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")
            
            # Session-Token generieren
            token = secrets.token_urlsafe(32)
            
            # Session speichern
            create_session(user['username'], token)
            
            # Cookie setzen
            response = JSONResponse(
                content={"success": True}
            )

            set_cookie(response, token)

            return response
        finally:
            conn.close()

    return api_login

def logout(app: FastAPI) -> None:
    """
    Endpoint für das Logout.
    
    POST /api/logout
    """
    @app.post("/api/logout", response_model=Dict[str, Any])
    async def api_logout(request: Request, response: Response):
        # Token aus Cookie lesen
        cookies = request.cookies
        token = cookies.get(SESSION_COOKIE_NAME)
        
        if token:
            delete_session(token)
        
        # Cookie löschen
        response = JSONResponse(
            content={"success": True}
        )

        delete_cookie(response, SESSION_COOKIE_NAME)

        return response

    return api_logout

def get_user_info(app: FastAPI) -> None:
    """
    Endpoint für Benutzerinformationen.
    
    GET /api/user
    """
    @app.get("/api/user", response_model=CurrentUser)
    async def api_get_user(request: Request):
        # Cookie lesen
        cookies = request.cookies
        token = cookies.get(SESSION_COOKIE_NAME)
        
        if not token:
            raise HTTPException(status_code=401, detail="Session Token fehlt")
        
        # User laden
        current_user = get_current_user(token)
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Session ungültig oder abgelaufen")
        
        return current_user

    return api_get_user

def require_login(request: Request):

    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401)

    current_user = get_current_user(token)

    if current_user is None:
        raise HTTPException(status_code=401)

    return current_user
    
    return user_dependency

# --- FastAPI Cookie-Hilfen ---

def set_cookie(response: Response, token: str) -> None:
    """
    Setzt ein HttpOnly Cookie im Response.
    """
    cookie = SimpleCookie()
    cookie[SESSION_COOKIE_NAME] = token
    cookie[SESSION_COOKIE_NAME]["httponly"] = "True"
    cookie[SESSION_COOKIE_NAME]["samesite"] = "lax"
    cookie[SESSION_COOKIE_NAME]["max-age"] = str(SESSION_EXPIRY_SECONDS)
    cookie[SESSION_COOKIE_NAME]["secure"] = "False" # secure=False laut Anforderung
    cookie[SESSION_COOKIE_NAME]["path"] = "/"
    response.set_cookie(SESSION_COOKIE_NAME, token, 
                        httponly=True, 
                        samesite="lax", 
                        max_age=SESSION_EXPIRY_SECONDS, 
                        secure=False,
                        path="/")

def delete_cookie(response: Response, cookie_name: str) -> None:
    """
    Löscht ein Cookie im Response.
    """
    response.delete_cookie(cookie_name, path="/")

