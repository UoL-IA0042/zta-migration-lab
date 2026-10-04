# Phase 0 journal

## 2026-09-06 09:00–10:00 | phase-0 | node-reset | debugging
Investigated why the planned BMC-based re-flash path was not viable.
The BMC's own filesystem is ~128 MB NAND (37 MB rom + 24 MB overlay),
far too small to stage OS images; initial node imaging had been done
manually through the BMC web UI. Established that the 32 GB eMMC and
4 TB NVMe live on each RK1 module and are visible only from the node
OS, not from the BMC. Node inspection (lsblk) recorded the actual
layout: mmcblk0p1 = vfat CIDATA (cloud-init NoCloud seed), mmcblk0p2 =
ext4 cloudimg-rootfs 29G mounted as / (main OS runs from eMMC, not
NVMe as the draft design assumed), nvme0n1p1 = single whole-disk ext4
data partition mounted /data (28K used). extlinux.conf found at
/boot/extlinux/extlinux.conf on the root filesystem itself, not on a
separate boot partition.

## 2026-09-06 10:00–11:30 | phase-0 | node-reset | testing
Attempted to determine the U-Boot boot scan order via `tpi uart`.
First captures returned only kernel boot logs; the UART ring buffer
evicts U-Boot's output almost immediately. Working procedure: power
cycle the node, then interrupt autoboot by sending input during the
window (`tpi uart -n 1 set --cmd ""` repeatedly), then issue
`printenv` commands and read with `tpi uart -n 1 get`.

Findings (node 1, expected identical across nodes):

- U-Boot 2024.01 (built Jun 13 2024), SPL loaded from eMMC,
  TF-A/BL31 v2.3 (fwver v1.45), no OPTEE.
- bootcmd = "bootflow scan"
- boot_targets = "mmc1 nvme scsi usb mmc0 pxe dhcp spi"
- Environment is ENV_IS_NOWHERE ("Loading Environment from nowhere"):
  compiled-in defaults; setenv/saveenv cannot persist changes.

Critical implication: only one MMC controller exists (device 0 = the
eMMC), so mmc1 is absent and **NVMe is scanned before the eMMC**. Any
bootable NVMe partition would win every boot, not act as a fallback.
Combined with the non-persistent environment, the boot order cannot be
changed without rebuilding U-Boot.

Incidental observations, recorded for later reference: nodes report
hostnames tpi2-N; one PCIe controller (fe180000) logs "PCIe Link Fail /
failed to initialize host" while the NVMe controller works — check
whether thisappears on all four nodes (likely an unpopulated lane)
before Phase 2.

## 2026-09-06 11:30–13:00 | phase-0 | node-reset | coding
Redesigned the node-reset component around the verified boot behavior.
Discarded the draft design (recovery on eMMC / main on NVMe, explicit
extlinux flip on a shared boot partition) — invalidated twice, first
by the actual storage layout, then by the NVMe-before-eMMC scan order.

Final design: main OS stays on eMMC (mmcblk0p2, the restore target);
NVMe repartitions to p1 = 16G recovery OS + p2 = /data holding a
zstd-compressed, sha256-checksummed golden image of the eMMC root.
The boot switch is the presence of extlinux.conf on the recovery
partition: normally renamed to .disabled so the scan falls through to
the eMMC; reset enables it, boots recovery, dd-restores the golden
image, disables it again, and boots back. Main's /boot/extlinux is
never modified. Accepted trade-off: no automatic failover for a
corrupted eMMC root (recovery is deliberately unbootable in normal
operation); escalation is a streamed `tpi flash` eMMC re-flash.
Reconciled dependent components: ansible-k3s no longer formats the
whole NVMe (Longhorn moves to /data/longhorn); storage layout table
added to docs/addressing.md as the single source of truth.

## 2026-09-06 13:00–13:30 | phase-0 | node-reset | documentation
Recorded the verified platform facts (U-Boot build, TF-A version,
bootcmd, boot_targets, ENV_IS_NOWHERE) in the node-reset README and
this journal. Dissertation relevance (RQ1): the reproducibility
procedure had to be redesigned twice due to undocumented platform
constraints — BMC storage capacity, actual eMMC/NVMe roles, boot scan
precedence, and a non-persistent bootloader environment. None of these
appear in the migration literature; they are exactly the class of
small-scale deployment pitfalls this research sets out to surface.
Remaining verification queue: NVMe repartition + recovery install,
end-to-end boot-switch test, one tpi flash streaming test at BMC
2.0.5, capture/restore timing, hostname alignment.
