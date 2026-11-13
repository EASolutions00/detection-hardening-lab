# Golden image baseline for WIN-EP-01 (runbook Phase 5): set the decided baseline, then print a check table.
# Not a hardening change. Run in the guest, in an Administrator PowerShell:
#   powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -WDigest On        (set, then check)
#   powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -Verify -WDigest On (check only)
# Exit code 0 only when every check passes. Some checks pass only after a restart (LSA Protection, TermService).
#
# Each baseline value and its decision:
#   LSA Protection off, RunAsPPL = 0 ............................ DECISIONS 2026-11-03 (C3 turns it on)
#   Remote Desktop on, NLA off, firewall rule to 10.20.10.1 only . DECISIONS 2026-11-12 (C5 turns NLA on)
#   WDigest caching: -WDigest On sets UseLogonCredential = 1; -WDigest Default leaves the value absent
#                    (C1 baseline, decided by the student; C1 sets 0)
# Each value checked and its source:
#   Process Creation and Credential Validation auditing, command line in 4688 ... COMMANDS 2.11; DECISIONS 2026-09-29
#   Sysmon config SHA256 02C43AC8...B3AD ............................................ DECISIONS pinned table
#   Fence tool SHA256 D35C939B...D814; ProcDump 12.02 SHA256 099FD0CD...6BD9 ....... DECISIONS pinned table
#   Tamper Protection off; Defender exclusion C:\AtomicRedTeam ...................... runbook Phase 5; DECISIONS 2026-09-02
#   Change scripts and the Config S script present in C:\telos ...................... lab/scripts/README.md
param([switch]$Verify, [Parameter(Mandatory = $true)][ValidateSet('On', 'Default')][string]$WDigest)

$lsa = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa'
$ts = 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server'
$rdp = "$ts\WinStations\RDP-Tcp"
$wd = 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest'
$fwName = 'Remote Desktop - User Mode (TCP-In)'

if (-not $Verify) {
    New-ItemProperty $lsa -Name RunAsPPL -PropertyType DWord -Value 0 -Force | Out-Null
    Set-ItemProperty $ts -Name fDenyTSConnections -Value 0
    Set-ItemProperty $rdp -Name UserAuthentication -Value 0
    Get-NetFirewallRule -DisplayName $fwName | Set-NetFirewallRule -Enabled True -RemoteAddress 10.20.10.1
    if ($WDigest -eq 'On') {
        New-ItemProperty $wd -Name UseLogonCredential -PropertyType DWord -Value 1 -Force | Out-Null
    } else {
        Remove-ItemProperty $wd -Name UseLogonCredential -ErrorAction SilentlyContinue
    }
}

function Row([string]$check, $value, [string]$want) {
    [pscustomobject]@{ Check = $check; Value = "$value"; Want = $want; OK = ("$value" -eq $want) }
}
function Hash([string]$path) {
    if (Test-Path $path) { (Get-FileHash $path -Algorithm SHA256).Hash } else { 'missing' }
}

$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
$w12 = Get-WinEvent -FilterHashtable @{LogName = 'System'; ProviderName = 'Microsoft-Windows-Wininit'; Id = 12; StartTime = $boot} `
       -MaxEvents 1 -ErrorAction SilentlyContinue
$fw = Get-NetFirewallRule -DisplayName $fwName
$fwAddr = ($fw | Get-NetFirewallAddressFilter).RemoteAddress -join ','
$wdValue = (Get-ItemProperty $wd -ErrorAction SilentlyContinue).UseLogonCredential
$mp = Get-MpComputerStatus
$excl = (Get-MpPreference).ExclusionPath -join ','
$auditPC = (auditpol /get /subcategory:"Process Creation" | Select-String 'Process Creation').ToString().Trim()
$auditCV = (auditpol /get /subcategory:"Credential Validation" | Select-String 'Credential Validation').ToString().Trim()
$cmdline = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit' -ErrorAction SilentlyContinue).ProcessCreationIncludeCmdLine_Enabled

$rows = @(
    Row 'LSA Protection, RunAsPPL' (Get-ItemProperty $lsa).RunAsPPL '0'
    Row 'Wininit event 12 since this boot (after restart)' ($(if ($w12) { 'yes' } else { 'none' })) 'none'
    Row 'Remote Desktop on, fDenyTSConnections' (Get-ItemProperty $ts).fDenyTSConnections '0'
    Row 'NLA off, UserAuthentication' (Get-ItemProperty $rdp).UserAuthentication '0'
    Row 'Firewall rule enabled' $fw.Enabled 'True'
    Row 'Firewall rule remote address' $fwAddr '10.20.10.1'
    Row 'TermService (Running after restart)' (Get-Service TermService).Status 'Running'
    Row 'WDigest UseLogonCredential' ($(if ($null -eq $wdValue) { 'absent' } else { $wdValue })) ($(if ($WDigest -eq 'On') { '1' } else { 'absent' }))
    Row 'Audit Process Creation' ($auditPC -replace '^Process Creation\s+', '') 'Success'
    Row 'Audit Credential Validation' ($auditCV -replace '^Credential Validation\s+', '') 'Success and Failure'
    Row '4688 command line' $cmdline '1'
    Row 'Sysmon config SHA256' (Hash 'C:\telos\sysmonconfig.xml') '02C43AC8EA7B27A9D290C2FE4587A5C184B09FC0AEDA263C2C4E24A4EE43B3AD'
    Row 'Fence tool SHA256' (Hash 'C:\telos\telos-fence.exe') 'D35C939B71ECAC94868947932292531C02A171DECFD3046DEE47DB8E3BD0D814'
    Row 'ProcDump SHA256' (Hash 'C:\AtomicRedTeam\ExternalPayloads\procdump.exe') '099FD0CD771B583D283814A225A8FBBDB3FAA47CC8A644568D6201893AD76BD9'
    Row 'Tamper Protection' $mp.IsTamperProtected 'False'
    Row 'Defender exclusion' $excl 'C:\AtomicRedTeam'
    Row 'Script change-C1 present' (Test-Path 'C:\telos\change-C1-disable-wdigest.ps1') 'True'
    Row 'Script change-C3 present' (Test-Path 'C:\telos\change-C3-lsa-protection.ps1') 'True'
    Row 'Script change-C5 present' (Test-Path 'C:\telos\change-C5-rdp-nla.ps1') 'True'
    Row 'Script config-S present' (Test-Path 'C:\telos\config-S-defender-off.ps1') 'True'
)
$rows | Format-Table -AutoSize | Out-String -Width 220 | Write-Output
$bad = @($rows | Where-Object { -not $_.OK })
Write-Output ("checks passed: {0} of {1}" -f ($rows.Count - $bad.Count), $rows.Count)
if ($bad.Count -eq 0) { exit 0 } else { exit 1 }
