# Test case K1: "Audit Logon" set to No Auditing (success and failure)
# NOT a hardening change. A configuration mistake made on purpose, with a known answer (OPEN-QUESTIONS 42;
# DECISIONS 2026-11-26). It breaks these benchmark items:
#   DISA Windows 11 STIG WN11-AU-000075 (V-253317): audit Logon successes, CAT II
#   CIS Microsoft Windows 11 Enterprise Benchmark v3.0.0, 17.5.4 "Audit Logon" = Success and Failure (Wazuh check
#   26148; the CIS version the study pins, DECISIONS 2026-11-26). Also 17.5.4 in CIS Intune for Windows 11 v2.0.0.
# Expected result, written before any run: docs/EXPECTED-RESULTS.md, case K1.
# Run by the harness inside WIN-EP-01:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K1-audit-logon-off.ps1           (apply)
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\telos\change-K1-audit-logon-off.ps1 -Verify   (exit 0 = in effect)
# Not in golden-base yet (OPEN-QUESTIONS 42, open points). Not yet run in the guest.
param([switch]$Verify)
if ($env:COMPUTERNAME -ne 'WIN-EP-01') { Write-Error 'This lab script changes security settings. It runs only on WIN-EP-01.'; exit 3 }
$sub = 'Logon'

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
