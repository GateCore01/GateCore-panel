from pydantic import BaseModel, Field


# -------------------------------------------------
# Login
# -------------------------------------------------

class LoginData(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=1)


# -------------------------------------------------
# Benutzer
# -------------------------------------------------

class User(BaseModel):
    id: int
    username: str
    role: str


# -------------------------------------------------
# Server
# -------------------------------------------------

class Server(BaseModel):
    id: int
    name: str
    host: str
    port: int
    username: str
    description: str | None = None


# -------------------------------------------------
# LXC
# -------------------------------------------------

class LXC(BaseModel):
    id: int
    server_id: int
    vmid: int
    name: str
    status: str
    node: str


# -------------------------------------------------
# API-Antworten
# -------------------------------------------------

class Message(BaseModel):
    success: bool
    message: str


class CurrentUser(BaseModel):
    username: str
    role: str