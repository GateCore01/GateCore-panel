########################################
# Install script for the Web Panel     #
# This script will install the Web Panel and its dependencies on your system.
# It is recommended to run this script as root or with sudo privileges.
########################################
# Creator: Korbinian Musch
# License: MIT License
# Date Created: 06.06.2026
########################################
#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root or with sudo privileges."
  exit 1
fi

# Configure LDAP settings
echo "Configuring LDAP settings..."
read -p "Enter the LDAP server address (e.g., ldap://localhost:389): " ldap_server
read -p "Enter the LDAP base DN (e.g., dc=example,dc=com): " ldap_base_dn
read -p "Enter the LDAP admin DN (e.g., cn=admin,dc=example,dc=com): " ldap_admin_dn
read -s -p "Enter the LDAP admin password: " ldap_admin_password
echo

# Save the LDAP settings to a configuration file
cat <<EOL > panel/login-ldap.py
LDAP_SERVER = "$ldap_server"
LDAP_BASE_DN = "$ldap_base_dn"
LDAP_USERNAME = "$ldap_admin_dn"
LDAP_PASSWORD = "$ldap_admin_password"
EOL

# Update the package list and install dependencies
echo "Updating package list and installing dependencies..."
apt update
apt install -y python3 python3-pip python3-venv apache2 libapache2-mod-wsgi-py3 ldap-utils git 

# Download the Web Panel source code
echo "Downloading the Web Panel source code..."
git clone https://github.com/Korbinian0/GameServer-Gateway.git
cd GameServer-Gateway

# Copy the Web Panel files to the Apache web directory
echo "Copying Web Panel files to the Apache web directory..."
cp -r panel/*.html /var/www/html/
cp -r panel/*.css /var/www/html/
cp -r panel/*.js /var/www/html/

# Copy the python files to the appropriate location and create the directory if it doesn't exist
mkdir -p /opt/webpanel/
cp -r panel/*.py /opt/webpanel/

# Set the correct permissions for the Web Panel files
echo "Setting permissions for the Web Panel files..."
chown -R www-data:www-data /var/www/html/
chown -R root:root /opt/webpanel/
chmod -R 755 /var/www/html/
chmod -R 755 /opt/webpanel/

# Create the Systemd service file for the Web Panel
echo "Creating Systemd service file for the Web Panel..."
cat <<EOL > /etc/systemd/system/webpanel-ldap.service
[Unit]
Description=Web Panel LDAP Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/webpanel/
ExecStart=/usr/bin/python3 /opt/webpanel/login-ldap.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload Systemd to apply the new service file
echo "Reloading Systemd..."
systemctl daemon-reload

# Enable and start the Web Panel service
echo "Enabling and starting the Web Panel LDAP service..."
systemctl enable webpanel-ldap.service
systemctl start webpanel-ldap.service

# Restart Apache to apply changes
echo "Restarting Apache..."
systemctl restart apache2

# Final message
echo "Web Panel installation and configuration complete. The Web Panel should now be accessible via your web browser. Please ensure that your LDAP server is running and properly configured to allow the Web Panel to authenticate users."
