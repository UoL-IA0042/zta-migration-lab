#!/usr/bin/env bash
# Capture the golden rootfs image of a node's NVMe root partition.
# Run AFTER booting the node into the recovery OS (reset.yml --tags
# to-recovery), so the partition is not mounted during capture.
#
# Usage: ./capture-golden.sh tpi2-3 [10.0.0.73]
set -euo pipefail

NODE="${1:?node name}"
HOST="${2:-$NODE}"
ROOT_PART="${ROOT_PART:-/dev/mmcblk0p2}"   # eMMC main OS root
DATA_MOUNT="${DATA_MOUNT:-/data}"
SSH="ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null ubuntu@${HOST}"

# Refuse to capture if the partition is mounted (running main OS).
if $SSH "findmnt -S ${ROOT_PART} >/dev/null 2>&1"; then
  echo "ERROR: ${ROOT_PART} is mounted on ${HOST} - boot recovery OS first" >&2
  exit 1
fi

echo "capturing ${ROOT_PART} on ${HOST} -> ${DATA_MOUNT}/golden/rootfs.img.zst"
$SSH "sudo mkdir -p ${DATA_MOUNT}/golden && \
      sudo sh -c 'dd if=${ROOT_PART} bs=4M status=progress | \
        zstd -3 -T0 -o ${DATA_MOUNT}/golden/rootfs.img.zst.new' && \
      sudo sh -c 'sha256sum ${DATA_MOUNT}/golden/rootfs.img.zst.new > ${DATA_MOUNT}/golden/rootfs.sha256.new' && \
      sudo mv ${DATA_MOUNT}/golden/rootfs.img.zst.new ${DATA_MOUNT}/golden/rootfs.img.zst && \
      sudo mv ${DATA_MOUNT}/golden/rootfs.sha256.new ${DATA_MOUNT}/golden/rootfs.sha256"

$SSH "ls -lh ${DATA_MOUNT}/golden/"
echo "captured. Record image identity in the journal:"
$SSH "cat ${DATA_MOUNT}/golden/rootfs.sha256"
