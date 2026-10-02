# Active Directory health and troubleshooting runbook

## Health checks

- Confirm domain controllers are online, DNS/service health is good, and FSMO role holders are known.
- Review replication partner metadata and `repadmin /replsummary`; investigate repeated failures, DNS, time skew, RPC/firewall, and site-link problems before forcing synchronization.
- Review locked accounts with the user and source workstation/service logs. Confirm identity and investigate the lockout source before any unlock.
- Review disabled accounts and service-account password age with owners and policy. Use a managed service account where appropriate.
- Find stale computer objects using the approved inactivity threshold; confirm ownership and backup/decommission status before disabling or removing an object.
- Review password expiry warnings with the identity team and notify users through approved channels.

## Safe administrative handling

Unlocks, resets, group membership changes, and computer-object cleanup are privileged actions. Require authorization, ticket/change reference, least privilege, confirmation of target identity, and an audit record. Never automate or perform these write actions from the sample collector.

## Recording

Import read-only health findings into **Active Directory**. Record the responsible domain controller/source, last sync or logon, finding details, owner, and resolution evidence. Clear the finding only after a fresh health check confirms recovery.
