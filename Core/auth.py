###########################################################################
# File: Core/auth.py
# Authentifizierungs- und Session-Management
###########################################################################
import secrets
import time
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi.responses import JSONResponse
from http.cookies import SimpleCookie
from fastapi import FastAPI, Request, Response, Depends, HTTPException
import bcrypt
from database import user_connection

BASE_DIR = Path(__file__).resolve().parent
SESSION_COOKIE_NAME = "gatecore_session"
SESSION_EXPIRY_SECONDS = 86400

from models import LoginData, CurrentUser

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_db_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()):
    return conn.execute(query, params)

def fetch_one(conn: sqlite3.Connection, query: str, params: tuple = ()):
    cursor = execute_query(conn, query, params)
    return cursor.fetchone()

def fetch_all(conn: sqlite3.Connection, query: str, params: tuple = ()):
    cursor = conn.execute(query, params)
    return cursor.fetchall()

def create_session(username: str, token: str) -> bool:
    conn = user_connection()
    try:
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
    conn = user_connection()
    try:
        cursor = conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def cleanup_sessions() -> int:
    conn = user_connection()
    try:
        now = int(time.time())
        cursor = conn.execute("DELETE FROM sessions WHERE expires < ?", (now,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def get_current_user(token: str) -> Optional[CurrentUser]:
    conn = user_connection()
    try:
        session = fetch_one(conn, "SELECT * FROM sessions WHERE token = ?", (token,))
        if not session or session['expires'] < int(time.time()):
            return None
        user = fetch_one(conn, "SELECT * FROM users WHERE username = ?", (session['username'],))
        if not user:
            return None
        return CurrentUser(username=user['username'])
    finally:
        conn.close()

def require_login(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401)
    current_user = get_current_user(token)
    if current_user is None:
        raise HTTPException(status_code=401)
    return current_user

def login(app: FastAPI):
    @app.post("/api/login")
    async def api_login(request_data: LoginData):
        conn = user_connection()
        try:
            user = fetch_one(conn, "SELECT * FROM users WHERE username = ?", (request_data.username,))
            if not user or not verify_password(request_data.password, user['password']):
                raise HTTPException(status_code=401, detail="Benutzername oder Passwort falsch")
            token = secrets.token_urlsafe(32)
            create_session(user['username'], token)
            response = JSONResponse(content={"success": True})
            response.set_cookie(
                SESSION_COOKIE_NAME, token,
                httponly=True, samesite="lax",
                max_age=SESSION_EXPIRY_SECONDS, secure=False, path="/"
            )
            return response
        finally:
            conn.close()

def logout(app: FastAPI):
    @app.post("/api/logout")
    async def api_logout(request: Request, response: Response):
        token = request.cookies.get(SESSION_COOKIE_NAME)
        if token:
            delete_session(token)
        response = JSONResponse(content={"success": True})
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")
        return response

def get_user_info(app: FastAPI):
    @app.get("/api/user")
    async def api_get_user(request: Request):
        token = request.cookies.get(SESSION_COOKIE_NAME)
        if not token:
            raise HTTPException(status_code=401)
        user = get_current_user(token)
        if not user:
            raise HTTPException(status_code=401)
        return user