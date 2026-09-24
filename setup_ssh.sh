#!/bin/bash
set -e

# 1. Fix permissions on /root and /root/.ssh
chown -R root:root /root
chmod 700 /root
mkdir -p /root/.ssh
chown -R root:root /root/.ssh
chmod 700 /root/.ssh

# 2. Set authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFXa3Gg/8rT2GW8uOdx/SUkdCfWcmAZKC7bEeSZYzN7 hostinger-openclaw" > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# 3. Set a clean known root password directly via chpasswd
echo "root:Agente@2026" | chpasswd

# 4. Configure SSH daemon
mkdir -p /etc/ssh/sshd_config.d
cat << 'EOF' > /etc/ssh/sshd_config.d/00-root.conf
PermitRootLogin yes
PasswordAuthentication yes
KbdInteractiveAuthentication yes
PubkeyAuthentication yes
EOF

sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true

# 5. Restart SSH
systemctl restart ssh ssh.socket sshd 2>/dev/null || true

echo "=== SSH SETUP SUCCESSFUL - PASSWORD IS Agente@2026 ==="
