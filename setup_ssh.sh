#!/bin/bash
set -e

# 1. Setup authorized_keys
mkdir -p /root/.ssh
chmod 700 /root/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFXa3Gg/8rT2GW8uOdx/SUkdCfWcmAZKC7bEeSZYzN7 hostinger-openclaw" > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# 2. Setup SSH daemon config
mkdir -p /etc/ssh/sshd_config.d
cat << 'EOF' > /etc/ssh/sshd_config.d/00-root.conf
PermitRootLogin yes
PasswordAuthentication yes
KbdInteractiveAuthentication yes
EOF

sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true

# 3. Restart SSH
systemctl restart ssh ssh.socket sshd 2>/dev/null || true

echo "=== SSH SETUP SUCCESSFUL ==="
