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

## 2026-10-04 17:45-18:15 | phase-0 | ansible-keycloak | deployment
Set all necessary passwords and secrets for keycloak deployment and encrypt them with
`ansible-vault`.
Deployed `ansible-keycloak`.
```
$ ansible-playbook -i inventory.yaml --vault-pass-file ../.vault-pass site.yaml 

PLAY [Deploy Keycloak with declarative realm] **************************************************************************************************************************************************

TASK [Gathering Facts] *************************************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Install Docker Engine and compose plugin] ************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Enable and start Docker] *****************************************************************************************************************************************************************
ok: [tpi2-2]

TASK [Create install directories] **************************************************************************************************************************************************************
ok: [tpi2-2] => (item=/opt/keycloak)
ok: [tpi2-2] => (item=/opt/keycloak/import)

TASK [Template realm definition (roles, users, OIDC clients)] **********************************************************************************************************************************
ok: [tpi2-2]

TASK [Template compose file] *******************************************************************************************************************************************************************
changed: [tpi2-2]

TASK [Start (or restart on config change) Keycloak stack] **************************************************************************************************************************************
changed: [tpi2-2]

TASK [Wait for Keycloak health endpoint] *******************************************************************************************************************************************************
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (29 retries left).
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (28 retries left).
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (27 retries left).
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (26 retries left).
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (25 retries left).
FAILED - RETRYING: [tpi2-2]: Wait for Keycloak health endpoint (24 retries left).
ok: [tpi2-2]

TASK [Verify realm import (OIDC discovery document)] *******************************************************************************************************************************************
ok: [tpi2-2]

TASK [Report OIDC issuer for ZTNA integration] *************************************************************************************************************************************************
ok: [tpi2-2] => {
    "msg": "OIDC issuer: http://10.0.0.72:8080/realms/lab"
}

PLAY RECAP *************************************************************************************************************************************************************************************
tpi2-2                     : ok=10   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## 2026-10-04 18:15-18:45 | phase-0 | ansible-workloads | deployment
Set all necessary passwords and secrets for keycloak deployment and encrypt them with
`ansible-vault`.
Deployed `ansible-workloads`.
```
$ ansible-playbook -i inventory.yaml --vault-pass-file ../.vault-pass site.yaml

PLAY [Deploy protected workloads] ***********************************************************************************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Install Docker Engine and compose plugin] *********************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Enable and start Docker] **************************************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Create directories] *******************************************************************************************************************************************************************************
changed: [tpi2-3] => (item=/opt/workloads)
changed: [tpi2-3] => (item=/opt/workloads/www)
changed: [tpi2-3] => (item=/opt/workloads/share)

TASK [Intranet web content] *****************************************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Seed file share] **********************************************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Template database init (per-role users and grants)] ***********************************************************************************************************************************************
changed: [tpi2-3]

TASK [Template compose file] ****************************************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Start workloads] **********************************************************************************************************************************************************************************
changed: [tpi2-3]

TASK [Verify intranet web responds] *********************************************************************************************************************************************************************
ok: [tpi2-3]

TASK [Verify postgres accepts connections] **************************************************************************************************************************************************************
FAILED - RETRYING: [tpi2-3]: Verify postgres accepts connections (5 retries left).
ok: [tpi2-3]

PLAY RECAP **********************************************************************************************************************************************************************************************
tpi2-3                     : ok=11   changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```

## 2026-10-04 21:45-22:45 | phase-0 | terraform-aws | deployment
Deploy AWS resources to AWS account using terraform. Some modififications
to the code were needed to ensure the S3 bucket is globally unique, so
those are included with this update.

`terraform init` output
```
<user>$ tf init
Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 6.0"...
- Finding hashicorp/random versions matching "~> 3.6"...
- Installing hashicorp/random v3.9.1...
- Installed hashicorp/random v3.9.1 (signed by HashiCorp)
- Installing hashicorp/aws v6.67.0...
- Installed hashicorp/aws v6.67.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

`terraform plan -var ssh_key_name=UoL-IA0042` output
```
$ tf plan -var ssh_key_name=UoL-IA0042
data.aws_ami.ubuntu_arm64: Reading...
data.aws_ami.ubuntu_arm64: Read complete after 0s [id=ami-06c11807f6c511068]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
 <= read (data resources)

Terraform will perform the following actions:

  # data.aws_iam_policy_document.s3_read will be read during apply
  # (config refers to values not yet known)
 <= data "aws_iam_policy_document" "s3_read" {
      + id            = (known after apply)
      + json          = (known after apply)
      + minified_json = (known after apply)

      + statement {
          + actions   = [
              + "s3:GetObject",
              + "s3:ListBucket",
            ]
          + resources = [
              + (known after apply),
              + (known after apply),
            ]
        }
    }

  # data.aws_iam_policy_document.s3_write will be read during apply
  # (config refers to values not yet known)
 <= data "aws_iam_policy_document" "s3_write" {
      + id            = (known after apply)
      + json          = (known after apply)
      + minified_json = (known after apply)

      + statement {
          + actions   = [
              + "s3:PutObject",
            ]
          + resources = [
              + (known after apply),
            ]
        }
    }

  # aws_iam_policy.s3_read will be created
  + resource "aws_iam_policy" "s3_read" {
      + arn              = (known after apply)
      + attachment_count = (known after apply)
      + id               = (known after apply)
      + name             = "zta-lab-s3-read"
      + name_prefix      = (known after apply)
      + path             = "/"
      + policy           = (known after apply)
      + policy_id        = (known after apply)
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
    }

  # aws_iam_policy.s3_write will be created
  + resource "aws_iam_policy" "s3_write" {
      + arn              = (known after apply)
      + attachment_count = (known after apply)
      + id               = (known after apply)
      + name             = "zta-lab-s3-write"
      + name_prefix      = (known after apply)
      + path             = "/"
      + policy           = (known after apply)
      + policy_id        = (known after apply)
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
    }

  # aws_iam_user.role_users["remote-admin"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-admin"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-analyst"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-analyst"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-contractor"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-contractor"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-developer"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-developer"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user_policy_attachment.read["remote-admin"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-admin"
    }

  # aws_iam_user_policy_attachment.read["remote-analyst"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-analyst"
    }

  # aws_iam_user_policy_attachment.read["remote-developer"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-developer"
    }

  # aws_iam_user_policy_attachment.write["remote-admin"] will be created
  + resource "aws_iam_user_policy_attachment" "write" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-admin"
    }

  # aws_instance.app will be created
  + resource "aws_instance" "app" {
      + ami                                  = "ami-06c11807f6c511068"
      + arn                                  = (known after apply)
      + associate_public_ip_address          = (known after apply)
      + availability_zone                    = (known after apply)
      + disable_api_stop                     = (known after apply)
      + disable_api_termination              = (known after apply)
      + ebs_optimized                        = (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      + force_destroy                        = false
      + get_password_data                    = false
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      + id                                   = (known after apply)
      + instance_initiated_shutdown_behavior = (known after apply)
      + instance_lifecycle                   = (known after apply)
      + instance_state                       = (known after apply)
      + instance_type                        = "t4g.micro"
      + ipv6_address_count                   = (known after apply)
      + ipv6_addresses                       = (known after apply)
      + key_name                             = "UoL-IA0042"
      + monitoring                           = (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      + placement_partition_number           = (known after apply)
      + primary_network_interface_id         = (known after apply)
      + private_dns                          = (known after apply)
      + private_ip                           = "10.100.10.10"
      + public_dns                           = (known after apply)
      + public_ip                            = (known after apply)
      + region                               = "us-west-2"
      + secondary_private_ips                = (known after apply)
      + security_groups                      = (known after apply)
      + source_dest_check                    = true
      + spot_instance_request_id             = (known after apply)
      + subnet_id                            = (known after apply)
      + tags                                 = {
          + "Name" = "zta-lab-app"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-app"
          + "Project" = "zta-migration-lab"
        }
      + tenancy                              = (known after apply)
      + user_data                            = <<-EOT
            #!/bin/bash
            apt-get update && apt-get install -y nginx
            sed -i 's/listen 80/listen 8080/' /etc/nginx/sites-available/default
            echo '<h1>AWS lab application</h1>' > /var/www/html/index.html
            systemctl restart nginx
        EOT
      + user_data_base64                     = (known after apply)
      + user_data_replace_on_change          = false
      + vpc_security_group_ids               = (known after apply)

      + capacity_reservation_specification (known after apply)

      + cpu_options (known after apply)

      + ebs_block_device (known after apply)

      + enclave_options (known after apply)

      + ephemeral_block_device (known after apply)

      + instance_market_options (known after apply)

      + maintenance_options (known after apply)

      + metadata_options (known after apply)

      + network_interface (known after apply)

      + primary_network_interface (known after apply)

      + private_dns_name_options (known after apply)

      + root_block_device (known after apply)

      + secondary_network_interface (known after apply)
    }

  # aws_instance.vpn_gateway will be created
  + resource "aws_instance" "vpn_gateway" {
      + ami                                  = "ami-06c11807f6c511068"
      + arn                                  = (known after apply)
      + associate_public_ip_address          = (known after apply)
      + availability_zone                    = (known after apply)
      + disable_api_stop                     = (known after apply)
      + disable_api_termination              = (known after apply)
      + ebs_optimized                        = (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      + force_destroy                        = false
      + get_password_data                    = false
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      + id                                   = (known after apply)
      + instance_initiated_shutdown_behavior = (known after apply)
      + instance_lifecycle                   = (known after apply)
      + instance_state                       = (known after apply)
      + instance_type                        = "t4g.micro"
      + ipv6_address_count                   = (known after apply)
      + ipv6_addresses                       = (known after apply)
      + key_name                             = "UoL-IA0042"
      + monitoring                           = (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      + placement_partition_number           = (known after apply)
      + primary_network_interface_id         = (known after apply)
      + private_dns                          = (known after apply)
      + private_ip                           = (known after apply)
      + public_dns                           = (known after apply)
      + public_ip                            = (known after apply)
      + region                               = "us-west-2"
      + secondary_private_ips                = (known after apply)
      + security_groups                      = (known after apply)
      + source_dest_check                    = false
      + spot_instance_request_id             = (known after apply)
      + subnet_id                            = (known after apply)
      + tags                                 = {
          + "Name" = "zta-lab-vpn-gateway"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-vpn-gateway"
          + "Project" = "zta-migration-lab"
        }
      + tenancy                              = (known after apply)
      + user_data_base64                     = (known after apply)
      + user_data_replace_on_change          = false
      + vpc_security_group_ids               = (known after apply)

      + capacity_reservation_specification (known after apply)

      + cpu_options (known after apply)

      + ebs_block_device (known after apply)

      + enclave_options (known after apply)

      + ephemeral_block_device (known after apply)

      + instance_market_options (known after apply)

      + maintenance_options (known after apply)

      + metadata_options (known after apply)

      + network_interface (known after apply)

      + primary_network_interface (known after apply)

      + private_dns_name_options (known after apply)

      + root_block_device (known after apply)

      + secondary_network_interface (known after apply)
    }

  # aws_internet_gateway.igw will be created
  + resource "aws_internet_gateway" "igw" {
      + arn      = (known after apply)
      + id       = (known after apply)
      + owner_id = (known after apply)
      + region   = "us-west-2"
      + tags_all = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id   = (known after apply)
    }

  # aws_route_table.private will be created
  + resource "aws_route_table" "private" {
      + arn              = (known after apply)
      + id               = (known after apply)
      + owner_id         = (known after apply)
      + propagating_vgws = (known after apply)
      + region           = "us-west-2"
      + route            = [
          + {
              + cidr_block                 = "10.0.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
          + {
              + cidr_block                 = "10.9.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
        ]
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id           = (known after apply)
    }

  # aws_route_table.public will be created
  + resource "aws_route_table" "public" {
      + arn              = (known after apply)
      + id               = (known after apply)
      + owner_id         = (known after apply)
      + propagating_vgws = (known after apply)
      + region           = "us-west-2"
      + route            = [
          + {
              + cidr_block                 = "0.0.0.0/0"
              + gateway_id                 = (known after apply)
                # (12 unchanged attributes hidden)
            },
        ]
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id           = (known after apply)
    }

  # aws_route_table_association.private will be created
  + resource "aws_route_table_association" "private" {
      + id             = (known after apply)
      + region         = "us-west-2"
      + route_table_id = (known after apply)
      + subnet_id      = (known after apply)
    }

  # aws_route_table_association.public will be created
  + resource "aws_route_table_association" "public" {
      + id             = (known after apply)
      + region         = "us-west-2"
      + route_table_id = (known after apply)
      + subnet_id      = (known after apply)
    }

  # aws_s3_bucket.data will be created
  + resource "aws_s3_bucket" "data" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = (known after apply)
      + bucket_domain_name          = (known after apply)
      + bucket_namespace            = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_region               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = "us-west-2"
      + request_payer               = (known after apply)
      + tags_all                    = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_public_access_block.data will be created
  + resource "aws_s3_bucket_public_access_block" "data" {
      + block_public_acls       = true
      + block_public_policy     = true
      + bucket                  = (known after apply)
      + id                      = (known after apply)
      + ignore_public_acls      = true
      + region                  = "us-west-2"
      + restrict_public_buckets = true
    }

  # aws_s3_object.probe_seed will be created
  + resource "aws_s3_object" "probe_seed" {
      + acl                    = (known after apply)
      + arn                    = (known after apply)
      + bucket                 = (known after apply)
      + bucket_key_enabled     = (known after apply)
      + checksum_crc32         = (known after apply)
      + checksum_crc32c        = (known after apply)
      + checksum_crc64nvme     = (known after apply)
      + checksum_sha1          = (known after apply)
      + checksum_sha256        = (known after apply)
      + content                = <<-EOT
            seed object for access-matrix read probes
        EOT
      + content_type           = (known after apply)
      + etag                   = (known after apply)
      + force_destroy          = false
      + id                     = (known after apply)
      + key                    = "probe.txt"
      + kms_key_id             = (known after apply)
      + region                 = "us-west-2"
      + server_side_encryption = (known after apply)
      + storage_class          = (known after apply)
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + version_id             = (known after apply)
    }

  # aws_security_group.vpn_gateway will be created
  + resource "aws_security_group" "vpn_gateway" {
      + arn                    = (known after apply)
      + description            = "Managed by Terraform"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
                # (1 unchanged attribute hidden)
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + description      = "OpenVPN site-to-site from the public address of the lab"
              + from_port        = 1194
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "udp"
              + security_groups  = []
              + self             = false
              + to_port          = 1194
            },
        ]
      + name                   = "zta-lab-vpn-gateway"
      + name_prefix            = (known after apply)
      + owner_id               = (known after apply)
      + region                 = "us-west-2"
      + revoke_rules_on_delete = false
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                 = (known after apply)
    }

  # aws_security_group.workload will be created
  + resource "aws_security_group" "workload" {
      + arn                    = (known after apply)
      + description            = "Managed by Terraform"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
                # (1 unchanged attribute hidden)
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = [
                  + "10.0.0.0/24",
                  + "10.9.0.0/24",
                  + "10.100.0.0/16",
                ]
              + description      = "All traffic from on-prem and VPN clients via tunnel"
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
            },
        ]
      + name                   = "zta-lab-workload"
      + name_prefix            = (known after apply)
      + owner_id               = (known after apply)
      + region                 = "us-west-2"
      + revoke_rules_on_delete = false
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                 = (known after apply)
    }

  # aws_subnet.private will be created
  + resource "aws_subnet" "private" {
      + arn                                            = (known after apply)
      + assign_ipv6_address_on_creation                = false
      + availability_zone                              = (known after apply)
      + availability_zone_id                           = (known after apply)
      + cidr_block                                     = "10.100.10.0/24"
      + enable_dns64                                   = false
      + enable_resource_name_dns_a_record_on_launch    = false
      + enable_resource_name_dns_aaaa_record_on_launch = false
      + id                                             = (known after apply)
      + ipv6_cidr_block                                = (known after apply)
      + ipv6_cidr_block_association_id                 = (known after apply)
      + ipv6_native                                    = false
      + map_public_ip_on_launch                        = false
      + owner_id                                       = (known after apply)
      + private_dns_hostname_type_on_launch            = (known after apply)
      + region                                         = "us-west-2"
      + tags                                           = {
          + "Name" = "zta-lab-private"
        }
      + tags_all                                       = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-private"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                                         = (known after apply)
    }

  # aws_subnet.public will be created
  + resource "aws_subnet" "public" {
      + arn                                            = (known after apply)
      + assign_ipv6_address_on_creation                = false
      + availability_zone                              = (known after apply)
      + availability_zone_id                           = (known after apply)
      + cidr_block                                     = "10.100.0.0/24"
      + enable_dns64                                   = false
      + enable_resource_name_dns_a_record_on_launch    = false
      + enable_resource_name_dns_aaaa_record_on_launch = false
      + id                                             = (known after apply)
      + ipv6_cidr_block                                = (known after apply)
      + ipv6_cidr_block_association_id                 = (known after apply)
      + ipv6_native                                    = false
      + map_public_ip_on_launch                        = true
      + owner_id                                       = (known after apply)
      + private_dns_hostname_type_on_launch            = (known after apply)
      + region                                         = "us-west-2"
      + tags                                           = {
          + "Name" = "zta-lab-public"
        }
      + tags_all                                       = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-public"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                                         = (known after apply)
    }

  # aws_vpc.lab will be created
  + resource "aws_vpc" "lab" {
      + arn                                  = (known after apply)
      + cidr_block                           = "10.100.0.0/16"
      + default_network_acl_id               = (known after apply)
      + default_route_table_id               = (known after apply)
      + default_security_group_id            = (known after apply)
      + dhcp_options_id                      = (known after apply)
      + enable_dns_hostnames                 = true
      + enable_dns_support                   = true
      + enable_network_address_usage_metrics = (known after apply)
      + id                                   = (known after apply)
      + instance_tenancy                     = "default"
      + ipv6_association_id                  = (known after apply)
      + ipv6_cidr_block                      = (known after apply)
      + ipv6_cidr_block_network_border_group = (known after apply)
      + main_route_table_id                  = (known after apply)
      + owner_id                             = (known after apply)
      + region                               = "us-west-2"
      + tags                                 = {
          + "Name" = "zta-lab"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab"
          + "Project" = "zta-migration-lab"
        }
    }

  # random_string.bucket_suffix will be created
  + resource "random_string" "bucket_suffix" {
      + id          = (known after apply)
      + length      = 6
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + numeric     = true
      + result      = (known after apply)
      + special     = false
      + upper       = false
    }

Plan: 26 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + app_private_ip        = "10.100.10.10"
  + data_bucket           = (known after apply)
  + role_user_arns        = {
      + remote-admin      = (known after apply)
      + remote-analyst    = (known after apply)
      + remote-contractor = (known after apply)
      + remote-developer  = (known after apply)
    }
  + vpn_gateway_public_ip = (known after apply)
  ```

`terraform apply -var ssh_key_name=UoL-IA0042` output
```
$ tf apply -var ssh_key_name=UoL-IA0042
data.aws_ami.ubuntu_arm64: Reading...
data.aws_ami.ubuntu_arm64: Read complete after 1s [id=ami-06c11807f6c511068]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
 <= read (data resources)

Terraform will perform the following actions:

  # data.aws_iam_policy_document.s3_read will be read during apply
  # (config refers to values not yet known)
 <= data "aws_iam_policy_document" "s3_read" {
      + id            = (known after apply)
      + json          = (known after apply)
      + minified_json = (known after apply)

      + statement {
          + actions   = [
              + "s3:GetObject",
              + "s3:ListBucket",
            ]
          + resources = [
              + (known after apply),
              + (known after apply),
            ]
        }
    }

  # data.aws_iam_policy_document.s3_write will be read during apply
  # (config refers to values not yet known)
 <= data "aws_iam_policy_document" "s3_write" {
      + id            = (known after apply)
      + json          = (known after apply)
      + minified_json = (known after apply)

      + statement {
          + actions   = [
              + "s3:PutObject",
            ]
          + resources = [
              + (known after apply),
            ]
        }
    }

  # aws_iam_policy.s3_read will be created
  + resource "aws_iam_policy" "s3_read" {
      + arn              = (known after apply)
      + attachment_count = (known after apply)
      + id               = (known after apply)
      + name             = "zta-lab-s3-read"
      + name_prefix      = (known after apply)
      + path             = "/"
      + policy           = (known after apply)
      + policy_id        = (known after apply)
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
    }

  # aws_iam_policy.s3_write will be created
  + resource "aws_iam_policy" "s3_write" {
      + arn              = (known after apply)
      + attachment_count = (known after apply)
      + id               = (known after apply)
      + name             = "zta-lab-s3-write"
      + name_prefix      = (known after apply)
      + path             = "/"
      + policy           = (known after apply)
      + policy_id        = (known after apply)
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
    }

  # aws_iam_user.role_users["remote-admin"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-admin"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-analyst"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-analyst"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-contractor"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-contractor"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user.role_users["remote-developer"] will be created
  + resource "aws_iam_user" "role_users" {
      + arn           = (known after apply)
      + force_destroy = false
      + id            = (known after apply)
      + name          = "remote-developer"
      + path          = "/"
      + tags          = {
          + "Purpose" = "access-matrix-probe"
        }
      + tags_all      = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
          + "Purpose" = "access-matrix-probe"
        }
      + unique_id     = (known after apply)
    }

  # aws_iam_user_policy_attachment.read["remote-admin"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-admin"
    }

  # aws_iam_user_policy_attachment.read["remote-analyst"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-analyst"
    }

  # aws_iam_user_policy_attachment.read["remote-developer"] will be created
  + resource "aws_iam_user_policy_attachment" "read" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-developer"
    }

  # aws_iam_user_policy_attachment.write["remote-admin"] will be created
  + resource "aws_iam_user_policy_attachment" "write" {
      + id         = (known after apply)
      + policy_arn = (known after apply)
      + user       = "remote-admin"
    }

  # aws_instance.app will be created
  + resource "aws_instance" "app" {
      + ami                                  = "ami-06c11807f6c511068"
      + arn                                  = (known after apply)
      + associate_public_ip_address          = (known after apply)
      + availability_zone                    = (known after apply)
      + disable_api_stop                     = (known after apply)
      + disable_api_termination              = (known after apply)
      + ebs_optimized                        = (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      + force_destroy                        = false
      + get_password_data                    = false
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      + id                                   = (known after apply)
      + instance_initiated_shutdown_behavior = (known after apply)
      + instance_lifecycle                   = (known after apply)
      + instance_state                       = (known after apply)
      + instance_type                        = "t4g.micro"
      + ipv6_address_count                   = (known after apply)
      + ipv6_addresses                       = (known after apply)
      + key_name                             = "UoL-IA0042"
      + monitoring                           = (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      + placement_partition_number           = (known after apply)
      + primary_network_interface_id         = (known after apply)
      + private_dns                          = (known after apply)
      + private_ip                           = "10.100.10.10"
      + public_dns                           = (known after apply)
      + public_ip                            = (known after apply)
      + region                               = "us-west-2"
      + secondary_private_ips                = (known after apply)
      + security_groups                      = (known after apply)
      + source_dest_check                    = true
      + spot_instance_request_id             = (known after apply)
      + subnet_id                            = (known after apply)
      + tags                                 = {
          + "Name" = "zta-lab-app"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-app"
          + "Project" = "zta-migration-lab"
        }
      + tenancy                              = (known after apply)
      + user_data                            = <<-EOT
            #!/bin/bash
            apt-get update && apt-get install -y nginx
            sed -i 's/listen 80/listen 8080/' /etc/nginx/sites-available/default
            echo '<h1>AWS lab application</h1>' > /var/www/html/index.html
            systemctl restart nginx
        EOT
      + user_data_base64                     = (known after apply)
      + user_data_replace_on_change          = false
      + vpc_security_group_ids               = (known after apply)

      + capacity_reservation_specification (known after apply)

      + cpu_options (known after apply)

      + ebs_block_device (known after apply)

      + enclave_options (known after apply)

      + ephemeral_block_device (known after apply)

      + instance_market_options (known after apply)

      + maintenance_options (known after apply)

      + metadata_options (known after apply)

      + network_interface (known after apply)

      + primary_network_interface (known after apply)

      + private_dns_name_options (known after apply)

      + root_block_device (known after apply)

      + secondary_network_interface (known after apply)
    }

  # aws_instance.vpn_gateway will be created
  + resource "aws_instance" "vpn_gateway" {
      + ami                                  = "ami-06c11807f6c511068"
      + arn                                  = (known after apply)
      + associate_public_ip_address          = (known after apply)
      + availability_zone                    = (known after apply)
      + disable_api_stop                     = (known after apply)
      + disable_api_termination              = (known after apply)
      + ebs_optimized                        = (known after apply)
      + enable_primary_ipv6                  = (known after apply)
      + force_destroy                        = false
      + get_password_data                    = false
      + host_id                              = (known after apply)
      + host_resource_group_arn              = (known after apply)
      + iam_instance_profile                 = (known after apply)
      + id                                   = (known after apply)
      + instance_initiated_shutdown_behavior = (known after apply)
      + instance_lifecycle                   = (known after apply)
      + instance_state                       = (known after apply)
      + instance_type                        = "t4g.micro"
      + ipv6_address_count                   = (known after apply)
      + ipv6_addresses                       = (known after apply)
      + key_name                             = "UoL-IA0042"
      + monitoring                           = (known after apply)
      + outpost_arn                          = (known after apply)
      + password_data                        = (known after apply)
      + placement_group                      = (known after apply)
      + placement_group_id                   = (known after apply)
      + placement_partition_number           = (known after apply)
      + primary_network_interface_id         = (known after apply)
      + private_dns                          = (known after apply)
      + private_ip                           = (known after apply)
      + public_dns                           = (known after apply)
      + public_ip                            = (known after apply)
      + region                               = "us-west-2"
      + secondary_private_ips                = (known after apply)
      + security_groups                      = (known after apply)
      + source_dest_check                    = false
      + spot_instance_request_id             = (known after apply)
      + subnet_id                            = (known after apply)
      + tags                                 = {
          + "Name" = "zta-lab-vpn-gateway"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-vpn-gateway"
          + "Project" = "zta-migration-lab"
        }
      + tenancy                              = (known after apply)
      + user_data_base64                     = (known after apply)
      + user_data_replace_on_change          = false
      + vpc_security_group_ids               = (known after apply)

      + capacity_reservation_specification (known after apply)

      + cpu_options (known after apply)

      + ebs_block_device (known after apply)

      + enclave_options (known after apply)

      + ephemeral_block_device (known after apply)

      + instance_market_options (known after apply)

      + maintenance_options (known after apply)

      + metadata_options (known after apply)

      + network_interface (known after apply)

      + primary_network_interface (known after apply)

      + private_dns_name_options (known after apply)

      + root_block_device (known after apply)

      + secondary_network_interface (known after apply)
    }

  # aws_internet_gateway.igw will be created
  + resource "aws_internet_gateway" "igw" {
      + arn      = (known after apply)
      + id       = (known after apply)
      + owner_id = (known after apply)
      + region   = "us-west-2"
      + tags_all = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id   = (known after apply)
    }

  # aws_route_table.private will be created
  + resource "aws_route_table" "private" {
      + arn              = (known after apply)
      + id               = (known after apply)
      + owner_id         = (known after apply)
      + propagating_vgws = (known after apply)
      + region           = "us-west-2"
      + route            = [
          + {
              + cidr_block                 = "10.0.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
          + {
              + cidr_block                 = "10.9.0.0/24"
              + network_interface_id       = (known after apply)
                # (12 unchanged attributes hidden)
            },
        ]
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id           = (known after apply)
    }

  # aws_route_table.public will be created
  + resource "aws_route_table" "public" {
      + arn              = (known after apply)
      + id               = (known after apply)
      + owner_id         = (known after apply)
      + propagating_vgws = (known after apply)
      + region           = "us-west-2"
      + route            = [
          + {
              + cidr_block                 = "0.0.0.0/0"
              + gateway_id                 = (known after apply)
                # (12 unchanged attributes hidden)
            },
        ]
      + tags_all         = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id           = (known after apply)
    }

  # aws_route_table_association.private will be created
  + resource "aws_route_table_association" "private" {
      + id             = (known after apply)
      + region         = "us-west-2"
      + route_table_id = (known after apply)
      + subnet_id      = (known after apply)
    }

  # aws_route_table_association.public will be created
  + resource "aws_route_table_association" "public" {
      + id             = (known after apply)
      + region         = "us-west-2"
      + route_table_id = (known after apply)
      + subnet_id      = (known after apply)
    }

  # aws_s3_bucket.data will be created
  + resource "aws_s3_bucket" "data" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = (known after apply)
      + bucket_domain_name          = (known after apply)
      + bucket_namespace            = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_region               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = "us-west-2"
      + request_payer               = (known after apply)
      + tags_all                    = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_public_access_block.data will be created
  + resource "aws_s3_bucket_public_access_block" "data" {
      + block_public_acls       = true
      + block_public_policy     = true
      + bucket                  = (known after apply)
      + id                      = (known after apply)
      + ignore_public_acls      = true
      + region                  = "us-west-2"
      + restrict_public_buckets = true
    }

  # aws_s3_object.probe_seed will be created
  + resource "aws_s3_object" "probe_seed" {
      + acl                    = (known after apply)
      + arn                    = (known after apply)
      + bucket                 = (known after apply)
      + bucket_key_enabled     = (known after apply)
      + checksum_crc32         = (known after apply)
      + checksum_crc32c        = (known after apply)
      + checksum_crc64nvme     = (known after apply)
      + checksum_sha1          = (known after apply)
      + checksum_sha256        = (known after apply)
      + content                = <<-EOT
            seed object for access-matrix read probes
        EOT
      + content_type           = (known after apply)
      + etag                   = (known after apply)
      + force_destroy          = false
      + id                     = (known after apply)
      + key                    = "probe.txt"
      + kms_key_id             = (known after apply)
      + region                 = "us-west-2"
      + server_side_encryption = (known after apply)
      + storage_class          = (known after apply)
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + version_id             = (known after apply)
    }

  # aws_security_group.vpn_gateway will be created
  + resource "aws_security_group" "vpn_gateway" {
      + arn                    = (known after apply)
      + description            = "Managed by Terraform"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
                # (1 unchanged attribute hidden)
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + description      = "OpenVPN site-to-site from the public address of the lab"
              + from_port        = 1194
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "udp"
              + security_groups  = []
              + self             = false
              + to_port          = 1194
            },
        ]
      + name                   = "zta-lab-vpn-gateway"
      + name_prefix            = (known after apply)
      + owner_id               = (known after apply)
      + region                 = "us-west-2"
      + revoke_rules_on_delete = false
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                 = (known after apply)
    }

  # aws_security_group.workload will be created
  + resource "aws_security_group" "workload" {
      + arn                    = (known after apply)
      + description            = "Managed by Terraform"
      + egress                 = [
          + {
              + cidr_blocks      = [
                  + "0.0.0.0/0",
                ]
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
                # (1 unchanged attribute hidden)
            },
        ]
      + id                     = (known after apply)
      + ingress                = [
          + {
              + cidr_blocks      = [
                  + "10.0.0.0/24",
                  + "10.9.0.0/24",
                  + "10.100.0.0/16",
                ]
              + description      = "All traffic from on-prem and VPN clients via tunnel"
              + from_port        = 0
              + ipv6_cidr_blocks = []
              + prefix_list_ids  = []
              + protocol         = "-1"
              + security_groups  = []
              + self             = false
              + to_port          = 0
            },
        ]
      + name                   = "zta-lab-workload"
      + name_prefix            = (known after apply)
      + owner_id               = (known after apply)
      + region                 = "us-west-2"
      + revoke_rules_on_delete = false
      + tags_all               = {
          + "Managed" = "terraform"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                 = (known after apply)
    }

  # aws_subnet.private will be created
  + resource "aws_subnet" "private" {
      + arn                                            = (known after apply)
      + assign_ipv6_address_on_creation                = false
      + availability_zone                              = (known after apply)
      + availability_zone_id                           = (known after apply)
      + cidr_block                                     = "10.100.10.0/24"
      + enable_dns64                                   = false
      + enable_resource_name_dns_a_record_on_launch    = false
      + enable_resource_name_dns_aaaa_record_on_launch = false
      + id                                             = (known after apply)
      + ipv6_cidr_block                                = (known after apply)
      + ipv6_cidr_block_association_id                 = (known after apply)
      + ipv6_native                                    = false
      + map_public_ip_on_launch                        = false
      + owner_id                                       = (known after apply)
      + private_dns_hostname_type_on_launch            = (known after apply)
      + region                                         = "us-west-2"
      + tags                                           = {
          + "Name" = "zta-lab-private"
        }
      + tags_all                                       = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-private"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                                         = (known after apply)
    }

  # aws_subnet.public will be created
  + resource "aws_subnet" "public" {
      + arn                                            = (known after apply)
      + assign_ipv6_address_on_creation                = false
      + availability_zone                              = (known after apply)
      + availability_zone_id                           = (known after apply)
      + cidr_block                                     = "10.100.0.0/24"
      + enable_dns64                                   = false
      + enable_resource_name_dns_a_record_on_launch    = false
      + enable_resource_name_dns_aaaa_record_on_launch = false
      + id                                             = (known after apply)
      + ipv6_cidr_block                                = (known after apply)
      + ipv6_cidr_block_association_id                 = (known after apply)
      + ipv6_native                                    = false
      + map_public_ip_on_launch                        = true
      + owner_id                                       = (known after apply)
      + private_dns_hostname_type_on_launch            = (known after apply)
      + region                                         = "us-west-2"
      + tags                                           = {
          + "Name" = "zta-lab-public"
        }
      + tags_all                                       = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab-public"
          + "Project" = "zta-migration-lab"
        }
      + vpc_id                                         = (known after apply)
    }

  # aws_vpc.lab will be created
  + resource "aws_vpc" "lab" {
      + arn                                  = (known after apply)
      + cidr_block                           = "10.100.0.0/16"
      + default_network_acl_id               = (known after apply)
      + default_route_table_id               = (known after apply)
      + default_security_group_id            = (known after apply)
      + dhcp_options_id                      = (known after apply)
      + enable_dns_hostnames                 = true
      + enable_dns_support                   = true
      + enable_network_address_usage_metrics = (known after apply)
      + id                                   = (known after apply)
      + instance_tenancy                     = "default"
      + ipv6_association_id                  = (known after apply)
      + ipv6_cidr_block                      = (known after apply)
      + ipv6_cidr_block_network_border_group = (known after apply)
      + main_route_table_id                  = (known after apply)
      + owner_id                             = (known after apply)
      + region                               = "us-west-2"
      + tags                                 = {
          + "Name" = "zta-lab"
        }
      + tags_all                             = {
          + "Managed" = "terraform"
          + "Name"    = "zta-lab"
          + "Project" = "zta-migration-lab"
        }
    }

  # random_string.bucket_suffix will be created
  + resource "random_string" "bucket_suffix" {
      + id          = (known after apply)
      + length      = 6
      + lower       = true
      + min_lower   = 0
      + min_numeric = 0
      + min_special = 0
      + min_upper   = 0
      + number      = true
      + numeric     = true
      + result      = (known after apply)
      + special     = false
      + upper       = false
    }

Plan: 26 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + app_private_ip        = "10.100.10.10"
  + data_bucket           = (known after apply)
  + role_user_arns        = {
      + remote-admin      = (known after apply)
      + remote-analyst    = (known after apply)
      + remote-contractor = (known after apply)
      + remote-developer  = (known after apply)
    }
  + vpn_gateway_public_ip = (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

random_string.bucket_suffix: Creating...
random_string.bucket_suffix: Creation complete after 0s [id=m8k415]
aws_iam_user.role_users["remote-analyst"]: Creating...
aws_iam_user.role_users["remote-developer"]: Creating...
aws_iam_user.role_users["remote-contractor"]: Creating...
aws_iam_user.role_users["remote-admin"]: Creating...
aws_vpc.lab: Creating...
aws_s3_bucket.data: Creating...
aws_iam_user.role_users["remote-analyst"]: Creation complete after 1s [id=remote-analyst]
aws_iam_user.role_users["remote-admin"]: Creation complete after 1s [id=remote-admin]
aws_iam_user.role_users["remote-contractor"]: Creation complete after 1s [id=remote-contractor]
aws_iam_user.role_users["remote-developer"]: Creation complete after 1s [id=remote-developer]
aws_vpc.lab: Creation complete after 2s [id=vpc-0e323ba9258e65156]
aws_internet_gateway.igw: Creating...
aws_subnet.private: Creating...
aws_subnet.public: Creating...
aws_security_group.workload: Creating...
aws_security_group.vpn_gateway: Creating...
aws_s3_bucket.data: Creation complete after 2s [id=lab-data-bucket-m8k415]
data.aws_iam_policy_document.s3_read: Reading...
data.aws_iam_policy_document.s3_write: Reading...
aws_s3_bucket_public_access_block.data: Creating...
data.aws_iam_policy_document.s3_write: Read complete after 0s [id=3512013586]
data.aws_iam_policy_document.s3_read: Read complete after 0s [id=3946160476]
aws_s3_object.probe_seed: Creating...
aws_iam_policy.s3_write: Creating...
aws_iam_policy.s3_read: Creating...
aws_s3_bucket_public_access_block.data: Creation complete after 1s [id=lab-data-bucket-m8k415]
aws_s3_object.probe_seed: Creation complete after 1s [id=lab-data-bucket-m8k415/probe.txt]
aws_iam_policy.s3_write: Creation complete after 1s [id=arn:aws:iam::<account-id>:policy/zta-lab-s3-write]
aws_internet_gateway.igw: Creation complete after 1s [id=igw-06f896d5cffcb011e]
aws_iam_user_policy_attachment.write["remote-admin"]: Creating...
aws_route_table.public: Creating...
aws_iam_policy.s3_read: Creation complete after 1s [id=arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.read["remote-developer"]: Creating...
aws_iam_user_policy_attachment.read["remote-analyst"]: Creating...
aws_iam_user_policy_attachment.read["remote-admin"]: Creating...
aws_iam_user_policy_attachment.write["remote-admin"]: Creation complete after 0s [id=remote-admin/arn:aws:iam::<account-id>:policy/zta-lab-s3-write]
aws_iam_user_policy_attachment.read["remote-admin"]: Creation complete after 0s [id=remote-admin/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.read["remote-developer"]: Creation complete after 0s [id=remote-developer/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_iam_user_policy_attachment.read["remote-analyst"]: Creation complete after 0s [id=remote-analyst/arn:aws:iam::<account-id>:policy/zta-lab-s3-read]
aws_subnet.private: Creation complete after 1s [id=subnet-04c7c617caf0628c9]
aws_route_table.public: Creation complete after 1s [id=rtb-0441dc354c986e027]
aws_security_group.vpn_gateway: Creation complete after 3s [id=sg-0d61d59f641036bea]
aws_security_group.workload: Creation complete after 3s [id=sg-0fc7bc85ea7ef3fc3]
aws_instance.app: Creating...
aws_subnet.public: Still creating... [00m10s elapsed]
aws_subnet.public: Creation complete after 12s [id=subnet-01cf32af4e477ea6b]
aws_route_table_association.public: Creating...
aws_instance.vpn_gateway: Creating...
aws_route_table_association.public: Creation complete after 0s [id=rtbassoc-0ab9ce32e86af2f14]
aws_instance.app: Still creating... [00m10s elapsed]
aws_instance.app: Creation complete after 13s [id=i-0d30a5d0816aa57bc]
aws_instance.vpn_gateway: Still creating... [00m10s elapsed]
aws_instance.vpn_gateway: Creation complete after 13s [id=i-08e5aaf4219a04872]
aws_route_table.private: Creating...
aws_route_table.private: Creation complete after 2s [id=rtb-05a9d2c188ba97454]
aws_route_table_association.private: Creating...
aws_route_table_association.private: Creation complete after 1s [id=rtbassoc-08f4025d50d79088c]

Apply complete! Resources: 26 added, 0 changed, 0 destroyed.

Outputs:

app_private_ip = "10.100.10.10"
data_bucket = "lab-data-bucket-m8k415"
role_user_arns = {
  "remote-admin" = "arn:aws:iam::<account-id>:user/remote-admin"
  "remote-analyst" = "arn:aws:iam::<account-id>:user/remote-analyst"
  "remote-contractor" = "arn:aws:iam::<account-id>:user/remote-contractor"
  "remote-developer" = "arn:aws:iam::<account-id>:user/remote-developer"
}
vpn_gateway_public_ip = "<hub-eip>"
```

## 2026-10-04 21:47 | phase-0 | terraform-aws | deployment
Recording `terraform` and provider versions and resolved AMI ID.
```
$ tf -version
Terraform v1.16.4
on darwin_arm64
+ provider registry.terraform.io/hashicorp/aws v6.67.0
+ provider registry.terraform.io/hashicorp/random v3.9.1

Your version of Terraform is out of date! The latest version
is 1.16.5. You can update by downloading from https://developer.hashicorp.com/terraform/install
```

```
AMI_ID=ami-06c11807f6c511068
```
