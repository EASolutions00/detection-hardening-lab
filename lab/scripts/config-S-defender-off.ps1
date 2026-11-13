# Config S: Defender's live scanning off, read back until it is really off (not a hardening change)
# Why: C3 is measured with Defender off (DECISIONS 2026-11-03). On 2026-11-13, right after a restart,
#   Set-MpPreference had no effect although the stored values were True; the same command 20 s later worked
#   (COMMANDS 2.13; runbook Phase 5). So the harness runs this after every boot, and a run where it fails is voided.
# Needs Tamper Protection off (runbook Phase 5; OPEN-QUESTIONS 10).
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\config-S-defender-off.ps1   (exit 0 = off)
for ($i = 0; $i -lt 12; $i++) {
    Set-MpPreference -DisableRealtimeMonitoring $true -DisableBehaviorMonitoring $true `
                     -DisableScriptScanning $true -DisableIOAVProtection $true -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    $s = Get-MpComputerStatus
    if (-not $s.RealTimeProtectionEnabled -and -not $s.BehaviorMonitorEnabled -and -not $s.IoavProtectionEnabled) {
        exit 0
    }
}
exit 1
