## 2026-10-10 11:00-16:00 | phase-1 | ansible-openvpn | deployment
Created AWS access keys for the four test users
`remote-admin`
`remote-analyst`
`remote-developer`
`remote-contractor`

Updated `openvpn` version string in `requirements.yaml` to be correct and installed the `openvpn` module.

Having trouble with the lab network and the local gateway. It is owned by the service provider and has limited capabilities. I allows port-forwarding, but only to devices that it has handed out IP addresses to. Working to resolve the problem.

Resolved the problem by setting the MAC address to `00:52:83:67:c2:f5`.
Now the node shows up in the app to allow port-forwarding for `openvpn`.
Port-forwarding for `openvpn` on UDP port 1194 is now setup. I had to
move the IP for the node to the gateway's DHCP range and update
`inventory.yaml` to reflect the change. IPs for some of the other nodes
will also need to be moved to that range for Phase 2.

Code changes were required for Phase 1 to continue. The changes are on
branch `phase-1-network-fixes` and will be merged to main through a PR.
