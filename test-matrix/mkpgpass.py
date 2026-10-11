#!/usr/bin/env python3
"""Write the probing machine's ~/.pgpass for the test-matrix postgres probes.

Reads the decrypted ansible-workloads vault on stdin and writes one
.pgpass line per experimental role, so psql picks each role's password
from the -U user (no PGPASSWORD switching between runs). Passwords are
never printed.

Usage (from the repo root):
    ansible-vault view --vault-password-file .vault-pass \\
        ansible-workloads/group_vars/all/vault.yaml \\
      | test-matrix/.venv/bin/python test-matrix/mkpgpass.py
    unset PGPASSWORD    # an exported PGPASSWORD overrides .pgpass

- Replaces only this lab's entries (host:port:db prefix below); other
  lines in the file are kept, so re-running after a vault change is safe.
- Escapes ':' and '\\' as .pgpass requires; sets mode 0600 (psql ignores
  the file otherwise).
- PGPASSFILE overrides the target path.

Keep HOST/DB and ROLES in sync with docs/addressing.md and the workloads
vault keys (vault_db_role_<role with _>_password).
"""

import os
import sys

import yaml

HOST, PORT, DB = "10.0.0.73", "5432", "labdb"
ROLES = ["remote-admin", "remote-developer", "remote-analyst", "remote-contractor"]


def esc(value):
    # .pgpass needs backslash and colon escaped
    return str(value).replace("\\", "\\\\").replace(":", "\\:")


def main():
    vault = yaml.safe_load(sys.stdin)
    if not isinstance(vault, dict):
        sys.exit("expected the decrypted vault YAML on stdin")
    prefix = ":".join([HOST, PORT, DB]) + ":"
    new = []
    for role in ROLES:
        key = "vault_db_role_" + role.replace("-", "_") + "_password"
        if key not in vault:
            sys.exit(f"vault has no {key}")
        new.append(prefix + role + ":" + esc(vault[key]))

    path = os.path.expanduser(os.environ.get("PGPASSFILE", "~/.pgpass"))
    old = []
    if os.path.exists(path):
        with open(path) as fh:
            old = fh.read().splitlines()
    keep = [line for line in old if not line.startswith(prefix)]
    with open(path, "w") as fh:
        fh.write("\n".join(keep + new) + "\n")
    os.chmod(path, 0o600)
    print("wrote", len(new), "lab entries to", path)


if __name__ == "__main__":
    main()
