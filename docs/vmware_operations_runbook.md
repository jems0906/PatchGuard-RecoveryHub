# VMware vCenter operations runbook

## Daily monitoring

- Review VM power state, host cluster, datastore, CPU ready time, memory active/ballooning, disk utilization, and VMware Tools status.
- Investigate datastore capacity below the organization's threshold (the demo flags <15% free), elevated CPU ready time, and memory ballooning with the virtualization team.
- Validate application owner and change approval before power operations, resource changes, migrations, or maintenance.
- Review snapshots older than 7 days and urgently review snapshots older than 30 days. Confirm owner/purpose and backup coverage before removal; snapshots are not backups.
- Update VMware Tools through the approved maintenance/change workflow and confirm guest health afterward.

## Inventory and escalation

Import a vCenter export under **Data imports → vCenter VM inventory**. Preserve the source export and timestamp. Escalate capacity/performance risks with VM name, cluster, datastore, observed metrics, and time window. The dashboard is a tracker and does not connect to vCenter or execute infrastructure changes.
