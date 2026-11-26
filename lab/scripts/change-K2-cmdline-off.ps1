# Test case K2: "Include command line in process creation events" turned off
# NOT a hardening change. A configuration mistake made on purpose, with a known answer (OPEN-QUESTIONS 42;
# DECISIONS 2026-11-26). It breaks these benchmark items:
#   CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0, 18.9.3.1 (Enabled) (Wazuh check 26222; the CIS version the
#   study pins, DECISIONS 2026-11-26). The same number in v5.0.1.
#   DISA Windows 11 STIG WN11-CC-000066
# The golden image sets the value to 1 (baseline-golden.ps1, row "4688 command line").
# Expected result, written before any run: docs/EXPECTED-RESULTS.md, case K2.
# -Verify checks the effect, not only the value: it starts one cmd.exe and reads that process's 4688 event.
#   Whether the value takes effect without a restart is (unverified). If it does not, -Verify exits 1 and the
#   harness voids the run, so a change that did not take effect is never analysed.
# Run by the harness inside WIN-EP-01:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K2-cmdline-off.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K2-cmdline-off.ps1 -Verify   (exit 0 = in effect)
# Not in golden-base yet (OPEN-QUESTIONS 42, open points). Not yet run in the guest.
param([switch]$Verify)
$key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit'
$name = 'ProcessCreationIncludeCmdLine_Enabled'

if ($Verify) {
    $v = (Get-ItemProperty $key -ErrorAction SilentlyContinue).$name
    if ($v -ne 0) { exit 1 }
    $since = Get-Date
    Start-Process -FilePath "$env:SystemRoot\System32\cmd.exe" -ArgumentList '/c', 'rem', 'telos-K2-verify' -Wait -WindowStyle Hidden
    Start-Sleep -Seconds 2
    $events = Get-WinEvent -FilterHashtable @{LogName = 'Security'; Id = 4688; StartTime = $since} -ErrorAction SilentlyContinue
    foreach ($e in $events) {
        $data = ([xml]$e.ToXml()).Event.EventData.Data
        $image = ($data | Where-Object { $_.Name -eq 'NewProcessName' }).'#text'
        if ($image -like '*\cmd.exe') {
            $cmd = ($data | Where-Object { $_.Name -eq 'CommandLine' }).'#text'
            if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 } else { exit 1 }
        }
    }
    exit 1
}
New-ItemProperty $key -Name $name -PropertyType DWord -Value 0 -Force | Out-Null
exit 0
