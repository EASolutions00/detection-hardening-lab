# Change C5: Require Network Level Authentication for Remote Desktop (UserAuthentication = 1)
# Source: control ID (unverified); blueprint row C5. The baseline has Remote Desktop on and NLA off (DECISIONS 2026-11-12).
# Expected telemetry effect (a prediction): 4624 / 4625 distribution shifts.
#   Measured 2026-11-12: with the default client, NLA on and off write the same events (OPEN-QUESTIONS 37).
# No restart needed: NLA applied to the next connection without one (measured 2026-11-12).
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C5-rdp-nla.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C5-rdp-nla.ps1 -Verify   (exit 0 = in effect)
param([switch]$Verify)
$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp'
if ($Verify) {
    $v = (Get-ItemProperty $key -ErrorAction SilentlyContinue).UserAuthentication
    if ($v -eq 1) { exit 0 } else { exit 1 }
}
Set-ItemProperty $key -Name UserAuthentication -Value 1
exit 0
