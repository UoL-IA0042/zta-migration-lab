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

## 2026-10-04 11:00-11:30 | phase-0 | github-repo | coding, documentation
Added the documentation, journal, and code to the github repo so
as to start running experiments and establish a baseline from which
to make changes and document the process, procedure, and outcomes
of establishing the supporting base infrastructure to begin phase 1.

## 2026-10-04 12:00-12:15 | phase-0 | ansible-observability | coding
Add Alloy deployment to all nodes and containers for log export to Loki.

## 2026-10-04 13:00-12:30 | phase-0 | ansible-observability | deployment
Attempted to deploy observability stack to nodes. Installation of
`node_exporter` was successful on all nodes. Installation of
prometheus on node 1 failed.

```
$ ansible-playbook -i inventory.yaml site.yaml
[WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
[DEPRECATION WARNING]: ansible.builtin.apt_repository has been deprecated. Use deb822_repository instead. This feature will be removed from ansible-core version 2.25.
Origin: /Users/<user>/dev/CYM500/zta-migration-lab/ansible-observability/site.yaml:118:7

116
117     - name: Add Grafana apt repository
118       ansible.builtin.apt_repository:
          ^ column 7


PLAY [Install node_exporter on all nodes] ******************************************************************************************************************************************************

TASK [Gathering Facts] *************************************************************************************************************************************************************************
ok: [tpi2-3]
ok: [tpi2-4]
ok: [tpi2-2]
ok: [tpi2-1]

TASK [Install prometheus-node-exporter] ********************************************************************************************************************************************************
changed: [tpi2-4]
changed: [tpi2-2]
changed: [tpi2-3]
changed: [tpi2-1]

TASK [Enable and start node_exporter] **********************************************************************************************************************************************************
ok: [tpi2-1]
ok: [tpi2-4]
ok: [tpi2-2]
ok: [tpi2-3]

PLAY [Deploy observability stack on tpi2-1] ****************************************************************************************************************************************************

TASK [Gathering Facts] *************************************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Install Docker Engine and compose plugin] ************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Enable and start Docker] *****************************************************************************************************************************************************************
ok: [tpi2-1]

TASK [Create install directory] ****************************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Template Prometheus config] **************************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Provision Grafana datasources (Prometheus + Loki)] ***************************************************************************************************************************************
changed: [tpi2-1]

TASK [Template compose file] *******************************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Start stack] *****************************************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Reload Prometheus on config change] ******************************************************************************************************************************************************
changed: [tpi2-1]

TASK [Wait for Prometheus readiness] ***********************************************************************************************************************************************************
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (11 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (10 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (9 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (8 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (7 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (6 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (5 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (4 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (3 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (2 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (1 retries left).
FAILED - RETRYING: [tpi2-1]: Wait for Prometheus readiness (0 retries left).
[ERROR]: Task failed: Module failed: Status code was -1 and not [200]: Request failed: <urlopen error [Errno 111] Connection refused>
Origin: /Users/<user>/dev/CYM500/zta-migration-lab/ansible-observability/site.yaml:83:7

81       when: prom_cfg.changed
82
83     - name: Wait for Prometheus readiness
         ^ column 7

fatal: [tpi2-1]: FAILED! => {"attempts": 12, "changed": false, "elapsed": 0, "msg": "Status code was -1 and not [200]: Request failed: <urlopen error [Errno 111] Connection refused>", "redirected": false, "status": -1, "url": "http://10.0.0.71:9090/-/ready"}

PLAY RECAP *************************************************************************************************************************************************************************************
tpi2-1                     : ok=12   changed=8    unreachable=0    failed=1    skipped=0    rescued=0    ignored=0
tpi2-2                     : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
tpi2-3                     : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
tpi2-4                     : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

Looking at the `docker` logs, there is this output.
```
ubuntu@tpi2-1:~$ sudo docker logs b432de766d91
time=2026-10-04T20:13:55.748Z level=INFO source=main.go:1544 msg="updated GOGC" old=100 new=75
time=2026-10-04T20:13:55.748Z level=INFO source=main.go:676 msg="Leaving GOMAXPROCS=8: CPU quota undefined" component=automaxprocs
time=2026-10-04T20:13:55.749Z level=INFO source=memlimit.go:198 msg="GOMEMLIMIT is updated" component=automemlimit package=github.com/KimMachineGun/automemlimit/memlimit GOMEMLIMIT=29984713113 previous=9223372036854775807
time=2026-10-04T20:13:55.749Z level=INFO source=main.go:769 msg="Starting Prometheus Server" mode=server version="(version=3.5.0, branch=HEAD, revision=8be3a9560fbdd18a94dedec4b747c35178177202)"
time=2026-10-04T20:13:55.749Z level=INFO source=main.go:774 msg="operational information" build_context="(go=go1.24.5, platform=linux/arm64, user=root@4451b64cb451, date=20250714-16:18:17, tags=netgo,builtinassets)" host_details="(Linux 6.1.0-1025-rockchip #25-Ubuntu SMP Mon Aug 26 23:01:14 UTC 2024 aarch64 b432de766d91 (none))" fd_limits="(soft=524287, hard=524288)" vm_limits="(soft=unlimited, hard=unlimited)"
time=2026-10-04T20:13:55.750Z level=ERROR source=query_logger.go:137 msg="Failed to create directory for logging active queries" component=activeQueryTracker
time=2026-10-04T20:13:55.750Z level=ERROR source=query_logger.go:113 msg="Error opening query log file" component=activeQueryTracker file=/prometheus/data/queries.active err="open data/queries.active: no such file or directory"
panic: Unable to create mmap-ed active query log

goroutine 1 [running]:
github.com/prometheus/prometheus/promql.NewActiveQueryTracker({0x3aa3f19, 0x5}, 0x14, 0x40006d2bb0)
	/app/promql/query_logger.go:145 +0x260
main.main()
	/app/cmd/prometheus/main.go:854 +0x7354
time=2026-10-04T20:13:56.615Z level=INFO source=main.go:1544 msg="updated GOGC" old=100 new=75
time=2026-10-04T20:13:56.615Z level=INFO source=main.go:676 msg="Leaving GOMAXPROCS=8: CPU quota undefined" component=automaxprocs
time=2026-10-04T20:13:56.615Z level=INFO source=memlimit.go:198 msg="GOMEMLIMIT is updated" component=automemlimit package=github.com/KimMachineGun/automemlimit/memlimit GOMEMLIMIT=29984713113 previous=9223372036854775807
time=2026-10-04T20:13:56.615Z level=INFO source=main.go:769 msg="Starting Prometheus Server" mode=server version="(version=3.5.0, branch=HEAD, revision=8be3a9560fbdd18a94dedec4b747c35178177202)"
time=2026-10-04T20:13:56.615Z level=INFO source=main.go:774 msg="operational information" build_context="(go=go1.24.5, platform=linux/arm64, user=root@4451b64cb451, date=20250714-16:18:17, tags=netgo,builtinassets)" host_details="(Linux 6.1.0-1025-rockchip #25-Ubuntu SMP Mon Aug 26 23:01:14 UTC 2024 aarch64 b432de766d91 (none))" fd_limits="(soft=524287, hard=524288)" vm_limits="(soft=unlimited, hard=unlimited)"
time=2026-10-04T20:13:56.616Z level=ERROR source=query_logger.go:137 msg="Failed to create directory for logging active queries" component=activeQueryTracker
time=2026-10-04T20:13:56.616Z level=ERROR source=query_logger.go:113 msg="Error opening query log file" component=activeQueryTracker file=/prometheus/data/queries.active err="open data/queries.active: no such file or directory"
panic: Unable to create mmap-ed active query log

goroutine 1 [running]:
github.com/prometheus/prometheus/promql.NewActiveQueryTracker({0x3aa3f19, 0x5}, 0x14, 0x400067d940)
	/app/promql/query_logger.go:145 +0x260
main.main()
	/app/cmd/prometheus/main.go:854 +0x7354
time=2026-10-04T20:13:57.694Z level=INFO source=main.go:1544 msg="updated GOGC" old=100 new=75
time=2026-10-04T20:13:57.694Z level=INFO source=main.go:676 msg="Leaving GOMAXPROCS=8: CPU quota undefined" component=automaxprocs
time=2026-10-04T20:13:57.694Z level=INFO source=memlimit.go:198 msg="GOMEMLIMIT is updated" component=automemlimit package=github.com/KimMachineGun/automemlimit/memlimit GOMEMLIMIT=29984713113 previous=9223372036854775807
time=2026-10-04T20:13:57.694Z level=INFO source=main.go:769 msg="Starting Prometheus Server" mode=server version="(version=3.5.0, branch=HEAD, revision=8be3a9560fbdd18a94dedec4b747c35178177202)"
time=2026-10-04T20:13:57.694Z level=INFO source=main.go:774 msg="operational information" build_context="(go=go1.24.5, platform=linux/arm64, user=root@4451b64cb451, date=20250714-16:18:17, tags=netgo,builtinassets)" host_details="(Linux 6.1.0-1025-rockchip #25-Ubuntu SMP Mon Aug 26 23:01:14 UTC 2024 aarch64 b432de766d91 (none))" fd_limits="(soft=524287, hard=524288)" vm_limits="(soft=unlimited, hard=unlimited)"
time=2026-10-04T20:13:57.695Z level=ERROR source=query_logger.go:137 msg="Failed to create directory for logging active queries" component=activeQueryTracker
time=2026-10-04T20:13:57.695Z level=ERROR source=query_logger.go:113 msg="Error opening query log file" component=activeQueryTracker file=/prometheus/data/queries.active err="open data/queries.active: no such file or directory"
panic: Unable to create mmap-ed active query log

goroutine 1 [running]:
github.com/prometheus/prometheus/promql.NewActiveQueryTracker({0x3aa3f19, 0x5}, 0x14, 0x4000155110)
	/app/promql/query_logger.go:145 +0x260
main.main()
	/app/cmd/prometheus/main.go:854 +0x7354
```
 Need to debug the startup problem next.

## 2026-10-04 14:00-14:30 | phase-0 | ansible-observability | deployment
Found a bug in the ansible code where the directories were not being created, which
caused the `permission denied` errors. Fixed in a commit alongside this journal
entry. The observability stack is now deployed.

## 2026-10-04 14:00-14:30 | phase-0 | ansible-observability | deployment
Update the observability ansible code to use `ansible-vault` for the grafana admin
password.
