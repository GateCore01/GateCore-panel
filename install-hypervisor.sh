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
    # Debian/Ubuntu systems
    debian|ubuntu)
        echo "Detected Debian/Ubuntu system. Installing dependencies..."
        apt update
        apt upgrade -y
        apt install -y lxc lxc-templates lxcfs uidmap bridge-utils vlan dnsmasq-base debootstrap rsync curl wget sudo openssh-server iptables nftables iproute2 bridge-utils smartmontools nvme-cli lvm2 mdadm parted xfsprogs btrfs-progs jq
        ;;

    # Red Hat-based systems
    centos|rhel|rocky)
        echo "Detected Red Hat-based system. Installing dependencies..."
        dnf update -y
        dnf install -y lxc lxc-templates lxcfs shadow-utils bridge-utils dnsmasq iptables nftables iproute rsync curl wget openssh-server smartmontools nvme-cli lvm2 mdadm parted jq
        ;;

    # Fedora-based systems
    fedora)
        echo "Detected Fedora system. Installing dependencies..."
        dnf update -y
        dnf install -y lxc lxc-templates lxcfs bridge-utils dnsmasq iptables nftables iproute rsync curl wget openssh-server jq
        ;;

    # OpenSUSE-based systems
    opensuse*|suse)
        echo "Detected OpenSUSE-based system. Installing dependencies..."
        zypper refresh
        zypper update -y
        zypper install -y lxc lxcfs bridge-utils dnsmasq iptables nftables iproute2 rsync curl wget openssh-server jq
        ;;

    # Unknown or unsupported OS
    *)
        echo "Unsupported operating system: $OS. Exiting."
        exit 1
        ;;
esac

# Enable and start the LXC service
if systemctl list-unit-files | grep -q "lxc.service"; then
    systemctl enable lxc.service
    systemctl start lxc.service
    echo "LXC service enabled and started."
else
    echo "LXC service not found. Please ensure LXC is installed correctly."
fi

# Enable and start the SSH service
if systemctl list-unit-files | grep -q "ssh.service"; then
    systemctl enable ssh.service
    systemctl start ssh.service
    echo "SSH service enabled and started."
else
    echo "SSH service not found. Please ensure OpenSSH is installed correctly."
fi

# Enable Root login for SSH
if grep -q "^PermitRootLogin" /etc/ssh/sshd_config; then
    sed -i 's/^PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
else
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
fi

# Restart SSH service to apply changes
systemctl restart ssh.service
echo "SSH service restarted."

# Final message
echo "Hypervisor installation and configuration completed successfully."
echo "Please set a secure password for the root user if you haven't done so already."
echo "Happy virtualization!"