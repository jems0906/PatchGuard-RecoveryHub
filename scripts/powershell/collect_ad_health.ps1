[CmdletBinding()]
param(
    [string]$OutputPath = ".\ad_health_report.csv",
    [int]$StaleDays = 90,
    [int]$PasswordWarningDays = 7,
    [int]$ServiceAccountMaxAgeDays = 180
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
                details = "Replication result: $($partner.LastReplicationResult)"
            })
        }
    } catch {
        $results.Add([pscustomobject]@{
            issue_type = "Replication"; username = ""; object_name = ""; domain_controller = $dc.HostName
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = ""; source = ""
            details = "Unable to read replication metadata: $($_.Exception.Message)"
        })
    }
}

Get-ADUser -Filter 'LockedOut -eq $true' -Properties LockedOut,LockedOutTime |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Locked Account"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = $_.LockedOutTime; last_modified = $_.Modified
            source = ""; details = "Account is locked. Confirm identity before unlocking."
        })
    }
Get-ADComputer -Filter * -Properties LastLogonDate |
    Where-Object { !$_.LastLogonDate -or $_.LastLogonDate -lt $cutoff } |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Stale Computer"; username = ""; object_name = $_.Name; domain_controller = ""
            status = "open"; last_logon = $_.LastLogonDate; lockout_time = ""; last_modified = $_.Modified
            source = ""; details = "No recent computer logon; review before cleanup."
        })
    }

$passwordPolicy = Get-ADDefaultDomainPasswordPolicy
Get-ADUser -Filter 'Enabled -eq $true' -Properties PasswordLastSet,PasswordNeverExpires |
    Where-Object { !$_.PasswordNeverExpires -and $_.PasswordLastSet } |
    ForEach-Object {
        $expires = $_.PasswordLastSet + $passwordPolicy.MaxPasswordAge
        if ($expires -le (Get-Date).AddDays($PasswordWarningDays)) {
            $results.Add([pscustomobject]@{
                issue_type = "Password Expiry"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
                status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.PasswordLastSet
                source = ""; details = "Password expires on $($expires.ToString('yyyy-MM-dd'))."
            })
        }
    }

Get-ADUser -LDAPFilter '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' -Properties PasswordLastSet |
    Where-Object { !$_.PasswordLastSet -or $_.PasswordLastSet -lt (Get-Date).AddDays(-$ServiceAccountMaxAgeDays) } |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Service Account Password Age"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.PasswordLastSet
            source = ""; details = "Service account password is missing or older than $ServiceAccountMaxAgeDays days."
        })
    }

$disabledCutoff = (Get-Date).AddDays(-$StaleDays)
Get-ADUser -Filter 'Enabled -eq $false' -Properties whenChanged |
    Where-Object { !$_.whenChanged -or $_.whenChanged -lt $disabledCutoff } |
    ForEach-Object {
        $results.Add([pscustomobject]@{
            issue_type = "Disabled Account"; username = $_.SamAccountName; object_name = ""; domain_controller = ""
            status = "open"; last_logon = ""; lockout_time = ""; last_modified = $_.whenChanged
            source = ""; details = "Disabled account requires owner and retention review."
        })
    }

$results | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Wrote $($results.Count) AD health findings to $OutputPath. This collector performs read-only queries."
