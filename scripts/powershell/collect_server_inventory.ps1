[CmdletBinding()]
param(
    [string]$OutputPath = ".\windows_servers.csv"
)

$ErrorActionPreference = "Stop"
$computer = Get-CimInstance -ClassName Win32_ComputerSystem
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$network = Get-CimInstance -ClassName Win32_NetworkAdapterConfiguration -Filter "IPEnabled = True" |
    Select-Object -First 1

[pscustomobject]@{
    hostname       = $computer.Name
    os_version     = $os.Caption
    role           = $computer.DomainRole
    ip_address     = ($network.IPAddress | Where-Object { $_ -match '^\d{1,3}(\.\d{1,3}){3}$' } | Select-Object -First 1)
    domain         = $computer.Domain
    last_boot      = $os.LastBootUpTime.ToString("yyyy-MM-dd")
    asset_type     = "Server"
    app_name       = ""
    service_status = ""
    backup_policy  = ""
} | Export-Csv -Path $OutputPath -NoTypeInformation

Write-Host "Wrote read-only inventory for $($computer.Name) to $OutputPath"
