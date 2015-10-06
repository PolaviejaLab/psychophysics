
# Remove Amazon search
apt-get remove unity-webapps-common

# Disable automatic updates
cat <<EOF > /etc/apt/apt.conf.d/10periodic
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
EOF

# Setup boot script
cp ../../config/plab-client/setup-after-imaging.sh /usr/local/bin

cat <<EOF > /etc/rc.local
/usr/local/bin/setup-after-imaging.sh
EOF

chmod +x /etc/rc.local

