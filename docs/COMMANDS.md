# Commands: what was run, why, and what correct looks like

Every command run on this machine for this project. Grouped by whether it changed
the machine, because that is what matters when something goes wrong.

Newest work is at the bottom of each section. If you add a command, add it here.

---

## Part 1: Commands the student ran

Only two. Both were steps that could not be delegated.

### 1.1 Turn off the Windows hypervisor

```
bcdedit /set hypervisorlaunchtype off
```

| | |
|---|---|
| **What** | Tells Windows not to start its own hypervisor at boot. `bcdedit` edits the boot configuration. |
| **Why** | Hyper-V was on, so Windows ran a hypervisor and VMware ran on top of it instead of directly on hardware. That adds timing changes, and this thesis measures timing variance. |
| **When** | Before building any VM. Doing it after the golden snapshot would change VM timing partway through and invalidate earlier runs. |
| **Where** | Admin terminal. Right-click Start, then Terminal (Admin). Then restart the computer. A sign-out is not enough. |
| **Correct result** | `The operation completed successfully.` Then after restart, `HypervisorPresent` reads `False`. |
| **If it fails** | "Access is denied" means the terminal is not running as administrator. |
| **Undo** | `bcdedit /set hypervisorlaunchtype auto` then restart. Also re-enables Docker Desktop, WSL2, and host Credential Guard, none of which are used here. |
| **Safe to re-run** | Yes, it is idempotent. |

**This must stay off for the whole experiment.** It is part of the host baseline, like a
pinned version. See DECISIONS.md, 2026-08-20.

### 1.2 Log in to GitHub

```
gh auth login
```

| | |
|---|---|
| **What** | Connects the GitHub command line tool to the account and stores a token. |
| **Why** | So pushes and repo creation work from the terminal instead of the website. |
| **When** | Once, after gh was installed. Not repeated unless the token is revoked. |
| **Where** | The student's own terminal. Claude cannot enter account credentials. |
| **Answers** | GitHub.com, HTTPS, Yes, Login with a web browser. |
| **Correct result** | `✓ Logged in to github.com account EASolutions00 (keyring)` with scopes `gist, read:org, repo, workflow`. |
| **Safe to re-run** | Yes, it replaces the existing token. |

---

## Part 2: Commands that CHANGED the machine

### 2.1 Install the GitHub CLI

```
winget install --id GitHub.cli -e --accept-source-agreements --accept-package-agreements --silent
```

**What.** Installs `gh` 2.97.0 to `C:\Program Files\GitHub CLI`.
**Why.** To create and push the repo from the terminal.
**Correct result.** `Successfully installed`, then `gh --version` prints `gh version 2.97.0`.
**Undo.** `winget uninstall GitHub.cli`

**Important.** In the Bash tool gh is not on the path automatically. Every gh command needs
this first:

```bash
export PATH="$PATH:/c/Program Files/GitHub CLI"
```

### 2.2 Create the git repository

```
git init -b main
```

**What.** Creates the hidden `.git` folder that records every version of every file.
`-b main` names the first branch `main`.
**When.** Once per project. Never again for this folder.
**Correct result.** `Initialized empty Git repository in E:/Claude general/.git/`

### 2.3 Move the source documents into folders

```
mv "T1_Detection of Hardening-Induced Blind Spots.txt" thesis/T1/proposal.txt
```

**What.** Renames and relocates. Content unchanged.
**Risk.** `mv` overwrites the target silently if it exists. Check the target first.

### 2.4 Create the public repo and push

```
gh repo create detection-hardening-lab --public --source=. --remote=origin --push
```

**What.** Four actions at once: creates the repo on GitHub, sets it public, links the local
folder as `origin`, and uploads all commits.
**When.** Once. After this, use `git push`.
**Correct result.** Prints the URL, then `* [new branch] HEAD -> main`.

### 2.5 Purge a file from all git history

```
pip install git-filter-repo
python "C:/Users/Elijah/AppData/Roaming/Python/Python313/site-packages/git_filter_repo.py" --path docs/AI-RULES.txt --invert-paths --force
git remote add origin https://github.com/EASolutions00/detection-hardening-lab.git
git push --force -u origin main
```

**What.** Deleting a file in git does not remove it from history. `git-filter-repo` rebuilds
every commit without it. `--invert-paths` means remove this path rather than keep only it.
**Why.** `AI-RULES.txt` held personal preferences and did not belong in a public portfolio.
**Side effects.** It removes the `origin` remote on purpose, as a safety measure, which is why
it has to be re-added. It also changes every commit ID.
**Correct result.** `gh api repos/EASolutions00/detection-hardening-lab/contents/docs/AI-RULES.txt`
returns `404 Not Found`. **The 404 is the success signal.**

> **This is the most dangerous command in this project.** It was safe because the repo was
> minutes old and nobody had cloned it. If anyone has a copy, a force push breaks theirs, and
> the deleted file comes back when they push. Ask before using it again.

### 2.6 Create the Python virtual environment

```
"C:\Program Files\Python313\python.exe" -m venv .venv
```

**What.** Creates a private Python installation in `E:\Claude general\.venv`. Packages here
do not touch system Python.
**When.** Once per project.
**Correct result.** `.venv\Scripts\python.exe --version` prints `Python 3.13.14`, and
`git check-ignore .venv` prints `.venv`, confirming git ignores it.

### 2.7 Install the analysis packages

```
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

| Package | Used for |
|---|---|
| numpy 2.5.2 | Arrays, mean, standard deviation |
| scipy 1.18.1 | Chi-square, normal tail, Benjamini-Hochberg correction |
| pandas 3.0.5 | Tables, not used by the core yet |
| PyYAML 6.0.3 | Sigma rule parsing, not written yet |
| pytest 9.1.1 | Tests |

**Correct result.** Versions print, and this import succeeds:
```
from scipy.stats import false_discovery_control
```
That import matters: it means statsmodels is not needed.

**Do not upgrade these mid-experiment.** A version bump makes earlier runs incomparable.

### 2.8 Clone SigmaHQ to count STP annotations

```
git clone --depth 1 https://github.com/SigmaHQ/sigma.git
git rev-parse HEAD
grep -rlE '^\s*-\s*stp\.[0-9]' rules* --include='*.yml' | wc -l
```

**What.** Downloads the Sigma rule corpus. `--depth 1` takes only the latest version, not the
full history, which is far faster.
**Why.** To count rules carrying a Summiting the Pyramid annotation. This decided whether T3
was a real fallback. It was not: 6 of 3,783.
**Correct result.** 4,767 files, commit `da9bb07d642a2826e89702445d32c795209ec108`.

> **Trap.** A plain `grep stp.` returns 19 files, and 13 are false hits on `cmstp.exe` and
> `chrmstp.exe`, which are Windows binaries many rules mention. Match the tag line
> `- stp.<digit>`, never the bare substring. Trusting the first number would have called T3
> safe when it is not.

**Record the commit hash.** Without it the count is not reproducible.

---

## Part 3: Read-only checks (safe, change nothing)

### 3.1 Hardware and Windows state

| Command | Checks | Correct result here |
|---|---|---|
| `Get-Volume` | Free disk space | F: 732 GB, C: 315 GB, E: 2348 GB |
| `(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled` | AMD SVM in BIOS | `True` |
| `(Get-CimInstance Win32_ComputerSystem).HypervisorPresent` | Windows hypervisor running | `False` |
| `Get-CimInstance -Namespace root\Microsoft\Windows\DeviceGuard Win32_DeviceGuard` | VBS status | `0` (off). `2` means running. |
| `Get-CimInstance Win32_OptionalFeature -Filter "Name='Microsoft-Hyper-V-All'"` | Is Hyper-V enabled | Was `Enabled`, now irrelevant since boot launch is off |
| `bcdedit /enum '{current}'` | Boot settings | Shows `hypervisorlaunchtype` |

### 3.2 VMware

```
"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws list
```

**What.** Lists running VMs. `-T ws` means VMware Workstation.
**Why.** The Phase 0 proof that vmrun works. The whole harness calls vmrun, so if this fails,
nothing later works.
**Correct result.** `Total running VMs: 0`. Zero is correct with no VMs built. The point is
that it answered at all.

### 3.3 Git and GitHub

| Command | Checks | Correct result |
|---|---|---|
| `git status --short` | Unsaved changes | **Blank means everything is saved** |
| `git log --oneline` | Commit history | Newest first |
| `git ls-files` | What is tracked | Must NOT list `.venv` or files under `data/runs/` |
| `git check-ignore .venv` | Is it ignored | Prints `.venv` |
| `git log --format='%h %ad %s' --date=format:'%Y-%m-%d'` | Real commit dates | Used to catch two wrongly dated WORKLOG entries |
| `gh auth status` | Logged in | `EASolutions00` |
| `gh repo view --json name,visibility,url` | Repo state | `detection-hardening-lab \| PUBLIC` |
| `gh api repos/OWNER/REPO/license --jq '.license.spdx_id'` | License detected | `MIT` |

### 3.4 Reading a .docx without pandoc

Pandoc is **not installed** on this machine. Neither is LibreOffice. A `.docx` is a zip of XML,
so Python's built-in `zipfile` and `xml.etree.ElementTree` read it directly.

**Why it mattered.** The Gantt schedule is drawn as **colored cell shading**, not text. Plain
text extraction loses it entirely. The shading is read from the `w:shd` element's `w:fill`
attribute in each cell's `w:tcPr`.

### 3.5 The date

```
date '+%Y-%m-%d %A'
```

**Why it mattered.** It caught a real error. Two WORKLOG entries were dated 2026-08-19 based on
file timestamps, but `git log` showed the work happened 2026-08-20. Both were corrected.

**Lesson.** Use `date` for the current date and `git log` for when past work happened. Never
infer a date from a file timestamp.

---

## Part 4: The five commands used from now on

### Run the system

```bash
.venv/Scripts/python.exe src/demo.py
```
**Correct result.** The noise floor table, the analysis, then the Stage D comparison showing
naive at 20.0% precision and the proposed system at 100%.

### Run the tests

```bash
.venv/Scripts/python.exe -m pytest tests -v
```
**Correct result.** `20 passed`.
**If any test fails, stop.** A failing test means the analysis gives wrong answers. Fix it
before writing more code.

### Check what changed

```bash
git status --short
```
**Correct result.** Blank means saved. `M` is modified, `??` is a new untracked file.

### Save the work

```bash
git add -A
```
```bash
git commit -m "short description of what changed"
```
```bash
git push
```
**When.** At minimum at the end of every runbook phase, per the rule in CLAUDE.md. More often
is better.
**Correct result.** `git status --short` prints nothing afterwards.

### Rebuild the environment on another machine

```bash
"C:\Program Files\Python313\python.exe" -m venv .venv
```
```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

---

## Part 5: Pre-flight check

Run all four before starting a runbook phase. All four must pass.

```bash
"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws list
```
Expect `Total running VMs: 0`

```powershell
(Get-CimInstance Win32_ComputerSystem).HypervisorPresent
```
Expect `False`. **If it says True, the hypervisor came back and timing is compromised.**
Re-run the Part 1.1 command and restart.

```bash
.venv/Scripts/python.exe -m pytest tests -q
```
Expect `20 passed`

```bash
git status --short
```
Expect blank
