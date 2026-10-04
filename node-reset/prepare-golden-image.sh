#!/usr/bin/env bash
# Inject cloud-init NoCloud seed (SSH key, per-node hostname/IP) into a
# stock Ubuntu ARM64 image so freshly imaged nodes are Ansible-manageable
# on first boot. Run on the workstation; requires losetup/mount (sudo).
#
# Usage: sudo ./prepare-golden-image.sh ubuntu-rockchip.img tpi2-3 10.0.0.73
#
# VERIFY: the boot/seed partition location differs between image builds;
# this script drops the seed on the first vfat/ext4 partition containing
# extlinux or boot artifacts. Confirm cloud-init consumed it on first
# boot: `cloud-init status --long`.
set -euo pipefail

IMG="${1:?image file}"
HOSTNAME="${2:?hostname (e.g. tpi2-3)}"
ADDRESS="${3:?static address (e.g. 10.0.0.73)}"
PUBKEY_FILE="${PUBKEY_FILE:-$HOME/.ssh/id_ed25519.pub}"
GATEWAY="${GATEWAY:-10.0.0..1}"

PUBKEY=$(cat "$PUBKEY_FILE")
LOOP=$(losetup --show -fP "$IMG")
trap 'umount -q /mnt/img-seed 2>/dev/null; losetup -d "$LOOP"' EXIT
mkdir -p /mnt/img-seed

# Find the seed-bearing partition (boot partition with extlinux/ or
# system-boot label).
SEED_PART=""
for PART in "${LOOP}"p*; do
  mount "$PART" /mnt/img-seed 2>/dev/null || continue
  if [ -d /mnt/img-seed/extlinux ] || [ -f /mnt/img-seed/user-data ] \
     || [ -d /mnt/img-seed/boot/extlinux ]; then
    SEED_PART="$PART"; break
  fi
  umount /mnt/img-seed
done
[ -n "$SEED_PART" ] || { echo "no boot/seed partition found - inspect image layout" >&2; exit 1; }
echo "seeding $SEED_PART"

cat > /mnt/img-seed/user-data <<EOF
#cloud-config
hostname: ${HOSTNAME}
users:
  - name: ubuntu
    groups: [sudo]
    shell: /bin/bash
    sudo: "ALL=(ALL) NOPASSWD:ALL"
    ssh_authorized_keys:
      - ${PUBKEY}
ssh_pwauth: false
package_update: false
write_files:
  - path: /etc/golden-image-release
    content: "${HOSTNAME} $(date -u +%Y-%m-%dT%H:%M:%SZ) $(sha256sum "$IMG" | cut -c1-16)\n"
EOF

cat > /mnt/img-seed/meta-data <<EOF
instance-id: ${HOSTNAME}-golden
local-hostname: ${HOSTNAME}
EOF

cat > /mnt/img-seed/network-config <<EOF
version: 2
ethernets:
  eth0:
    match: {name: "e*"}
    addresses: ["${ADDRESS}/24"]
    routes: [{to: default, via: "${GATEWAY}"}]
    nameservers: {addresses: ["${GATEWAY}"]}
EOF

umount /mnt/img-seed
echo "done: ${IMG} seeded for ${HOSTNAME} (${ADDRESS})"
echo "flash with: tpi flash --node <N> --image-path ${IMG}"
