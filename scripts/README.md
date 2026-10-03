# Data collection scripts

The scripts in this directory generate **read-only inventory and report files** for authorized Windows lab environments. They do not install or approve patches, change registry settings, unlock or disable accounts, reset passwords, modify group membership, remove computer objects, or perform backup/restore operations.

## Requirements

- Windows PowerShell 5.1 or later.
- Run only with an account authorized to read the target environment.
- The Active Directory collector requires the RSAT ActiveDirectory module and domain connectivity.
- Review each script and its output fields before use. The sample data is synthetic; do not upload production inventories to a public demo instance.

## Collect reports

From the repository root:

```powershell
.\scripts\powershell\collect_server_inventory.ps1 -OutputPath .\data_samples\windows_servers.csv
.\scripts\powershell\collect_windows_patches.ps1 -OutputPath .\data_samples\installed_hotfixes.csv
.\scripts\powershell\collect_ad_health.ps1 -OutputPath .\data_samples\ad_health_report.csv -StaleDays 90 -PasswordWarningDays 7 -ServiceAccountMaxAgeDays 90
```

`Get-HotFix` reports installed hotfixes only; it is not a WSUS approval or missing-update report. The AD collector exports replication findings, locked and disabled accounts, stale computers, password expiry dates, and service-account password-age evidence. Its CSV columns match the API import fields.

The application imports CSV files transactionally with `python scripts/import_all.py` for checked-in sample reports, or through the authenticated dashboard's **Data imports** page. Imports append rows; review the target database and avoid importing the same report repeatedly.

## Generated synthetic data

To generate reproducible synthetic infrastructure reports without querying a real environment:

```powershell
python scripts\generate_synthetic_infra_data.py --count 25 --seed 7
```

Use the script's `--output` option to write to a separate directory. Generated data is for development and demonstrations only.
