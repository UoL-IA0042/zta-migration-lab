# Keycloak Identity Provider (Realm-as-Code)

Deploys Keycloak 26.7.3 (official multi-arch image, ARM64-native on the
RK1) with PostgreSQL backing on tpi2-2. The entire realm — the four
experimental roles, one test user per role, and OIDC clients for
OpenZiti and NetBird — is a templated JSON artifact imported at startup
via `--import-realm`. Identity configuration is therefore code:
versioned, diffable, and reproducible with zero console clicks.

## Files

- `inventory.yaml` - tpi2-2
- `group_vars/all.yaml` - versions, roles, users, clients (vault the secrets)
- `templates/realm-lab.json.j2` - the realm definition
- `templates/docker-compose.yaml.j2` - Keycloak + PostgreSQL stack
- `site.yaml` - deploy, health-check, verify realm import

## Usage

```bash
# vault every CHANGE-ME in group_vars/all.yaml first
ansible-playbook -i inventory.yaml site.yaml
```

The playbook ends by fetching the realm's OIDC discovery document and
printing the issuer URL — the value OpenZiti and NetBird need for their
IdP integration.

## Design notes

- Role names match the OpenVPN client identities and test-matrix roles
  exactly; a realm-role protocol mapper puts them in a `roles` claim in
  access tokens, which both ZTNA control planes consume for policy.
- `directAccessGrantsEnabled` is on so the test harness can obtain
  tokens headlessly (password grant) for `auth_token_env` HTTP probes.
- Realm changes are made by editing the template and re-running the
  playbook (which force-recreates on change), not in the admin console.
  Note `--import-realm` skips import if the realm already exists — a
  changed realm therefore needs `docker compose down` plus removal of
  the realm via API, or simply a clean re-deploy per the reproducibility
  procedure. For the lab, clean re-deploys are the intended workflow.
- Plain HTTP on the lab network keeps the experiment focused; terminate
  TLS in front (or set KC_HOSTNAME to an https URL with certs) if a
  ZTNA component refuses http issuers — NetBird in particular expects
  https in production configurations.

## Verified

Realm template renders to valid JSON with correct roles/users/clients;
compose template renders to valid YAML.
