# lab/configs - Pinned configuration files

Every config file that shapes what the lab emits. These are committed to git so the
experiment can be reconstructed exactly.

## What belongs here

| File | Why it matters |
|---|---|
| `sysmonconfig.xml` | Decides which Sysmon events exist at all. A change here is a telemetry change and silently breaks comparison across runs. |
| `ossec.conf` (relevant blocks) | Must contain `<logall_json>yes</logall_json>`. Without it T1 is impossible. |
| Wazuh agent `<localfile>` block | Points at `Microsoft-Windows-Sysmon/Operational`. |

## Rule

Record the SHA256 of every file here in `docs/DECISIONS.md`, and re-record it if you ever
change one. A config edit halfway through the experiment invalidates every earlier run.

## Never commit here

Passwords, API keys, certificates. Strip credentials out of `ossec.conf` before committing.
