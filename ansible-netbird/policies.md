# NetBird Access Policies (phase-2 model)

NetBird policies are managed via its management API / dashboard rather
than startup import. To keep them as code, define them with the API and
commit the JSON here; the runbook below creates them idempotently with
curl once a service-user PAT exists (Dashboard -> Users -> Service users).

Model (identical to the OpenZiti dial table and phase-2 matrix):

| Group (from Keycloak role claim) | intranet-web | file-service | postgres | legacy | aws-app |
|---|---|---|---|---|---|
| remote-admin | yes | yes | yes | yes | yes |
| remote-developer | yes | yes | yes | no | yes |
| remote-analyst | yes | yes | yes(ro)* | no | yes |
| remote-contractor | yes | no | no | no | no |

\* network-level allow; read-only is enforced by DB grants (defense in
depth is itself a finding worth noting: mesh ZTNA polices reachability,
not operations — contrast with OpenZiti's per-service model in the
analysis).

Implementation notes:

- Sync Keycloak roles to NetBird groups via the JWT `roles` claim
  (Settings -> Groups -> "Enable JWT group sync", claim name `roles`).
- Resources: define tpi2-3/tpi2-4 peers as routing peers for
  10.0.0.73/32 service ports and the AWS network via a cloud peer.
- One policy per row above: source = role group, destination =
  resource group, protocol/port restricted to the service port.
- Export the final policy set:
  `curl -H "Authorization: Token <PAT>" http://<mgmt>/api/policies`
  and commit as `policies-export.json` — that export is the
  rule-to-policy artifact for this implementation (RQ2).
