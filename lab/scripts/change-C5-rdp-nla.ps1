# Change C5: Require Network Level Authentication for Remote Desktop, set the way Group Policy sets it
# Source: CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0, 18.10.56.3.9.4 (L1): the version Wazuh 4.14.7's scan
#   checks (Wazuh check 26426). 18.10.57.3.9.4 in CIS Windows 10 Enterprise v4.0.0. Blueprint row C5.
#   Group Policy: Computer Configuration > Administrative Templates > Windows Components > Remote Desktop Services >
#   Remote Desktop Session Host > Security > "Require user authentication for remote connections by using Network
#   Level Authentication" = Enabled.
# Since 2026-11-26 (DECISIONS 2026-11-26) it writes the policy key that Group Policy writes and the scan reads:
#   HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services, UserAuthentication = 1.
#   Before, it wrote the listener value (...\Terminal Server\WinStations\RDP-Tcp), which the scan never reads.
# The baseline turns NLA off through the same policy key, value 0 (baseline-golden.ps1, golden-base-v2).
# Expected telemetry effect (a prediction): none with the default client. Measured 2026-11-12 with the listener value
#   (OPEN-QUESTIONS 37); with the policy key (unverified) until the trial in docs/GOLDEN-BASE-V2.md.
# No restart needed for the listener value (measured 2026-11-12); for the policy key (unverified), same trial.
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C5-rdp-nla.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C5-rdp-nla.ps1 -Verify   (exit 0 = in effect)
param([switch]$Verify)
$key = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services'
if ($Verify) {
    $v = (Get-ItemProperty $key -ErrorAction SilentlyContinue).UserAuthentication
    if ($v -eq 1) { exit 0 } else { exit 1 }
}
# Create the key only when it is missing: New-Item -Force on an existing key would empty it.
if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
New-ItemProperty $key -Name UserAuthentication -PropertyType DWord -Value 1 -Force | Out-Null
exit 0
