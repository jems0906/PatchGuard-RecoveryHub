# WSUS patch management runbook

## Purpose and scope

Use this checklist to plan, deploy, and record Windows Server updates. PatchGuard tracks imported WSUS-style status; it does not control WSUS or install patches.

## Workflow

1. Review the WSUS console synchronization and product/classification settings; confirm the reporting period.
2. Export update metadata and per-computer installation status. Include the update/KB, classification, approval state, target group, computer, status, wave, and deployment date.
3. Import the report under **Data imports → WSUS patch report**. Verify the imported count and inspect a sample of production and test server records.
4. Triage critical/security updates, failed installs, and systems marked `reboot required`. Confirm ownership, maintenance window, application dependency, and rollback/recovery plan.
5. Approve first for a representative test group. Validate application health and event logs; document evidence and change approval.
6. Expand deployment in approved waves. Monitor installation status and pause rollout if failures or service impact exceed the change plan.
7. Reboot only within the approved window. Recheck the update state after restart and verify service health.
8. Close the change with deployment results, exceptions, and a remediation owner/date for outstanding systems.

## Escalation / completion criteria

- Investigate repeated failures with Windows Update logs, free disk space, servicing stack prerequisites, and WSUS connectivity.
- A server is compliant only when its required critical/security updates report installed; a pending reboot is not treated as installed.
- Keep the exported source report and approved change record as audit evidence.
