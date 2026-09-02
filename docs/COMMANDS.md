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

### 2.9 Phase 2: build SIEM-01 (2026-09-02)

Everything in this section ran **inside SIEM-01** unless it says otherwise. Commands are in the
order they were run.

#### 2.9.1 Give the root filesystem the whole disk

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
```
```bash
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
```

| | |
|---|---|
| **What** | The first grows the logical volume to use every free extent in the volume group. That changes the size of the block device only. The second grows the ext4 filesystem to fill it. Both are needed. Running only the first leaves the space unusable. |
| **Why** | The Ubuntu guided LVM install gave root 99 GiB of a 200 GB disk and left 99 GiB unallocated, with no error and no warning. |
| **When** | On a mounted, running root filesystem. ext4 supports online growth. No reboot. |
| **Correct result** | `Logical volume ubuntu-vg/ubuntu-lv successfully resized.` then `The filesystem ... is now 51903488 (4k) blocks long.` Confirm with `df -h /`: 97G becomes 195G. |
| **Undo** | **None. Treat as one-way.** Shrinking an ext4 root filesystem needs boot media. |
| **Safe to re-run** | Yes, but pointless. A second run reports the size already matches. |

#### 2.9.2 Static IP on the lab network

```bash
sudo tee /etc/netplan/01-lab-static.yaml > /dev/null <<'EOF'
network:
  version: 2
  ethernets:
    ens37:
      dhcp4: false
      addresses: [10.20.10.10/24]
EOF
```
```bash
sudo chmod 600 /etc/netplan/01-lab-static.yaml
```
```bash
sudo netplan apply
```

**What.** A heredoc writes the file byte for byte. `chmod 600` stops netplan warning about
permissions. `netplan apply` makes it live.
**Why a heredoc and not `nano`.** YAML depends on exact indentation, and pasting into an editor
can add or drop spaces invisibly.
**Why the filename starts with `01`.** Netplan reads files in name order. The installer's file
is `50-cloud-init.yaml` and owns `ens33`. They configure different interfaces and do not fight.
**Correct result.** All three print nothing. Silence is success. Then `ip -brief addr show ens37`
shows `UP  10.20.10.10/24`, and `ip route` shows **exactly one** `default` line, on `ens33`.
**Undo.** `sudo rm /etc/netplan/01-lab-static.yaml && sudo netplan apply`

> **The interface is `ens37`, not `ens34`.** The name comes from the PCI slot:
> `ethernet1.pciSlotNumber = "37"` in the `.vmx`. Always find it with `ip link show`.
> A second `default` route on `ens37` would mean the lab network is carrying internet traffic
> and isolation is broken. Check for it every time.

#### 2.9.3 Stop apt from updating on its own

```bash
sudo systemctl disable --now apt-daily.timer apt-daily-upgrade.timer
```
```bash
sudo sed -i 's/"1"/"0"/' /etc/apt/apt.conf.d/20auto-upgrades && cat /etc/apt/apt.conf.d/20auto-upgrades
```

**What.** The first stops both timers now and removes them from the boot sequence. The second
turns off the two `APT::Periodic` settings, which closes the shutdown-time path the timers do
not cover.
**Why.** Ubuntu 24.04 patches itself on a schedule. A package change inside a capture window
invalidates every run collected before it. **Do this before any long root install**, so an apt
timer cannot fire and take the dpkg lock halfway through.
**Correct result.** Two `Removed "/etc/systemd/system/timers.target.wants/..."` lines, then the
file showing both values as `"0"`. Verify with `systemctl is-enabled apt-daily.timer
apt-daily-upgrade.timer` (expect `disabled` twice).
**Undo.** `sudo systemctl enable --now apt-daily.timer apt-daily-upgrade.timer` and the same
`sed` with `'s/"0"/"1"/'`.

#### 2.9.4 Apply the pending updates once, deliberately

```bash
sudo apt update
```
```bash
sudo apt list --upgradable
```
```bash
sudo apt upgrade -y
```

**Run `apt list --upgradable` and save the output before upgrading.** It is the only record of
what changed and it cannot be recovered afterwards. Watch for `linux-`, `systemd`, `openssh`,
`auditd`, `rsyslog`. Those decide what the machine logs.
**Correct result.** The upgrade ends back at the prompt. Afterwards `apt list --upgradable`
prints only `Listing... Done`, meaning nothing was **kept back**. Then check
`ls /var/run/reboot-required`; silence means no reboot needed.
**Undo.** Not practical. Package downgrades are unreliable. One-way.
**If a purple screen appears** asking which daemons to restart, accept the default. **If one
asks about a modified config file, stop and think.** On a fresh machine it should not appear.

> **The apt record survives a cleared screen.** `sudo tail -60 /var/log/apt/history.log` holds
> the exact command, the timestamps, and every package with old and new version.

#### 2.9.5 Install Wazuh, after reading the installer

```bash
cd ~ && curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh && ls -lh wazuh-install.sh && sha256sum wazuh-install.sh
```
```bash
tmux new -s wazuh
```
```bash
sudo bash ./wazuh-install.sh -a 2>&1 | tee ~/wazuh-install-console.log
```

**Use `4.14`, not `4.x`.** `4.x` returns whatever is newest on the day it runs, which defeats
version pinning.
**Download and read it first.** It runs as root. `grep -n "nodes:" wazuh-install.sh` shows the
config it writes. Lines 97 to 106 proved the all-in-one path issues certificates for `127.0.0.1`,
which is why the Phase 5 NAT disconnect is safe.
**Record the SHA256.** It identifies exactly which file was run. It is **not** a tamper check
unless compared against a checksum published by Wazuh.
**Use `tmux`.** The install runs as root for 10 to 20 minutes. Inside tmux a dropped SSH session
costs nothing; reattach with `tmux attach -t wazuh`. Outside it, the install dies half finished.
**Correct result.** Ends with `INFO: Installation finished.` and prints the admin password.
Then `sudo /var/ossec/bin/wazuh-control info` reports the version.
**If it fails.** Read `/var/log/wazuh-install.log`. Retrying needs `-o` to overwrite, but read
the error first, because a failed install leaves services running.
**Undo.** No clean uninstall. Rebuild the VM.

**Getting the admin password back later:**
```bash
sudo tar -O -xf ~/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```
`-O` prints to the screen instead of unpacking files, so no second plaintext copy is left behind.
The password goes in a password manager. Never in this repo.

#### 2.9.6 Lock the Wazuh version (three locks)

```bash
sudo sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list && cat /etc/apt/sources.list.d/wazuh.list && sudo apt update
```
```bash
sudo apt-mark hold wazuh-manager wazuh-indexer wazuh-dashboard && apt-mark showhold
```

**Why both.** The installer, fetched from the pinned `4.14` path, configures the machine to track
`4.x`. Commenting the repo is one lock. The hold is a second, independent one that still works if
the repo is ever re-added.
**Correct result.** The file line starts with `#deb`, the `apt update` output contains **no**
`packages.wazuh.com` line, and `showhold` lists all three packages.
**Undo.** `sudo sed -i "s/^#deb/deb/" ...` and `sudo apt-mark unhold wazuh-manager wazuh-indexer
wazuh-dashboard`.

#### 2.9.7 Turn on full archiving (the most important change in Phase 2)

```bash
sudo grep -n "logall" /var/ossec/etc/ossec.conf
```
```bash
sudo cp -a /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.pre-logall.bak
```
```bash
sudo sed -i 's|<logall_json>no</logall_json>|<logall_json>yes</logall_json>|' /var/ossec/etc/ossec.conf && sudo grep -n "logall" /var/ossec/etc/ossec.conf
```
```bash
sudo systemctl restart wazuh-manager && sleep 15 && systemctl is-active wazuh-manager
```

**Look before editing.** Wazuh ships `logall_json` present and set to `no`, so this changes a
line rather than adding one. Adding a duplicate XML tag can stop the manager starting.
**`cp -a`, not `cp`.** `ossec.conf` is `root:wazuh` with restricted permissions. `-a` preserves
them, so a restored backup is still readable by the manager.
**`logall` stays `no`.** It writes a second archive in plain text, roughly doubling disk for the
raw line. `logall_json` gives the decoded event with its fields, which is what the unit of
analysis needs.
**Correct result.** `<logall_json>yes</logall_json>` and `active`.
**Undo.** `sudo cp -a /var/ossec/etc/ossec.conf.pre-logall.bak /var/ossec/etc/ossec.conf` then
restart.

#### 2.9.8 Disable Wazuh vulnerability detection

```bash
sudo cp -a /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.pre-vd.bak
```
```bash
sudo sed -i '/<vulnerability-detection>/,/<\/vulnerability-detection>/s|<enabled>yes</enabled>|<enabled>no</enabled>|' /var/ossec/etc/ossec.conf && sudo sed -n '110,120p' /var/ossec/etc/ossec.conf
```
```bash
sudo systemctl restart wazuh-manager && sleep 20 && systemctl is-active wazuh-manager
```

> **The `/start/,/end/` range is not optional.** `ossec.conf` has several
> `<enabled>yes</enabled>` lines and the `<indexer>` block has one immediately below. A plain
> search and replace switches off the indexer too, and Wazuh silently stops storing anything.
> The range confines the edit to the vulnerability block.

**Correct result.** The printed block shows `<vulnerability-detection>` with `no` **and**
`<indexer>` still with `yes`. Then `ossec.log` says
`vulnerability-scanner: INFO: Vulnerability scanner module is disabled.`
**Undo.** Restore `ossec.conf.pre-vd.bak` and restart. Needs internet to rebuild the 12 GB feed,
so reverse it **before** Phase 5 isolation, not after.

#### 2.9.9 On the Windows host

```powershell
ssh-keygen -R 10.20.10.10
```

**What.** Removes every stored host key for that address from `known_hosts`, saving the original
as `known_hosts.old`.
**Why.** An earlier machine had used `10.20.10.10` and SSH refused to connect on the changed key.
**Verify the new key before running this, never after.** Two independent checks were used:
the MAC answering at the address matched `ethernet1.generatedAddress` in the `.vmx`, and the
fingerprint matched the key already trusted for the same host on its NAT address.
**Correct result.** `# Host 10.20.10.10 found: line N` lines, then `... updated.` and
`Original contents retained as ... known_hosts.old`.
**Undo.** Copy `known_hosts.old` back.

**Also changed on the host, through the GUI:** Virtual Network Editor, VMnet8, ticked
**"Connect a host virtual adapter to this network"**. Without it the host has no address on
`192.168.243.0/24` and every SSH attempt to the VM's NAT address times out. This is a host
baseline change, recorded in OPEN-QUESTIONS item 7.

---

### 2.10 Phase 3: build WIN-EP-01 (2026-09-02)

Unless a step says otherwise, commands ran **on the Windows host**. Guest commands were driven
from the host with `vmrun`, so the student never typed inside the VM except where marked
**STUDENT**.

Two shorthands used below:

```powershell
$vmrun = "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe"
$vmx   = "F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx"
$pw    = Get-Content "$env:USERPROFILE\.telos\WIN-EP-01.pw" -Raw
$key   = "$env:USERPROFILE\.telos\siem01_ed25519"
```

#### 2.10.1 Create the virtual disk

```powershell
& "C:\Program Files (x86)\VMware\VMware Workstation\vmware-vdiskmanager.exe" -c -s 80GB -a lsilogic -t 0 "F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmdk"
```

| | |
|---|---|
| **What** | Creates an empty 80 GB virtual disk as one growable file. Growable means the file starts near zero bytes and only grows as Windows writes. It does not reserve 80 GB. |
| **Why** | `-t 0` is single growable, matching the 2026-09-02 decision that F: is NTFS so the 2 GB split option has no purpose. The wizard was avoided because it forces a virtual TPM and VM encryption on a Windows 11 guest. |
| **When** | Folder exists and is empty, no VM running. |
| **Correct result** | Progress dots, then exactly `Virtual disk creation successful.` A `SSLConfigLoad: Failed to load OpenSSL config file.` warning above it is harmless. |
| **Undo** | Delete the `.vmdk`. |
| **Safe to re-run** | **No.** It refuses if the file exists. Delete first. |

The `.vmx` was then written by hand. It is not reproduced here; the file itself is the record, and
the deviations from SIEM-01 are tabulated in `DECISIONS.md`.

#### 2.10.2 **STUDENT**: bypass the Windows 11 hardware check

At the **first** Windows setup screen, press **Shift+F10**, then run all four:

```
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassTPMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassRAMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassCPUCheck        /t REG_DWORD /d 1 /f
```

| | |
|---|---|
| **What** | Sets flags that setup reads before its hardware check. They affect setup only. They do not disable Secure Boot and do not weaken the installed system. |
| **Why** | **Required.** The VM has UEFI and Secure Boot but deliberately no TPM. Setup stops with `This PC doesn't currently meet Windows 11 system requirements` without them. |
| **When** | Before clicking Install. Then `exit` and continue. |
| **Correct result** | `The operation completed successfully.` from each. |
| **Undo** | Not needed. They live only in the temporary setup environment. |
| **Safe to re-run** | Yes. |

Then: **"I don't have a product key"**, edition **`Windows 11 Education`**, **Custom: Install
Windows only**. At the sign-in screen use **Sign-in options** then **Domain join instead**, which
despite its name is the supported route to a plain local account. Username `eli`. Privacy toggles
all off, diagnostic data **Required only**.

#### 2.10.3 Rename, time zone, static IP, adapter names

Run inside the guest by copying a script in and executing it. The changes made were:

```powershell
Rename-Computer -NewName 'WIN-EP-01' -Force
Set-TimeZone -Id 'UTC'
Rename-NetAdapter -Name <old> -NewName 'LAB'   # matched by MAC 00-0C-29-A7-96-32
Rename-NetAdapter -Name <old> -NewName 'NAT'   # matched by MAC 00-0C-29-A7-96-28
Set-NetIPInterface -InterfaceIndex $idx -Dhcp Disabled
New-NetIPAddress -InterfaceIndex $idx -IPAddress '10.20.10.20' -PrefixLength 24
Set-DnsClientServerAddress -InterfaceIndex $idx -ResetServerAddresses
```

| | |
|---|---|
| **What** | Renames the machine, sets the clock to UTC, names the two adapters, and gives the lab adapter a static address with **no gateway** and no DNS. |
| **Why** | The installer named it `DESKTOP-14G5S5G`, and the Wazuh agent registers by hostname, so that name would appear on every event in the results. UTC matches SIEM-01's `Etc/UTC`. No gateway means the lab adapter can never become the default route. DHCP off stops the adapter broadcasting requests nobody answers, which is repeating traffic inside future capture windows. |
| **When** | Before the Wazuh agent is installed. Scripts match adapters by **MAC**, not by name, because names change. |
| **Correct result** | `LAB 10.20.10.20/24 gw=` and `NAT 192.168.243.130/24 gw=192.168.243.2`. The rename needs a reboot; confirm with `ComputerName : WIN-EP-01` afterwards. |
| **Undo** | Each line has a direct reverse. |
| **Safe to re-run** | Yes, the script detects work already done. |

#### 2.10.4 Patch Windows using the built-in update interface

```powershell
$session  = New-Object -ComObject Microsoft.Update.Session
$sr = $session.CreateUpdateSearcher().Search("IsInstalled=0 and IsHidden=0")
# then CreateUpdateDownloader().Download() and CreateUpdateInstaller().Install()
```

| | |
|---|---|
| **What** | Searches, downloads and installs Windows updates through the COM interface built into Windows. It does not reboot by itself. |
| **Why** | The common alternative is the `PSWindowsUpdate` module from the PowerShell Gallery. It was **not** used on purpose: it would add third-party software to the golden image and to the software inventory that Chapter 3 has to describe. The built-in interface adds nothing. |
| **When** | While NAT is connected. Repeat passes until one reports zero. |
| **Correct result** | `install ResultCode: 2` (2 = succeeded, 3 = succeeded with errors, 4 = failed), then on the next pass `updates found: 0`. |
| **Undo** | `wusa /uninstall` per KB. Not normally needed. |
| **Safe to re-run** | Yes, designed for it. |

**Always verify the reboot actually happened** before trusting `updates found: 0`:

```powershell
Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'
(Get-CimInstance Win32_OperatingSystem).LastBootUpTime
```

Both `False` and a recent boot time. A pending reboot makes a zero result meaningless.

#### 2.10.5 Download and hash the artifacts (host)

```powershell
$sha = (gh api repos/SwiftOnSecurity/sysmon-config/commits --jq '.[0].sha')
Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "E:\TeLoS-artifacts\Sysmon.zip" -UseBasicParsing
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/$sha/sysmonconfig-export.xml" -OutFile "E:\TeLoS-artifacts\sysmonconfig-export.xml" -UseBasicParsing
Invoke-WebRequest -Uri "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.7-1.msi" -OutFile "E:\TeLoS-artifacts\wazuh-agent-4.14.7-1.msi" -UseBasicParsing
git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git      "E:\TeLoS-artifacts\atomic-red-team"
git clone --depth 1 https://github.com/redcanaryco/invoke-atomicredteam.git "E:\TeLoS-artifacts\invoke-atomicredteam"
Invoke-WebRequest -Uri "https://www.powershellgallery.com/api/v2/package/powershell-yaml" -OutFile "E:\TeLoS-artifacts\psmodules\powershell-yaml.nupkg" -UseBasicParsing
```

| | |
|---|---|
| **What** | Fetches every artifact to the host, pinning the Sysmon config to an exact commit rather than "whatever was there that day". |
| **Why** | Downloading on the host means each file is hashed **before** it reaches the endpoint, and the guest never runs a browser or a download tool. It also means Phase 5 can disconnect NAT without breaking anything. |
| **When** | Before any of it is copied into the guest. |
| **Correct result** | Every SHA256 is in `DECISIONS.md`. `git rev-parse HEAD` in each clone gives the pinned commit. |
| **Undo** | Delete `E:\TeLoS-artifacts`. |
| **Safe to re-run** | The downloads yes, the clones no (they refuse if the folder exists). |

**`E:\TeLoS-artifacts` must be excluded in Kaspersky first.** Otherwise 66 Atomic Red Team files
are unreadable and the pinned commit stops describing what is on disk. See DECISIONS.md.

#### 2.10.6 Install Sysmon (guest)

```powershell
C:\telos\Sysmon64.exe -accepteula -i C:\telos\sysmonconfig.xml
```

| | |
|---|---|
| **What** | Installs a Windows service and a kernel driver that record process, network, registry, file and DNS activity into their own event channel. |
| **Why** | This is the sensor. Everything T1 measures on the endpoint comes through it. Installed **before** the Wazuh agent so the channel already exists when the agent starts looking for it. |
| **When** | After patching, with no pending reboot. |
| **Correct result** | `Configuration file validated.`, `Sysmon64 installed.`, `SysmonDrv started.`, `Sysmon64 started.` Then `Sysmon64` and `SysmonDrv` both `Running`. |
| **Undo** | `Sysmon64.exe -u` |
| **Safe to re-run** | Refuses if already installed. Use `-c` to change config instead. |

**Then prove the sensor is running the committed file:**

```powershell
C:\telos\Sysmon64.exe -c
```

Look for `Config hash: SHA256=...` and compare it to `lab/configs/sysmonconfig.xml`. They matched
on 2026-09-02. The same output also reports `Image loading : disabled`, which is why Sysmon Event
ID 7 never appears.

#### 2.10.7 Install the Wazuh agent (guest)

```powershell
msiexec.exe /i C:\telos\wazuh-agent-4.14.7-1.msi /q /l*v C:\telos\wazuh-msi.log WAZUH_MANAGER=10.20.10.10 WAZUH_REGISTRATION_SERVER=10.20.10.10 WAZUH_AGENT_NAME=WIN-EP-01
```

| | |
|---|---|
| **What** | Installs the agent silently and registers it with the manager over port 1515. |
| **Why** | The version must match the manager exactly. A mismatch is a silent source of behaviour differences. |
| **When** | SIEM-01 must be **running and reachable** first. Check ports 1514 and 1515 with `Test-NetConnection` before installing. |
| **Correct result** | Exit code `0` (or `3010`, meaning success plus a reboot). Then in `ossec.log`: `Valid key received`, then `(4102): Connected to the server ([10.20.10.10]:1514/tcp).` |
| **Undo** | `msiexec /x` with the same MSI. |
| **Safe to re-run** | Yes, but check for an existing install first. |

**Registration happens when the service starts, not during the MSI.** Checking `client.keys`
before starting the service shows `0 bytes` and looks like a failure. Start the service, then
check. A non-empty `client.keys` with the agent id and name is the proof.

**Add the Sysmon channel**, appended as a new `<ossec_config>` block in `ossec.conf`:

```xml
<ossec_config>
  <localfile>
    <location>Microsoft-Windows-Sysmon/Operational</location>
    <log_format>eventchannel</log_format>
  </localfile>
</ossec_config>
```

Back up the original first. It is kept in the guest as `ossec.conf.telos-orig`, and both hashes
are recorded in `DECISIONS.md`. Restart with `Restart-Service WazuhSvc`.

#### 2.10.8 Unattended access to SIEM-01

Host side:

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.telos\siem01_ed25519" -N '""' -C "telos-harness" -q
```

**STUDENT**, typed **inside an interactive SSH session on SIEM-01**, not piped from PowerShell:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '<the public key line>' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

| | |
|---|---|
| **What** | Installs the harness public key so SSH needs no password. |
| **Why** | Blueprint run-protocol step 10 needs SSH to SIEM-01 for all 101 runs with nobody watching. |
| **When** | Before the Phase 3 check, which reads `archives.json`. |
| **Correct result** | `ssh -i <key> -o BatchMode=yes eli@10.20.10.10 hostname` prints `siem-01`. |
| **Undo** | Delete the `telos-harness` line from `~/.ssh/authorized_keys`. |
| **Safe to re-run** | Yes, but it appends a duplicate line. Harmless. |

**Do not pipe the key file through PowerShell into `ssh`.** Two attempts did that and wrote the
literal **file path** into `authorized_keys`, with a carriage return on the end:
`C:\Users\Elijah\.telos\siem01_ed25519.pub^M$`. It fails silently. `ssh -v` showing the key
offered and rejected is the symptom. Type it inside the SSH session instead.

Then the helper script and its single sudo rule, both **STUDENT**, on SIEM-01:

```bash
sudo install -o root -g root -m 755 /home/eli/telos-archive /usr/local/sbin/telos-archive
```
```bash
printf 'eli ALL=(root) NOPASSWD: /usr/local/sbin/telos-archive\n' | sudo tee /etc/sudoers.d/telos-archive > /dev/null && sudo chmod 440 /etc/sudoers.d/telos-archive && sudo visudo -c
```

| | |
|---|---|
| **What** | Installs a root-owned program with a fixed set of subcommands, then grants `eli` passwordless root for that one file and nothing else. |
| **Why** | `/var/ossec` is mode 750 `root:wazuh` and `eli` is not in the `wazuh` group. Adding `eli` to that group was rejected: it would give the login account write access to the evidence files, and then no one can claim the archives were protected from the harness account. |
| **When** | After the file is staged. **Stage it in the home directory, not `/tmp`.** `/tmp` is cleared on boot and a reboot silently deleted it once. |
| **Correct result** | Silence from the first. From the second, every line `parsed OK`, including `/etc/sudoers.d/telos-archive`. Then `sudo -n /usr/local/sbin/telos-archive size` prints a byte count with no password prompt. |
| **Undo** | `sudo rm /etc/sudoers.d/telos-archive /usr/local/sbin/telos-archive` |
| **Safe to re-run** | Yes. |

**Root ownership is what makes this safe.** If `eli` could edit that file, the sudo rule would be
a direct path to full root.

#### 2.10.9 The Phase 3 check

```powershell
& $vmrun -T ws -gu eli -gp $pw runProgramInGuest $vmx "C:\telos\telos-fence.exe" "START" "telos-p3-check-001"
# Invoke-AtomicTest T1082 -TestNumbers 1 -PathToAtomicsFolder C:\AtomicRedTeam\atomics
& $vmrun -T ws -gu eli -gp $pw runProgramInGuest $vmx "C:\telos\telos-fence.exe" "END" "telos-p3-check-001"
Start-Sleep -Seconds 120
```
```powershell
scp -i $key "$sp\p3pattern.txt" eli@10.20.10.10:/home/eli/p3pattern.txt
ssh -i $key eli@10.20.10.10 "sudo -n /usr/local/sbin/telos-archive count /home/eli/p3pattern.txt"
```

| | |
|---|---|
| **What** | Fires a fence, runs one harmless discovery test, fires a second fence, drains, then counts lines in `archives.json` carrying the run id. |
| **Why** | The runbook's own check. It also exercises the Phase 6 harness design rather than just the plumbing. |
| **When** | Everything else in Phase 3 installed and verified. |
| **Correct result** | Two fence Event ID 1 records on the endpoint, non-zero Sysmon events between them, and a non-zero count in `archives.json`. On 2026-09-02: 2 fences, 14 Sysmon events, 2 matching archive lines. |
| **Undo** | Nothing to undo. |
| **Safe to re-run** | Yes, with a new run id. |

**The search pattern goes in a file, and only the filename is on the command line.** `sudo`
writes every command line to journald, Wazuh collects journald, so a pattern typed on a `sudo`
line creates a new event containing that pattern and inflates its own count. That is
OPEN-QUESTIONS 1b. The helper script's `count` and `show` subcommands take a file for this reason.

**The 120 second drain is not optional.** Measured endpoint-to-archive latency is 1.6 to 1.9
seconds per event, but the agent buffers and the manager writes on its own schedule.

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

### 3.6 SIEM-01 checks (added 2026-09-02)

Run inside SIEM-01. None of these changes anything. All are safe to re-run.

| Command | Checks | Correct result here |
|---|---|---|
| `ip -brief addr show` | Interfaces and addresses | `ens33 UP 192.168.243.129/24`, `ens37 UP 10.20.10.10/24` |
| `ip route` | Routing | **Exactly one** `default` line, and it must be on `ens33` |
| `systemctl status ssh --no-pager` | Is SSH reachable | `Loaded: loaded` and `TriggeredBy: * ssh.socket`. `Active: inactive (dead)` is **correct**, see the trap below |
| `systemctl is-enabled ssh.socket` | Will SSH survive a reboot | `enabled` |
| `sudo ufw status` | Firewall | `Status: inactive`. Recorded as the Phase 2 baseline |
| `lsblk` | Disk layout | `sda 200G`, `sda3 198G`, `ubuntu--vg-ubuntu--lv 198G /` after the extend |
| `df -h /` | Usable space | `195G` total after the extend. `97G` means the extend was not done |
| `sudo vgs && sudo lvs` | LVM free space | `VFree` should be `0` after the extend |
| `systemctl is-active wazuh-manager wazuh-indexer wazuh-dashboard` | Wazuh running | three lines, all `active` |
| `sudo /var/ossec/bin/wazuh-control info` | Wazuh version | `WAZUH_VERSION="v4.14.7"`. Ignore `WAZUH_REVISION` |
| `dpkg -l \| grep -i wazuh \| awk '{print $2, $3}'` | Package versions, short output | three lines, all `4.14.7-1` |
| `apt policy wazuh-manager \| head -3` | Installed vs candidate | both `4.14.7-1` |
| `sudo grep -n "logall" /var/ossec/etc/ossec.conf` | Archiving on | `<logall>no</logall>` and `<logall_json>yes</logall_json>` |
| `sudo grep -n "location>" /var/ossec/etc/ossec.conf` | What Wazuh collects | exactly three: `journald`, `active-responses.log`, `/var/log/dpkg.log` |
| `sudo ls -lh /var/ossec/logs/archives/` | Archives exist | `archives.json` non-zero and growing. `archives.log` at 0 bytes is correct |
| `sudo du -h -d 1 /var/ossec \| sort -h \| tail -12` | Where Wazuh disk goes | `/var/ossec/queue/vd` was 12 GB before the module was disabled |

#### Indexer API checks

```bash
curl -sk -u admin "https://127.0.0.1:9200/_cluster/health?pretty"
```
```bash
curl -sk -u admin "https://127.0.0.1:9200/_cat/indices?v&h=health,status,index,pri,rep,docs.count,store.size"
```
```bash
curl -sk -u admin "https://127.0.0.1:9200/_template/wazuh?filter_path=**.settings&pretty" | grep -E "shards|replicas"
```

**Password handling.** `-u admin` with **no colon and no password** makes curl stop and prompt
for it. Do this always. A password typed on a command line is saved in shell history and is
visible to anyone who can list processes.
**Why `-k` is acceptable here and only here.** The connection goes to `127.0.0.1` on the same
machine. There is no network path for anyone to sit in the middle of. Do not carry this habit to
connections that leave the machine.
**Correct results.** Health: `"status" : "green"`, `"number_of_nodes" : 1`, and
`active_primary_shards` equal to `active_shards` with `unassigned_shards: 0`, which together mean
zero replicas. Indices: every row shows `rep 0`. Template: `"number_of_replicas" : "0"` with
`"auto_expand_replicas" : "0-1"`, which keeps a single node at 0 automatically.

#### Proving archiving works end to end

```bash
logger "TELOS-TEST-EVENT-001"
```
```bash
sudo -i
```
```bash
grep -c "TELOS-TEST-EVENT-001" /var/ossec/logs/archives/archives.json
```
```bash
exit
```

**Correct result.** Exactly `1`.

> **Trap, and it is the important one in this file.** Do **not** run
> `sudo grep -c "MARKER" archives.json`. `sudo` writes every command line to journald, Wazuh
> collects journald, so the search creates a new event containing the marker and counts it.
> One `logger` event returned `2`, then `3`, on repeated searches. Read from a `sudo -i` root
> shell, where individual commands are not logged by `sudo`, or pass the pattern from a file
> with `grep -f` so only the filename appears in the logged command. This does not error. It
> silently inflates counts, and it would do the same to a Phase 6 harness.

#### Two traps worth remembering

**Ubuntu 24.04 SSH looks broken when it is fine.** `systemctl is-active ssh` returns `inactive`
because 24.04 uses socket activation: `systemd` holds port 22 and starts `sshd` only when a
connection arrives. Check `ssh.socket`, or just connect. Do not "fix" `ssh.service`.

**tmux does not scroll with the mouse wheel by default.** Press `Ctrl+B`, release, then `[` to
enter copy mode, move with `PageUp` and the arrow keys, and press `q` to leave. Better habit:
keep the output short in the first place with `| grep -E "..."` or `| head -30`. `apt policy`
alone prints a hundred lines.

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
