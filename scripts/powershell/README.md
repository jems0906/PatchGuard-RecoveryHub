# Windows lab collectors

These examples are **read-only inventory/report collectors**. They do not approve or install updates, unlock users, reset passwords, modify group membership, clean up computer objects, or change registry values. Review scripts locally before use; run only with authorized accounts and the minimum read permissions required.

Run from an elevated PowerShell session only if your environment requires it:

```powershell
.\collect_server_inventory.ps1 -OutputPath .\windows_servers.csv
.\collect_windows_patches.ps1 -OutputPath .\installed_hotfixes.csv
.\collect_ad_health.ps1 -OutputPath .\ad_health_report.csv -StaleDays 90 -PasswordWarningDays 7 -ServiceAccountMaxAgeDays 180
```

The Active Directory collector requires the RSAT ActiveDirectory module. `Get-HotFix` reports installed hotfixes only; it is not a WSUS approval or missing-update report. Validate field values and schema mappings before importing a generated report. Do not upload production inventories to a public demo deployment.
