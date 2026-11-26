# Test case K3: "Audit Process Creation" set to No Auditing
# NOT a hardening change. A configuration mistake made on purpose, with a known answer (OPEN-QUESTIONS 42;
# DECISIONS 2026-11-26). It breaks this benchmark item:
#   CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0, 17.3.2 "Audit Process Creation" includes Success (Wazuh check
#   26144; the CIS version the study pins, DECISIONS 2026-11-26). The same number in v5.0.1.
# The golden image sets it to Success (baseline-golden.ps1; DECISIONS 2026-09-29). It was removed from the hardening
# catalogue on 2026-09-08 because CIS requires it on (lab/scripts/README.md); here it returns as a test case only.
# Expected result, written before any run: docs/EXPECTED-RESULTS.md, case K3.
# Run by the harness inside WIN-EP-01:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K3-audit-process-creation-off.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K3-audit-process-creation-off.ps1 -Verify   (exit 0 = in effect)
# Not in golden-base yet (OPEN-QUESTIONS 42, open points). Not yet run in the guest.
param([switch]$Verify)
$sub = 'Process Creation'

function Get-Inclusion([string]$name) {
    # auditpol /r prints CSV; the subcategory row's "Inclusion Setting" is the audit state.
    $rows = auditpol /get /subcategory:"$name" /r | Where-Object { $_ -match ',' } | ConvertFrom-Csv
    return ($rows | Where-Object { $_.Subcategory -eq $name }).'Inclusion Setting'
}

if ($Verify) {
    if ((Get-Inclusion $sub) -eq 'No Auditing') { exit 0 } else { exit 1 }
}
auditpol /set /subcategory:"$sub" /success:disable /failure:disable | Out-Null
exit $LASTEXITCODE
