#!/usr/bin/env bash
# Capture the golden rootfs image of a node's NVMe root partition.
# Run AFTER booting the node into the recovery OS (reset.yml --tags
# to-recovery), so the partition is not mounted during capture.
#
# Usage: ./capture-golden.sh tpi2-3 [10.0.0.73]
#        ./capture-golden.sh tpi2-4 10.0.0.251   # pass the address if the
#                                                # name may resolve stale
set -euo pipefail

NODE="${1:?node name}"
HOST="${2:-$NODE}"
ROOT_PART="${ROOT_PART:-/dev/mmcblk0p2}"   # eMMC main OS root
DATA_MOUNT="${DATA_MOUNT:-/data}"
SSH="ssh -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null ubuntu@${HOST}"

# An unreachable node must stop here: otherwise the mount check below
# fails and reads as "not mounted".
if ! $SSH -o ConnectTimeout=10 -o BatchMode=yes true; then
  echo "ERROR: cannot reach ${HOST} over SSH" >&2
  exit 1
fi

# Refuse to capture if the partition is mounted (running main OS).
if $SSH "findmnt -S ${ROOT_PART} >/dev/null 2>&1"; then
  echo "ERROR: ${ROOT_PART} is mounted on ${HOST} - boot recovery OS first" >&2
  exit 1
fi

echo "capturing ${ROOT_PART} on ${HOST} -> ${DATA_MOUNT}/golden/rootfs.img.zst"
# Write to .new files and rename at the end, so an interrupted capture
# never replaces a good golden image. The checksum is recorded against
# the FINAL relative name (reset.yaml runs `sha256sum -c` from inside
# the golden directory), not the temporary .new path.
$SSH "sudo mkdir -p ${DATA_MOUNT}/golden && \
      sudo sh -c 'dd if=${ROOT_PART} bs=4M status=progress | \
        zstd -3 -T0 -f -o ${DATA_MOUNT}/golden/rootfs.img.zst.new' && \
      sudo sh -c 'cd ${DATA_MOUNT}/golden && sha256sum rootfs.img.zst.new | sed \"s/[.]new\$//\" > rootfs.sha256.new' && \
      sudo mv ${DATA_MOUNT}/golden/rootfs.img.zst.new ${DATA_MOUNT}/golden/rootfs.img.zst && \
      sudo mv ${DATA_MOUNT}/golden/rootfs.sha256.new ${DATA_MOUNT}/golden/rootfs.sha256 && \
      cd ${DATA_MOUNT}/golden && sha256sum -c rootfs.sha256"

$SSH "ls -lh ${DATA_MOUNT}/golden/"
echo "captured. Record image identity in the journal:"
$SSH "cat ${DATA_MOUNT}/golden/rootfs.sha256"
