###########################################################################
# This script is used to install the necessary dependencies and set up the environment for the project.
# It checks for the required software, installs missing packages, and configures the system accordingly.
# Usage: Run this script in a terminal with appropriate permissions (e.g., using sudo if necessary).
###########################################################################
# License: MIT License
# Created by: Korbinian Musch
# Date: 2026-07-19
# Communion: GateCore01
############################################################################
# Base dependencies: Python 3.8+, pip 
# Supported Systems: 
# - Debian-based Linux distributions (e.g., Ubuntu, Debian)
# - Red Hat-based Linux distributions (e.g., CentOS, Fedora, Rocky Linux)
# - OpenSUSE-based Linux distributions (e.g., openSUSE Leap, openSUSE Tumbleweed)
#############################################################################
#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or use sudo."
    exit 1
fi

# Check the operating system
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot determine the operating system. Exiting."
    exit 1
fi

# Install dependencies based on the detected OS
case "$OS" in
    # Debian systems
    debian)
        echo "Detected Debian-based system. Installing dependencies..."
        apt update
        apt upgrade -y
        apt install -y python3 python3-pip python3-venv python3-dev build-essential git sqlite3 curl wget nano vim htop btop unzip zip openssl apache2 libapache2-mod-wsgi-py3 openssh-client openssh-server sudo acl cron systemd ethtool bridge-utils vlan ifupdown2 dnsutils net-tools iproute2 smartmontools nvme-cli lvm2 mdadm parted util-linux xfsprogs btrfs-progs zfsutils-linux rsync jq
        ;;

    # Ubuntu systems
    ubuntu)
        echo "Detected Ubuntu system. Installing dependencies..."
        apt update
        apt upgrade -y
        apt install -y python3 python3-pip python3-venv python3-dev build-essential git sqlite3 curl wget apache2 openssh-client openssh-server bridge-utils vlan ifupdown2 dnsutils net-tools iproute2 smartmontools nvme-cli lvm2 mdadm parted util-linux xfsprogs btrfs-progs zfsutils-linux jq
        ;;

    # Red Hat-based systems
    centos|rhel|rocky)
        echo "Detected Red Hat-based system. Installing dependencies..."
        dnf update -y
        dnf install -y python3 python3-pip python3-devel gcc gcc-c++ git sqlite wget curl wget httpd openssh-clients openssh-server sudo bridge-utils vconfig iproute bind-utils smartmontools nvme-cli lvm2 mdadm parted xfsprogs btrfs-progs rsync jq
        ;;

    # Fedora-based systems
    fedora)
        echo "Detected Fedora system. Installing dependencies..."
        dnf update -y
        dnf install -y python3 python3-pip python3-devel gcc gcc-c++ git sqlite curl wget httpd bridge-utils iproute bind-utils smartmontools nvme-cli lvm2 mdadm parted xfsprogs btrfs-progs jq
        ;;

    # OpenSUSE-based systems
    opensuse*|suse)
        echo "Detected OpenSUSE-based system. Installing dependencies..."
        zypper refresh
        zypper update -y
        zypper install -y python3 python3-pip python3-devel gcc gcc-c++ git sqlite3 curl wget apache2 openssh bridge-utils iproute2 bind-utils smartmontools nvme-cli lvm2 mdadm parted xfsprogs btrfsprogs jq
        ;;

    # Unknown or unsupported OS
    *)
        echo "Unsupported operating system: $OS. Exiting."
        exit 1
        ;;
esac

# Create necessary directories
mkdir -p /opt/gatecore/panel
mkdir -p /tmp/gatecore

# Set up Python virtual environment
python3 -m venv /opt/gatecore/panel/venv
source /opt/gatecore/panel/venv/bin/activate

# Upgrade pip and install Python dependencies
case "$OS" in
    
    # Debian/Ubuntu systems
    debian|ubuntu)
        echo "Installing Python dependencies for Debian/Ubuntu..."
        pip install --upgrade pip
        pip install fastapi uvicorn jinja2 python-multipart paramiko bcrypt passlib python-dotenv aiofiles psutil requests pydantic sqlalchemy
        ;;
    
    # Red Hat-based systems
    centos|rhel|rocky|fedora)
        echo "Installing Python dependencies for Red Hat-based systems..."
        pip install --upgrade pip
        pip install fastapi uvicorn jinja2 paramiko python-multipart passlib bcrypt aiofiles python-dotenv psutil requests pydantic sqlalchemy
        ;;

    # OpenSUSE-based systems
    opensuse*|suse)
        echo "Installing Python dependencies for OpenSUSE-based systems..."
        pip install --upgrade pip
        pip install fastapi uvicorn jinja2 paramiko python-multipart passlib bcrypt aiofiles python-dotenv psutil requests pydantic sqlalchemy
        ;;
esac

# Create a dedicated user for the GateCore panel
useradd -r -s /bin/false gatecore

# Clone the GateCore panel repository
git clone https://github.com/GateCore01/GateCore-panel /tmp/gatecore/

# Move the cloned repository to the installation directory
mv /tmp/gatecore/Core* /opt/gatecore/panel/

# Set permissions for the installation directory
chown -R gatecore:gatecore /opt/gatecore/panel/

# Set up systemd service for the GateCore panel
cat <<EOL > /etc/systemd/system/gatecore-panel.service
[Unit]
Description=GateCore Panel
After=network.target

[Service]
Type=simple

User=gatecore
Group=gatecore

WorkingDirectory=/opt/gatecore/panel

Environment="PATH=/opt/gatecore/panel/venv/bin"

ExecStart=/opt/gatecore/panel/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd daemon and enable the service
systemctl daemon-reload
systemctl enable gatecore-panel.service

# Start the GateCore panel service
systemctl start gatecore-panel.service

# Print completion message
echo "Installation complete. The GateCore panel is now running and accessible on port 8000."
echo "You can manage the service using: sudo systemctl [start|stop|restart|status] gatecore-panel.service"
echo "Please ensure that your firewall allows traffic on port 8000 if you want to access the panel remotely."
echo "For security, consider setting up a reverse proxy with HTTPS (e.g., using Nginx or Apache) to access the panel securely."
echo "Installation finished successfully."
echo "Please do not enable port 8000 on the public network; it may only be internal to your own network, as all API points are located there for external access. Please use a VPN such as WireGuard on the Fritzbox or other routers."
echo "Have fun with the GateCore panel and enjoy managing your systems efficiently!"