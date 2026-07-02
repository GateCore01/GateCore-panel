#!/usr/bin/env python3
import json
import secrets
import subprocess
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_ROOT / "panel"
CONFIG_DIR = PROJECT_ROOT / "config"
AUTH_CONFIG_PATH = CONFIG_DIR / "auth-config.json"
USERS_CONFIG_PATH = CONFIG_DIR / "users.json"
HOSTS_CONFIG_PATH = CONFIG_DIR / "hosts.json"
SERVERS_CONFIG_PATH = CONFIG_DIR / "servers.json"
SESSION_COOKIE_NAME = "gatecore_session"
CONTROL_BACKEND_URL = "http://127.0.0.1:8001"
SESSIONS = {}


def load_auth_config():
    with AUTH_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


AUTH_CONFIG = load_auth_config()


def load_users():
    if not USERS_CONFIG_PATH.exists():
        return []
    with USERS_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_users(users):
    with USERS_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(users, handle, indent=2)
        handle.write("\n")


def load_hosts():
    if not HOSTS_CONFIG_PATH.exists():
        return []
    with HOSTS_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_hosts(hosts):
    with HOSTS_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(hosts, handle, indent=2)
        handle.write("\n")


def load_servers():
    if not SERVERS_CONFIG_PATH.exists():
        return []
    with SERVERS_CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_servers(servers):
    with SERVERS_CONFIG_PATH.open("w", encoding="utf-8") as handle:
        json.dump(servers, handle, indent=2)
        handle.write("\n")


def distribute_state_to_hosts():
    hosts = load_hosts()
    servers = load_servers()
    payload = {"hosts": hosts, "servers": servers}
    results = []

    for host in hosts:
        address = str(host.get("address", "")).strip()
        if not address:
            continue

        ssh_user = str(host.get("sshUser") or host.get("user") or "root").strip() or "root"
        ssh_port = str(host.get("sshPort") or "22").strip() or "22"
        remote_dir = str(host.get("remoteDir") or "/tmp/gatecore-panel").strip() or "/tmp/gatecore-panel"
        remote_file = str(host.get("remoteFile") or f"{remote_dir}/state.json").strip() or f"{remote_dir}/state.json"
        script = (
            "import json, pathlib;"
            f"pathlib.Path({remote_dir!r}).mkdir(parents=True, exist_ok=True);"
            f"pathlib.Path({remote_file!r}).write_text({json.dumps(payload, indent=2)!r}, encoding='utf-8')"
        )

        try:
            subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no", "-p", ssh_port, f"{ssh_user}@{address}", "python3", "-c", script],
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            results.append({"host": address, "success": True})
        except Exception as exc:
            results.append({"host": address, "success": False, "message": str(exc)})

    return results


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/api/login", "/api/logout", "/api/auth/check", "/api/users", "/api/hosts", "/api/servers", "/api/control/servers"}:
            self.handle_api(path)
            return

        if self.requires_auth(path):
            if not self.is_authenticated():
                self.send_response(302)
                self.send_header("Location", "/index.html")
                self.send_header("Set-Cookie", f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

        self.serve_static(path)

    def handle_api(self, path):
        if path == "/api/login" and self.command == "POST":
            self.handle_login()
            return

        if path == "/api/logout":
            self.handle_logout()
            return

        if path == "/api/auth/check":
            self.send_json(200, {"authenticated": self.is_authenticated()})
            return

        if path == "/api/users":
            if not self.is_authenticated():
                self.send_json(401, {"success": False, "message": "Nicht autorisiert"})
                return
            if self.command == "GET":
                self.send_json(200, load_users())
            elif self.command == "POST":
                self.handle_users_update()
            else:
                self.send_json(405, {"success": False, "message": "Method not allowed"})
            return

        if path == "/api/hosts":
            if not self.is_authenticated():
                self.send_json(401, {"success": False, "message": "Nicht autorisiert"})
                return
            if self.command == "GET":
                self.send_json(200, load_hosts())
            elif self.command == "POST":
                self.handle_hosts_create()
            elif self.command == "DELETE":
                self.handle_hosts_delete()
            else:
                self.send_json(405, {"success": False, "message": "Method not allowed"})
            return

        if path in {"/api/servers", "/api/control/servers"}:
            if not self.is_authenticated():
                self.send_json(401, {"success": False, "message": "Nicht autorisiert"})
                return
            self.proxy_control_backend(path)
            return

        self.send_json(404, {"success": False, "message": "Endpoint not found"})

    def proxy_control_backend(self, path):
        method = self.command
        payload = None
        if method in {"POST", "DELETE"}:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
                return

        target_url = f"{CONTROL_BACKEND_URL}/api/servers"
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(target_url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = response.read().decode("utf-8")
                self.send_response(response.status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body.encode("utf-8"))
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", "ignore")
            self.send_response(error.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(error_body.encode("utf-8"))
        except Exception as error:
            self.send_json(502, {"success": False, "message": f"Control backend nicht erreichbar: {error}"})

    def handle_login(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        is_admin = username == AUTH_CONFIG.get("username") and password == AUTH_CONFIG.get("password")
        users = load_users()
        is_known_user = any(
            str(user.get("username", "")).strip() == username and str(user.get("password", "")) == password
            for user in users
        )

        if is_admin or is_known_user:
            session_id = secrets.token_urlsafe(24)
            SESSIONS[session_id] = username
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header(
                "Set-Cookie",
                f"{SESSION_COOKIE_NAME}={session_id}; Path=/; HttpOnly; SameSite=Lax; Max-Age=3600"
            )
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Login erfolgreich"}).encode("utf-8"))
        else:
            self.send_json(401, {"success": False, "message": "Ungültiger Benutzername oder Passwort"})

    def handle_logout(self):
        self.clear_session_cookie()
        self.send_json(200, {"success": True, "message": "Abgemeldet"})

    def handle_users_update(self):
        if not self.is_authenticated():
            self.send_json(401, {"success": False, "message": "Nicht autorisiert"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        users = data.get("users", [])
        if not isinstance(users, list):
            self.send_json(400, {"success": False, "message": "Ungültige Nutzerliste"})
            return

        save_users(users)
        self.send_json(200, {"success": True, "message": "Benutzer gespeichert"})

    def handle_hosts_create(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        if not isinstance(data, dict):
            self.send_json(400, {"success": False, "message": "Ungültiger Host"})
            return

        hosts = load_hosts()
        new_host = {
            "name": (data.get("name") or "").strip(),
            "address": (data.get("address") or "").strip(),
            "api": (data.get("api") or data.get("apiUrl") or "").strip(),
            "sshUser": (data.get("sshUser") or "").strip(),
            "sshPassword": (data.get("sshPassword") or "").strip(),
            "sshPort": str(data.get("sshPort") or "22").strip(),
            "storagePath": (data.get("storagePath") or "").strip(),
            "status": data.get("status") or "gespeichert"
        }

        if not new_host["name"] or not new_host["address"]:
            self.send_json(400, {"success": False, "message": "Name und Adresse sind erforderlich"})
            return

        if not any(str(host.get("address", "")).strip() == new_host["address"] for host in hosts):
            hosts.append(new_host)
            save_hosts(hosts)

        distribution = distribute_state_to_hosts()
        self.send_json(200, {"success": True, "hosts": load_hosts(), "distribution": distribution})

    def handle_hosts_delete(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        address = (data.get("address") or "").strip()
        if not address:
            self.send_json(400, {"success": False, "message": "Adresse ist erforderlich"})
            return

        hosts = load_hosts()
        filtered_hosts = [host for host in hosts if str(host.get("address", "")).strip() != address]
        save_hosts(filtered_hosts)
        distribution = distribute_state_to_hosts()
        self.send_json(200, {"success": True, "hosts": filtered_hosts, "distribution": distribution})

    def handle_servers_create(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"success": False, "message": "Ungültiges JSON"})
            return

        if not isinstance(data, dict):
            self.send_json(400, {"success": False, "message": "Ungültiger Server"})
            return

        servers = load_servers()
        autostart_value = data.get("autostart")
        if isinstance(autostart_value, bool):
            autostart = autostart_value
        elif isinstance(autostart_value, str):
            autostart = autostart_value.strip().lower() in {"1", "true", "yes", "ja", "on"}
        else:
            autostart = False

        online_status = (data.get("onlineStatus") or data.get("status") or "offline").strip().lower()
        if online_status not in {"online", "offline", "unknown"}:
            online_status = "unknown"

        new_server = {
            "id": str(len(servers) + 1),
            "name": (data.get("name") or "").strip(),
            "host": (data.get("host") or "").strip(),
            "path": (data.get("path") or "").strip(),
            "startCommand": (data.get("startCommand") or "").strip(),
            "autostart": autostart,
            "onlineStatus": online_status,
            "status": online_status,
            "createdAt": data.get("createdAt") or ""
        }

        if not new_server["name"] or not new_server["host"] or not new_server["path"] or not new_server["startCommand"]:
            self.send_json(400, {"success": False, "message": "Alle Server-Felder sind erforderlich"})
            return

        servers.append(new_server)
        save_servers(servers)
        distribution = distribute_state_to_hosts()
        self.send_json(200, {"success": True, "servers": load_servers(), "distribution": distribution})

    def handle_servers_delete(self):
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
        distribution = distribute_state_to_hosts()
        self.send_json(200, {"success": True, "servers": filtered_servers, "distribution": distribution})

    def requires_auth(self, path):
        public_paths = {
            "/",
            "/index.html",
            "/css/styles.css",
            "/js/auth.js",
            "/js/settings.js",
            "/config/auth-config.json",
            "/config/settings-config.json",
            "/api/login",
            "/api/auth/check",
            "/api/logout",
            "/api/users",
        }
        if path in public_paths:
            return False
        if path.startswith("/css/") or path.startswith("/js/") or path.startswith("/config/"):
            return False
        if path.startswith("/login-portal/"):
            return True
        return path in {"/panel.html", "/server.html", "/server-shell.html", "/host-shell.html", "/backup.html", "/user.html", "/hosts.html", "/settings.html"}

    def is_authenticated(self):
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return False
        for part in cookie_header.split(";"):
            if "=" in part:
                name, value = part.split("=", 1)
                if name.strip() == SESSION_COOKIE_NAME and value.strip() in SESSIONS:
                    return True
        return False

    def clear_session_cookie(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def serve_static(self, path):
        if path in {"/", "/index.html"}:
            file_path = ROOT_DIR / "index.html"
        elif path in {"/panel.html", "/server.html", "/server-shell.html", "/host-shell.html", "/backup.html", "/user.html", "/hosts.html", "/settings.html"}:
            alias_map = {
                "/panel.html": "login-portal/panel.html",
                "/server.html": "login-portal/server.html",
                "/server-shell.html": "login-portal/server-shell.html",
                "/host-shell.html": "login-portal/host-shell.html",
                "/backup.html": "login-portal/backup.html",
                "/user.html": "login-portal/user.html",
                "/hosts.html": "login-portal/hosts.html",
                "/settings.html": "login-portal/settings.html",
            }
            file_path = ROOT_DIR / alias_map[path]
        else:
            if path.startswith("/config/"):
                relative = path[len("/config/"):]
                file_path = CONFIG_DIR / relative
            else:
                clean_path = path.lstrip("/")
                if clean_path.startswith("login-portal/login-portal/"):
                    clean_path = clean_path.replace("login-portal/login-portal/", "login-portal/", 1)
                if clean_path.startswith("login-portal/"):
                    prefix = clean_path[len("login-portal/"):]
                    if prefix.startswith("css/") or prefix.startswith("js/"):
                        file_path = ROOT_DIR / prefix
                    else:
                        file_path = ROOT_DIR / "login-portal" / prefix
                else:
                    file_path = ROOT_DIR / clean_path

        if not file_path.exists() or file_path.is_dir():
            if file_path.with_suffix(".html").exists():
                file_path = file_path.with_suffix(".html")
            else:
                self.send_json(404, {"success": False, "message": "Datei nicht gefunden"})
                return

        try:
            content = file_path.read_bytes()
        except FileNotFoundError:
            self.send_json(404, {"success": False, "message": "Datei nicht gefunden"})
            return

        self.send_response(200)
        self.send_header("Cache-Control", "no-store")
        if file_path.suffix == ".css":
            self.send_header("Content-Type", "text/css; charset=utf-8")
        elif file_path.suffix == ".js":
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
        elif file_path.suffix == ".json":
            self.send_header("Content-Type", "application/json; charset=utf-8")
        elif file_path.suffix == ".html":
            self.send_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", 8000), AuthHandler)
    print("Auth-Server läuft auf http://0.0.0.0:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
