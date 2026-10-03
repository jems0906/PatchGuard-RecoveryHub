[CmdletBinding()]
param(
    [string]$OutputPath = ".\ad_health_report.csv",
    [int]$StaleDays = 90,
    [int]$PasswordWarningDays = 7,
    [int]$ServiceAccountMaxAgeDays = 90
)

$ErrorActionPreference = "Stop"
Import-Module ActiveDirectory
$cutoff = (Get-Date).AddDays(-$StaleDays)
$results = [System.Collections.Generic.List[object]]::new()

foreach ($dc in Get-ADDomainController -Filter *) {
    try {
        $partners = Get-ADReplicationPartnerMetadata -Target $dc.HostName -Scope Server -ErrorAction Stop
        foreach ($partner in $partners | Where-Object { $_.LastReplicationResult -ne 0 }) {
            $results.Add([pscustomobject]@{
                issue_type = "Replication"; username = ""; object_name = ""; domain_controller = $dc.HostName
                status = "open"; last_logon = ""; lockout_time = ""; last_modified = ""; source = $partner.Partner
                failed_partner = $partner.Partner
                details = "Replication result: $($partner.LastReplicationResult)"
            })
        }
    } catch {
        $results.Add([pscustomobject]@{
            issue_type = "Replication"; username = ""; object_name = ""; domain_controller = $dc.HostName
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = ""; source = ""
            failed_partner = ""
            details = "Unable to read replication metadata: $($_.Exception.Message)"
        })
    }
}

Get-ADUser -Filter 'LockedOut -eq $true' -Properties LockedOut,LockedOutTime,Enabled |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Locked Account"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = $_.LockedOutTime; last_modified = $_.Modified
            source = ""; details = "Account is locked. Confirm identity before unlocking."
            account_enabled = $_.Enabled; is_service_account = $false; password_last_set = ""; password_expires_at = ""; password_age_days = 0
        })
    }
Get-ADComputer -Filter * -Properties LastLogonDate |
    Where-Object { !$_.LastLogonDate -or $_.LastLogonDate -lt $cutoff } |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Stale Computer"; username = ""; object_name = $_.Name; domain_controller = ""
            status = "open"; last_logon = $_.LastLogonDate; lockout_time = ""; last_modified = $_.Modified
            source = ""; details = "No recent computer logon; review before cleanup."
            account_enabled = $true; is_service_account = $false; password_last_set = ""; password_expires_at = ""; password_age_days = 0
        })
    }

$passwordPolicy = Get-ADDefaultDomainPasswordPolicy
Get-ADUser -Filter 'Enabled -eq $true' -Properties PasswordLastSet,PasswordNeverExpires,Enabled |
    Where-Object { !$_.PasswordNeverExpires -and $_.PasswordLastSet } |
    ForEach-Object {
        $expires = $_.PasswordLastSet + $passwordPolicy.MaxPasswordAge
        if ($expires -le (Get-Date).AddDays($PasswordWarningDays)) {
            $results.Add([pscustomobject]@{
                issue_type = "Password Expiry"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
                status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.PasswordLastSet
                source = ""; details = "Password expires on $($expires.ToString('yyyy-MM-dd'))."
                account_enabled = $_.Enabled; is_service_account = $false
                password_last_set = $_.PasswordLastSet.ToString("yyyy-MM-dd")
                password_expires_at = $expires.ToString("yyyy-MM-dd")
                password_age_days = [math]::Max(0, [int]((Get-Date).Date - $_.PasswordLastSet.Date).TotalDays)
            })
        }
    }

Get-ADUser -LDAPFilter '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' -Properties PasswordLastSet,Enabled |
    Where-Object { !$_.PasswordLastSet -or $_.PasswordLastSet -lt (Get-Date).AddDays(-$ServiceAccountMaxAgeDays) } |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Service Account Password Age"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.PasswordLastSet
            source = ""; details = "Service account password is missing or older than $ServiceAccountMaxAgeDays days."
            account_enabled = $_.Enabled; is_service_account = $true
            password_last_set = $(if ($_.PasswordLastSet) { $_.PasswordLastSet.ToString("yyyy-MM-dd") } else { "" })
            password_expires_at = ""
            password_age_days = $(if ($_.PasswordLastSet) { [math]::Max(0, [int]((Get-Date).Date - $_.PasswordLastSet.Date).TotalDays) } else { $ServiceAccountMaxAgeDays + 1 })
        })
    }

Get-ADUser -Filter 'Enabled -eq $false' -Properties whenChanged |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Disabled Account"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.whenChanged
            source = ""; details = "Disabled account requires owner and retention review."
            account_enabled = $false; is_service_account = $false; password_last_set = ""; password_expires_at = ""; password_age_days = 0
        })
    }

$columns = @(
    "issue_type", "username", "object_name", "domain_controller", "dc_status", "last_sync",
    "failed_partner", "status", "last_logon", "lockout_time", "last_modified", "source", "details",
    "account_enabled", "is_service_account", "password_last_set", "password_expires_at", "password_age_days"
)
$results | Select-Object $columns | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Wrote $($results.Count) AD health findings to $OutputPath. This collector performs read-only queries."
