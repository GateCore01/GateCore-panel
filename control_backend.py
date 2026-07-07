#!/usr/bin/env python3
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
SERVERS_CONFIG_PATH = CONFIG_DIR / "servers.json"


def load_servers():
    if not SERVERS_CONFIG_PATH.exists():
        return []
    with SERVERS_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_servers(servers):
    with SERVERS_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(servers, handle, indent=2)
        handle.write("\n")


class ControlHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        if self.path != "/api/servers":
            self.send_json(404, {"success": False, "message": "Endpoint not found"})
            return

        if self.command == "GET":
            self.send_json(200, load_servers())
            return

        if self.command == "POST":
            self.handle_create()
            return

        if self.command == "DELETE":
            self.handle_delete()
            return

        self.send_json(405, {"success": False, "message": "Method not allowed"})

    def handle_create(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        servers = load_servers()
        new_server = {
            "id": str(len(servers) + 1),
            "name": (data.get("name") or "").strip(),
            "host": (data.get("host") or "").strip(),
            "path": (data.get("path") or "").strip(),
            "type": data.get("type") or data.get("serverType") or "linux",
            "system": data.get("system") or data.get("type") or data.get("serverType") or "linux",
            "serverType": data.get("serverType") or data.get("type") or "linux",
            "startCommand": (data.get("startCommand") or "").strip(),
            "systemdCommand": (data.get("systemdCommand") or data.get("serviceStartCommand") or data.get("controlCommand") or "").strip(),
            "serviceStartCommand": (data.get("serviceStartCommand") or data.get("systemdCommand") or "").strip(),
            "controlCommand": (data.get("controlCommand") or data.get("systemdCommand") or "").strip(),
            "autostart": bool(data.get("autostart")),
            "onlineStatus": (data.get("onlineStatus") or "offline").strip().lower(),
            "status": (data.get("status") or "offline").strip().lower(),
            "createdAt": data.get("createdAt") or ""
        }

        if not new_server["name"] or not new_server["host"] or not new_server["path"]:
            self.send_json(400, {"success": False, "message": "Pflichtfelder fehlen"})
            return

        servers.append(new_server)
        save_servers(servers)
        self.send_json(200, {"success": True, "servers": load_servers()})

    def handle_delete(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        server_id = (data.get("id") or "").strip()
        if not server_id:
            self.send_json(400, {"success": False, "message": "Server-ID ist erforderlich"})
            return

        servers = load_servers()
        filtered_servers = [server for server in servers if str(server.get("id", "")).strip() != server_id]
        save_servers(filtered_servers)
        self.send_json(200, {"success": True, "servers": filtered_servers})

    def send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", 8001), ControlHandler)
    print("GateCore Control-Backend läuft auf http://0.0.0.0:8001")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
