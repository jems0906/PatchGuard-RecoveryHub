# Backup validation and restore testing runbook

## Daily job and SLA review

1. Review Rubrik job results by SLA domain (Gold/Silver/Bronze), protected system, schedule cadence, configured retention days, last successful snapshot, next run, and error detail. Demo freshness thresholds are 2 hours for Gold, 26 hours for Silver, and 8 days for Bronze; set these and each schedule/retention value to the actual contractual RPO/SLA before use.
2. Investigate failed/partial jobs before the next recovery point objective is breached. Confirm cluster/connector health, capacity, credentials, and source-system availability.
3. Check every protected system is associated with the correct SLA domain and retention policy. Escalate systems without a recent successful backup.

## Restore evidence

1. Select representative systems and data sets according to the recovery test schedule and business criticality.
2. Obtain owner/change approval, choose an isolated restore target, and document the recovery point and expected recovery time.
3. Restore without overwriting production. Validate boot/application/data integrity with the service owner.
4. Record test date, result, tester, evidence location, actual recovery time, and any corrective actions.
5. Reconcile any failed test or expired test coverage with an owner and deadline.

PatchGuard records imported job/test evidence and a coverage indicator. It does not initiate backup or restore operations; never treat an imported `success` row as proof of a tested restore.
