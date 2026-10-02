[CmdletBinding()]
param(
    [string]$OutputPath = ".\installed_hotfixes.csv"
)

$ErrorActionPreference = "Stop"
$hotfixes = Get-HotFix | ForEach-Object {
    [pscustomobject]@{
        title               = if ($_.Description) { $_.Description } else { "Installed Windows hotfix $($_.HotFixID)" }
        kb_number           = $_.HotFixID
        classification      = "Unknown"
        approval_status     = "Unknown"
        target_group        = "Collected server"
        asset_hostname      = $env:COMPUTERNAME
        installation_status = "installed"
        wave                = "Inventory"
        deployment_date     = if ($_.InstalledOn) { $_.InstalledOn.ToString("yyyy-MM-dd") } else { "" }
    }
}
$hotfixes | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Wrote installed hotfix inventory to $OutputPath. Get-HotFix does not report WSUS approvals or missing updates."
