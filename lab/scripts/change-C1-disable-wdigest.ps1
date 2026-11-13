# Change C1: Disable WDigest (UseLogonCredential = 0)
# Source: DISA V-253358 (Windows 11 STIG); blueprint section 8, row C1
# Expected telemetry effect (a prediction): 4624 logon-type distribution shifts.
#   Measured 2026-11-13: not seen; a console sign-in wrote identical events (OPEN-QUESTIONS 1, "The C1 trial").
# Run by the harness inside WIN-EP-01:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C1-disable-wdigest.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C1-disable-wdigest.ps1 -Verify   (exit 0 = in effect)
param([switch]$Verify)
$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest'
if ($Verify) {
    $v = (Get-ItemProperty $key -ErrorAction SilentlyContinue).UseLogonCredential
    if ($v -eq 0) { exit 0 } else { exit 1 }
}
New-ItemProperty $key -Name UseLogonCredential -PropertyType DWord -Value 0 -Force | Out-Null
exit 0
