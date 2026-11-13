# Change C3: LSA Protection (LSASS as a protected process)
# Source: CIS Microsoft Windows 11 Enterprise Benchmark v5.1.0, 18.9.27.2 (18.9.25.2 in v2.0.0); blueprint row C3
# Stated deviation: RunAsPPL = 2 (no UEFI lock), not the benchmark's "Enabled with UEFI Lock"
#   (DECISIONS 2026-09-29; OPEN-QUESTIONS 18). The baseline has RunAsPPL = 0 (DECISIONS 2026-11-03).
# Expected telemetry effect (a prediction): Sysmon 10 access to lsass.exe changes.
#   Measured 2026-11-13: the dump tools could no longer open lsass.exe; ruled prevention (DECISIONS 2026-11-13).
# Needs a reboot. Confirmed inside the guest, because Wininit event 12 never reaches the archive (OPEN-QUESTIONS 28):
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C3-lsa-protection.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-C3-lsa-protection.ps1 -Verify   (exit 0 = in effect)
param([switch]$Verify)
$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa'
if ($Verify) {
    $boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $e = Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-Wininit'; Id=12; StartTime=$boot} `
         -MaxEvents 1 -ErrorAction SilentlyContinue
    if ($e) { exit 0 } else { exit 1 }
}
New-ItemProperty $key -Name RunAsPPL -PropertyType DWord -Value 2 -Force | Out-Null
exit 0
