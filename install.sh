#!/bin/sh
#
# GateCore Panel installer
# Supported: Debian/Ubuntu, openSUSE, Rocky Linux/RHEL-compatible systems, FreeBSD

set -eu

APP_NAME="gatecore-panel"
APP_USER="${APP_USER:-gatecore}"
APP_GROUP="${APP_GROUP:-gatecore}"
PREFIX="${PREFIX:-/opt/gatecore-panel}"
REPO_URL="${REPO_URL:-https://github.com/GateCore01/GameServer-panel.git}"
AUTH_PORT="${AUTH_PORT:-8000}"
CONTROL_PORT="${CONTROL_PORT:-8001}"
SKIP_PACKAGES="${SKIP_PACKAGES:-0}"
FORCE_CONFIG="${FORCE_CONFIG:-0}"

log() {
  printf '%s\n' "==> $*"
}

warn() {
  printf '%s\n' "WARN: $*" >&2
}

die() {
  printf '%s\n' "ERROR: $*" >&2
  exit 1
}

need_root() {
  [ "$(id -u)" -eq 0 ] || die "Bitte als root ausfuehren, z. B. mit sudo ./install.sh"
}

detect_os() {
  OS_NAME="$(uname -s)"
  OS_ID=""
  OS_LIKE=""

  if [ "$OS_NAME" = "FreeBSD" ]; then
    OS_ID="freebsd"
    return
  fi

  if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    OS_ID="${ID:-}"
    OS_LIKE="${ID_LIKE:-}"
    return
  fi

  die "Betriebssystem konnte nicht erkannt werden."
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

install_packages() {
  [ "$SKIP_PACKAGES" = "1" ] && {
    log "Paketinstallation wird uebersprungen (SKIP_PACKAGES=1)."
    return
  }

  case "$OS_ID" in
    debian|ubuntu)
      log "Installiere Pakete mit apt..."
      apt-get update
      apt-get install -y python3 git openssh-client sshpass ca-certificates
      ;;
    opensuse*|sles)
      log "Installiere Pakete mit zypper..."
      zypper --non-interactive refresh
      zypper --non-interactive install python3 git openssh sshpass ca-certificates
      ;;
    rocky|rhel|almalinux|centos|fedora)
      log "Installiere Pakete mit dnf/yum..."
      if has_cmd dnf; then
        dnf install -y python3 git openssh-clients sshpass ca-certificates
      else
        yum install -y python3 git openssh-clients sshpass ca-certificates
      fi
      ;;
    freebsd)
      log "Installiere Pakete mit pkg..."
      pkg update
      pkg install -y python3 git sshpass ca_root_nss
      ;;
    *)
      case " $OS_LIKE " in
        *" debian "*)
          log "Installiere Pakete mit apt..."
          apt-get update
          apt-get install -y python3 git openssh-client sshpass ca-certificates
          ;;
        *" rhel "*|*" fedora "*)
          log "Installiere Pakete mit dnf/yum..."
          if has_cmd dnf; then
            dnf install -y python3 git openssh-clients sshpass ca-certificates
          else
            yum install -y python3 git openssh-clients sshpass ca-certificates
          fi
          ;;
        *" suse "*)
          log "Installiere Pakete mit zypper..."
          zypper --non-interactive refresh
          zypper --non-interactive install python3 git openssh sshpass ca-certificates
          ;;
        *)
          die "Nicht unterstuetzte Distribution: ${OS_ID:-unbekannt}. Nutze SKIP_PACKAGES=1, wenn alle Pakete bereits installiert sind."
          ;;
      esac
      ;;
  esac
}

find_python() {
  if has_cmd python3; then
    PYTHON_BIN="$(command -v python3)"
  elif has_cmd python; then
    PYTHON_BIN="$(command -v python)"
  else
    die "python3 wurde nicht gefunden."
  fi
}

create_user() {
  if [ "$OS_ID" = "freebsd" ]; then
    pw groupadd "$APP_GROUP" 2>/dev/null || true
  elif has_cmd groupadd; then
    groupadd --system "$APP_GROUP" 2>/dev/null || true
  fi

  if id "$APP_USER" >/dev/null 2>&1; then
    log "Benutzer $APP_USER existiert bereits."
    return
  fi

  log "Erstelle Systembenutzer $APP_USER..."
  if [ "$OS_ID" = "freebsd" ]; then
    pw useradd "$APP_USER" -g "$APP_GROUP" -d "$PREFIX" -s /usr/sbin/nologin -c "GateCore Panel"
  else
    if has_cmd useradd; then
      useradd --system --gid "$APP_GROUP" --home-dir "$PREFIX" --shell /usr/sbin/nologin --comment "GateCore Panel" "$APP_USER"
    else
      adduser --system --home "$PREFIX" --no-create-home --group "$APP_USER"
    fi
  fi
}

source_dir() {
  SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
  if [ -f "$SCRIPT_DIR/auth_server.py" ] && [ -d "$SCRIPT_DIR/panel" ]; then
    SRC_DIR="$SCRIPT_DIR"
    return
  fi

  has_cmd git || die "git wird benoetigt, wenn install.sh nicht aus dem Repository gestartet wird."
  TMP_DIR="$(mktemp -d)"
  log "Klonen von $REPO_URL..."
  git clone "$REPO_URL" "$TMP_DIR/source"
  SRC_DIR="$TMP_DIR/source"
}

copy_tree() {
  log "Installiere Dateien nach $PREFIX..."
  mkdir -p "$PREFIX"

  install -m 0755 "$SRC_DIR/auth_server.py" "$PREFIX/auth_server.py"
  install -m 0755 "$SRC_DIR/control_backend.py" "$PREFIX/control_backend.py"

  rm -rf "$PREFIX/panel"
  mkdir -p "$PREFIX/panel"
  cp -R "$SRC_DIR/panel/." "$PREFIX/panel/"

  mkdir -p "$PREFIX/config"
  for file in auth-config.json hosts.json servers.json settings-config.js settings-config.json users.json; do
    if [ "$FORCE_CONFIG" = "1" ] || [ ! -e "$PREFIX/config/$file" ]; then
      install -m 0640 "$SRC_DIR/config/$file" "$PREFIX/config/$file"
    else
      log "Behalte vorhandene Konfiguration: config/$file"
    fi
  done

  [ -f "$SRC_DIR/LICENSE" ] && install -m 0644 "$SRC_DIR/LICENSE" "$PREFIX/LICENSE"
  [ -f "$SRC_DIR/README.md" ] && install -m 0644 "$SRC_DIR/README.md" "$PREFIX/README.md"

  chown -R "$APP_USER:$APP_GROUP" "$PREFIX"
  find "$PREFIX" -type d -exec chmod 0750 {} \;
  find "$PREFIX" -type f -exec chmod 0640 {} \;
  chmod 0750 "$PREFIX/auth_server.py" "$PREFIX/control_backend.py"
}

install_systemd_services() {
  log "Erstelle systemd Services..."
  cat > /etc/systemd/system/gatecore-control.service <<EOF
[Unit]
Description=GateCore Panel Control Backend
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$PREFIX
ExecStart=$PYTHON_BIN $PREFIX/control_backend.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

  cat > /etc/systemd/system/gatecore-auth.service <<EOF
[Unit]
Description=GateCore Panel Web and Auth Server
After=network.target gatecore-control.service
Wants=gatecore-control.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$PREFIX
ExecStart=$PYTHON_BIN $PREFIX/auth_server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable gatecore-control.service gatecore-auth.service
  systemctl restart gatecore-control.service gatecore-auth.service
}

install_freebsd_services() {
  log "Erstelle FreeBSD rc.d Services..."
  cat > /usr/local/etc/rc.d/gatecore_control <<EOF
#!/bin/sh

# PROVIDE: gatecore_control
# REQUIRE: NETWORKING
# KEYWORD: shutdown

. /etc/rc.subr

name="gatecore_control"
rcvar="gatecore_control_enable"
command="/usr/sbin/daemon"
command_args="-f -p /var/run/gatecore_control.pid -u $APP_USER -c $PREFIX $PYTHON_BIN $PREFIX/control_backend.py"
pidfile="/var/run/gatecore_control.pid"

load_rc_config "\$name"
: \${gatecore_control_enable:="NO"}

run_rc_command "\$1"
EOF

  cat > /usr/local/etc/rc.d/gatecore_auth <<EOF
#!/bin/sh

# PROVIDE: gatecore_auth
# REQUIRE: NETWORKING gatecore_control
# KEYWORD: shutdown

. /etc/rc.subr

name="gatecore_auth"
rcvar="gatecore_auth_enable"
command="/usr/sbin/daemon"
command_args="-f -p /var/run/gatecore_auth.pid -u $APP_USER -c $PREFIX $PYTHON_BIN $PREFIX/auth_server.py"
pidfile="/var/run/gatecore_auth.pid"

load_rc_config "\$name"
: \${gatecore_auth_enable:="NO"}

run_rc_command "\$1"
EOF

  chmod 0755 /usr/local/etc/rc.d/gatecore_control /usr/local/etc/rc.d/gatecore_auth
  sysrc gatecore_control_enable=YES
  sysrc gatecore_auth_enable=YES
  service gatecore_control restart || service gatecore_control start
  service gatecore_auth restart || service gatecore_auth start
}

print_summary() {
  HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
  [ -n "$HOST_IP" ] || HOST_IP="$(hostname 2>/dev/null || printf 'SERVER-IP')"

  cat <<EOF

GateCore Panel wurde installiert.

Pfad:        $PREFIX
Web/API:     http://$HOST_IP:$AUTH_PORT
Control API: http://127.0.0.1:$CONTROL_PORT
Login:       admin / admin123

Wichtige Dateien:
  $PREFIX/config/auth-config.json
  $PREFIX/config/users.json
  $PREFIX/config/hosts.json
  $PREFIX/config/servers.json

Bitte aendere die Standardpasswoerter direkt nach der Installation.
EOF
}

main() {
  need_root
  detect_os
  install_packages
  find_python
  create_user
  source_dir
  copy_tree

  if [ "$OS_ID" = "freebsd" ]; then
    install_freebsd_services
  else
    has_cmd systemctl || die "systemctl wurde nicht gefunden. Fuer diese Linux-Installation wird systemd erwartet."
    install_systemd_services
  fi

  print_summary
}

main "$@"
