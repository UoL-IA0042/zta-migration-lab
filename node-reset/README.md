# Node Reset (clean-state procedure)

Restores a checksummed golden image of the eMMC root from the node's
own NVMe, fully over SSH. Full eMMC re-flash via `tpi flash` (streams
from the workstation; BMC firmware 2.0.5) is the escalation path.

## Verified platform facts (journaled)

- U-Boot 2024.01 (Jun 13 2024), SPL from eMMC, TF-A v2.3, no OPTEE
- `bootcmd="bootflow scan"`,
  `boot_targets="mmc1 nvme scsi usb mmc0 pxe dhcp spi"`
- **NVMe is scanned before the eMMC (mmc0)**; `mmc1` is absent on RK1
- Environment is `ENV_IS_NOWHERE` (compiled-in; setenv cannot persist)

## Layout

| Device | Role |
|---|---|
| `/dev/mmcblk0p1` | vfat `CIDATA` — cloud-init NoCloud seed |
| `/dev/mmcblk0p2` | ext4 `cloudimg-rootfs` — main OS root (29G) |
| `/dev/nvme0n1p1` | recovery OS root (16G) |
| `/dev/nvme0n1p2` | `/data`: golden image, Longhorn, workloads |

## Boot switch

Because NVMe outranks eMMC in the scan and the scan order cannot be
changed, the switch is the presence of `extlinux.conf` on the
**recovery** partition:

- Normal operation: recovery's config is `extlinux.conf.disabled` ->
  NVMe is not bootable -> scan falls through to the eMMC main OS.
- Reset: main mounts nvme0n1p1 and renames the config into place ->
  reboot boots recovery -> restore -> recovery renames its own config
  back to disabled -> reboot falls through to main.

Main's `/boot/extlinux` is never touched. Consequence: a corrupted
eMMC root has **no automatic failover** (recovery is deliberately
unbootable in normal operation); a wedged node is always recovered
out-of-band with `tpi flash`. If the reset fails mid-cycle, the node
keeps booting recovery — re-run from `--tags restore`.

## One-time setup per node

1. Repartition the NVMe (currently one whole-disk `/data`, 28K used):
   p1 = 16G recovery, p2 = rest as `/data`; update fstab by-UUID.
2. Install the recovery OS onto nvme0n1p1 (seeded image via
   `prepare-golden-image.sh`, or debootstrap). Verify it boots (it will
   win the scan while enabled) and has your SSH key, then rename its
   `/boot/extlinux/extlinux.conf` to `extlinux.conf.disabled` and
   reboot back to main.
3. Bring the main OS to baseline, write `/etc/golden-image-release`,
   run `reset.yaml --tags to-recovery`, then `./capture-golden.sh tpi2-N`.
   Today's install becomes the golden image.

## Usage

```bash
ansible-galaxy collection install -r requirements.yaml       # once
ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3     # full cycle
ansible-playbook -i inventory.yaml reset.yaml -l tpi2-3 --tags to-recovery
./capture-golden.sh tpi2-3                                  # refresh golden
```

## Escalation (wedged node)

```bash
tpi power off -n 3 && tpi power on -n 3          # power cycle
tpi flash --node 3 --image-path seeded.img       # full eMMC re-flash
```

`tpi flash` writes the node's **eMMC** only; the NVMe is imaged from
the running node. Re-seeding cloud-init = writing user-data files to
the `CIDATA` partition (what `prepare-golden-image.sh` does).
node
## Edge nodes (tpi2-4)

tpi2-4 takes its address from the ISP gateway, not dnsmasq, because
the gateway only port-forwards to devices it leased (see
`docs/addressing.md`, "Edge node"). Its network state must survive
both reset paths:

- **Recovery OS**: `reset.yaml` reboots into recovery and waits for it
  at the inventory address, so the recovery root needs the same netplan
  override. Without it, recovery boots with the generated MAC, takes a
  dnsmasq lease, and the reboot task times out. From the main OS:

  ```bash
  sudo mkdir -p /mnt/recovery && sudo mount /dev/nvme0n1p1 /mnt/recovery
  cat /mnt/recovery/etc/netplan/*.yaml   # must use the zz-all-en/zz-all-eth IDs
  sudo install -m 600 /etc/netplan/60-dhcp-identifier.yaml /mnt/recovery/etc/netplan/
  sudo umount /mnt/recovery
  ```

  If recovery's netplan uses different IDs (e.g. a static `eth0` from
  the seed), adapt the override to those IDs instead of copying it.
- **Golden restore** (`reset.yaml`): the netplan override lives in the
  main root, so it is restored only if the golden image was captured
  *after* the override was added. Recapture once and journal it; a
  restore from an older golden image brings back the generated MAC and
  breaks the port forward:

  ```bash
  ansible-playbook -i inventory.yaml reset.yaml -l tpi2-4 --tags to-recovery
  ./capture-golden.sh tpi2-4 10.0.0.251
  ansible-playbook -i inventory.yaml reset.yaml -l tpi2-4 --tags to-main,verify
  ```
- **Re-flash** (`tpi flash`): seed with DHCP and the pinned MAC:

  ```bash
  sudo MACADDRESS=00:52:83:67:c2:f5 PUBKEY_FILE=~/.ssh/<lab-key>.pub \
      ./prepare-golden-image.sh ubuntu-rockchip.img tpi2-4 dhcp
  ```

After either path, confirm before running ansible-openvpn:

```bash
cat /sys/class/net/end0/address        # 00:52:83:67:c2:f5
grep SERVER_ADDRESS /run/systemd/netif/leases/*   # 10.0.0.1 (ISP gateway)
ip -4 addr show end0                   # 10.0.0.251
```

The seeded SSH key is whatever `PUBKEY_FILE` points at (default
`~/.ssh/id_ed25519.pub`); use the same lab key for every node so one
`IdentitiesOnly` entry in the workstation's `~/.ssh/config` covers the
cluster (agents holding several keys otherwise hit sshd's
`MaxAuthTries` before reaching the right one).

## Remaining VERIFY items (journal results)

- `tpi flash` streaming at BMC 2.0.5 completes without exhausting BMC
  storage (test one node).
- End-to-end switch test after recovery install: enable recovery
  extlinux, reboot, confirm recovery boots; disable, reboot, confirm
  main boots. (This validates the exact mechanism reset.yaml uses.)
- Capture/restore timing for the reproducibility discussion. dd
  rewrites the whole 29G partition (~10-15 min at eMMC speeds); switch
  to partclone (used-blocks only) if too slow, and note the change.
- Golden restore leaves `/data` untouched: decide per experiment
  whether Longhorn/workload data must also be wiped for clean state.
- Hostname convention: nodes currently report `tpi2-N`.
