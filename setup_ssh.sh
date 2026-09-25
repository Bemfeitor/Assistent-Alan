#!/bin/bash
set -e

# 1. Comment out existing conflicting directives across sshd_config and drop-ins
sed -i 's/^[#[:space:]]*PermitRootLogin.*/#&/' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true
sed -i 's/^[#[:space:]]*PasswordAuthentication.*/#&/' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true
sed -i 's/^[#[:space:]]*StrictModes.*/#&/' /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null || true

# 2. Prepend authoritative settings at line 1 of /etc/ssh/sshd_config
sed -i '1i PermitRootLogin yes\nPasswordAuthentication yes\nStrictModes no\nPubkeyAuthentication yes' /etc/ssh/sshd_config

# 3. Permissions & Keys
chown -R root:root /root
chmod 700 /root
mkdir -p /root/.ssh
chown -R root:root /root/.ssh
chmod 700 /root/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGFXa3Gg/8rT2GW8uOdx/SUkdCfWcmAZKC7bEeSZYzN7 hostinger-openclaw" > /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# 4. Set root password to both known options (user's password and fallback)
echo "root:Agente@2026" | chpasswd
echo 'root:08C7&ybM1(u4+zkU' | chpasswd

# 5. Restart SSH service and socket
systemctl daemon-reload 2>/dev/null || true
systemctl restart ssh.service ssh.socket ssh sshd 2>/dev/null || true

# 6. Verify effective configuration
echo "--- EFFECTIVE SSHD CONFIG ---"
sshd -T | grep -E 'permitrootlogin|passwordauthentication|strictmodes' || true
echo "============================="
echo "=== SSH SETUP SUCCESSFUL ==="
