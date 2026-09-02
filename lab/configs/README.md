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

## Git must never rewrite these files

`.gitattributes` marks this whole directory `-text`, meaning git stores the bytes exactly as
they are and converts nothing.

**This is not a style preference. It is load-bearing.** `core.autocrlf` is `true` on the build
host, and on 2026-09-02 it silently rewrote line endings on commit **twice**:

| File | Recorded | What git actually stored |
|---|---|---|
| `sysmonconfig.xml` | 123,257 bytes | 123,256 bytes, different SHA256 |
| `wazuh-agent-ossec.conf` | 11,848 bytes | 11,600 bytes, different SHA256 |

In both cases a clone would have produced a file whose hash did not match the value pinned in
`DECISIONS.md`, which makes the claim that the lab runs the committed config **false**, with no
error anywhere.

The first fix named one file. The second file was missed because of that. **The rule covers the
directory, so a new config added later is protected without anyone remembering to protect it.**

**Verify a pinned file from git itself, not through a shell.** PowerShell redirection re-encodes
and rewrites line endings, so `git show ... > file` measures what PowerShell wrote, not what git
stored:

```bash
git cat-file blob :lab/configs/sysmonconfig.xml | sha256sum
```

## Never commit here

Passwords, API keys, certificates. Strip credentials out of `ossec.conf` before committing.
