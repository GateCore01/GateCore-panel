###########################################################################
# File: Core/models.py
# All Classes for the API-Models are defined here.
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-19
# Communion: GateCore01
############################################################################
# !/bin/python

# import the required modules
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

class AddUser(BaseModel):
    username: str
    password: str

class ChangePassword(BaseModel):

    id: str

    password: str

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

class AddServer(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=128)
    ip: str = Field(..., min_length=7, max_length=45)
    username: str = Field(..., min_length=1, max_length=64)
    password: str | None = None
    private_key: str | None = None
    port: int = 22

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
    
class AddLXC(BaseModel):

    name: str

    server: str

    vmid: int

    template: str = "download"

class SourceForge_templates(BaseModel):
    name: str
    path: str | None = None
    type: str = "file"
    repo_url: str = "https://sourceforge.net/projects/gatecore-template/files/"
    download_url: str | None = None
    
class UpdateLXC(BaseModel):

    id: int

    name: str

    server: str

    vmid: int
    
# -------------------------------------------------
# Logs
# -------------------------------------------------
class LogEntry(BaseModel):

    server: str

    level: str

    action: str

    details: str
    
# -------------------------------------------------
# Storage
# -------------------------------------------------

class CreateStorage(BaseModel):

    name: str
    server: int
    pool: str
    filesystem: str
    raid: str
    mountpoint: str

class UpdateStorage(BaseModel):

    name: str
    new_name: str

    filesystem: str
    raid: str
    mountpoint: str

# -------------------------------------------------
# Allgemeine Aktionen
# -------------------------------------------------

class StorageAction(BaseModel):

    pool: str

class StorageSmartTest(BaseModel):

    disk: str
    type: str

# -------------------------------------------------
# Snapshots
# -------------------------------------------------

class SnapshotCreate(BaseModel):

    pool: str
    dataset: str
    name: str

class SnapshotRename(BaseModel):

    pool: str
    old_name: str
    new_name: str

class SnapshotClone(BaseModel):

    pool: str
    snapshot: str
    clone: str

# -------------------------------------------------
# Scrub
# -------------------------------------------------

class ScrubAction(BaseModel):

    pool: str