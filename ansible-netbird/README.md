# NetBird (Phase 2: WireGuard-mesh ZTNA)

Self-hosted NetBird management stack on tpi2-2, authenticating against
the lab Keycloak realm. Wraps NetBird's supported `configure.sh` flow
(clone -> setup.env -> render -> compose up) rather than reimplementing
their compose stack, so upstream template changes are absorbed.

```bash
# vault netbird_client_secret first; must match ansible-keycloak's
# netbird client secret
ansible-playbook -i inventory.yaml site.yaml
```

Peers: tpi2-3 and tpi2-4 run the netbird client as routing peers; an AWS
EC2 peer routes the VPC. Emulated remote workers run the client and
authenticate via Keycloak SSO.

Access policies: see `policies.md` — created via the management API,
exported to `policies-export.json`, and committed as this
implementation's rule-to-policy artifact.

## VERIFY at deployment time (journal these)

- Pin `netbird_version` to a release tag (default `latest` is for first
  contact only) and record image digests.
- NetBird's docs recommend HTTPS for production IdP integration; the
  lab runs plain HTTP on 10.0.0.72. If any component refuses the
  http issuer, terminate TLS for Keycloak (self-signed CA distributed
  to nodes) and update issuer URLs here and in ansible-openziti.
- The Keycloak advanced guide requires a client-scope audience mapping
  for the netbird client and a service account with realm user-view
  permission — follow docs.netbird.io/selfhosted/identity-providers/keycloak
  and journal any manual realm changes, then backport them into
  ansible-keycloak's realm template so the realm stays code.
- setup.env keys drift between NetBird releases; diff against the
  pinned tag's infrastructure_files before first run.
