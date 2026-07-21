###########################################################################
# File: Core/models.py
# Pydantic Models
###########################################################################
from pydantic import BaseModel, Field
from typing import List, Optional

# Login
class LoginData(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    password: str = Field(..., min_length=1)

# Benutzer
class User(BaseModel):
    id: int
    username: str

class AddUser(BaseModel):
    username: str
    password: str

class ChangePassword(BaseModel):
    id: str
    password: str

# Server
class Server(BaseModel):
    id: int
    name: str
    host: str
    port: int
    username: str
    description: Optional[str] = None

class AddServer(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=128)
    ip: str = Field(..., min_length=7, max_length=45)
    username: str = Field(..., min_length=1, max_length=64)
    password: Optional[str] = None
    private_key: Optional[str] = None
    port: int = 22

# Docker
class AddDockerContainer(BaseModel):
    name: str
    server_id: int
    image: str
    command: str = ""
    env: List[str] = []
    volumes: List[str] = []
    ports: List[str] = []
    detach: bool = True

class DockerContainer(BaseModel):
    id: int
    name: str
    server_id: int
    image: str
    status: str
    command: str
    created: str

# BTRFS Storage
class CreateBtrfsPool(BaseModel):
    name: str
    server_id: int
    mountpoint: str
    raid_level: str  # single, raid0, raid1, raid10, raid5, raid6
    devices: List[str]

class BtrfsPool(BaseModel):
    id: int
    name: str
    server_id: int
    mountpoint: str
    raid_level: str
    devices: str  # JSON
    created: str

class CreateBtrfsSubvolume(BaseModel):
    pool_id: int
    name: str

class CreateBtrfsSnapshot(BaseModel):
    subvolume_id: int
    snapshot_name: str

# Allgemeine Antworten
class Message(BaseModel):
    success: bool
    message: str

class CurrentUser(BaseModel):
    username: str

# Backup
class BackupAction(BaseModel):
    server_id: int