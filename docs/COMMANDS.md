# Commands: what was run, why, and what correct looks like

Every command run on this machine for this project. Grouped by whether it changed
the machine, because that is what matters when something goes wrong.

Newest work is at the bottom of each section. If you add a command, add it here.

---

## Part 1: Commands I ran by hand

Steps that could not be delegated, because they need an admin shell or my own account.

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
| **Where** | My own terminal. Account credentials are never delegated. |
| **Answers** | GitHub.com, HTTPS, Yes, Login with a web browser. |
| **Correct result** | `✓ Logged in to github.com account EASolutions00 (keyring)` with scopes `gist, read:org, repo, workflow`. |
| **Safe to re-run** | Yes, it replaces the existing token. |

### 1.3 Re-enable the VMware host adapters (2026-09-26)

Device Manager, Network adapters, right-click each `VMware Virtual Ethernet Adapter for VMnetN`,
Enable device. Or in an admin shell:

```powershell
Get-PnpDevice -FriendlyName "VMware Virtual Ethernet Adapter for VMnet2" | Enable-PnpDevice -Confirm:$false
```

| | |
|---|---|
| **What** | Turns a disabled VMware virtual adapter back on. |
| **Why** | On 2026-09-26 all four were disabled (`CM_PROB_DISABLED`), cause unknown, so the host could not reach SIEM-01. See OPEN-QUESTIONS 27. |
| **Where** | Admin rights. It is a host system setting. |
| **Correct result** | `Get-PnpDevice -Class Net` shows the adapter as `OK`, `CM_PROB_NONE`. On 2026-09-26 all four were enabled. |
| **Safe to re-run** | Yes. |

### 1.4 Give VMnet2 its host address back (2026-09-26)

```powershell
New-NetIPAddress -InterfaceAlias "VMware Network Adapter VMnet2" -IPAddress 10.20.10.1 -PrefixLength 24
```

| | |
|---|---|
| **What** | Sets the host's lab address, with no gateway and no DNS. |
| **Why** | After 1.3, VMnet2 came back with only a Windows fallback address, `169.254.5.96`. The harness and SSH need `10.20.10.1`. |
| **Where** | Admin shell. |
| **Correct result** | Two blocks print. The `ActiveStore` one says `Tentative`, then becomes `Preferred`. The `PersistentStore` one says `Invalid`, which is normal for the saved copy. Then `Test-Connection 10.20.10.10 -Count 2 -Quiet` gives `True`. |
| **If it fails** | An error saying the address or object already exists means it is already set. Check with `Get-NetIPAddress -InterfaceAlias "VMware Network Adapter VMnet2"`. |
| **Undo** | `Remove-NetIPAddress -InterfaceAlias "VMware Network Adapter VMnet2" -IPAddress 10.20.10.1` |
| **Safe to re-run** | No, it errors if the address exists. Check first. |

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
from the host with `vmrun`, so nothing was typed inside the VM except where marked
**BY HAND**.

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

#### 2.10.2 **BY HAND**: bypass the Windows 11 hardware check

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

**BY HAND**, typed **inside an interactive SSH session on SIEM-01**, not piped from PowerShell:

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

Then the helper script and its single sudo rule, both **BY HAND**, on SIEM-01:

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

### 2.11 Before the golden snapshot: Sysmon `lsass.exe` rule and audit settings (2026-11-03)

Decided 2026-09-29 (DECISIONS, items 18 and 20). Run by the student. The VM was started from the host with
`vmrun -T ws start` on the `$vmx` above; every other command was typed **BY HAND** in an Administrator
PowerShell inside WIN-EP-01, except the copy, which ran on the host.

| Step | Command | Correct result, as seen on 2026-11-03 |
|---|---|---|
| Back up the running config (guest) | `Copy-Item C:\telos\sysmonconfig.xml C:\telos\sysmonconfig.xml.telos-pre-item18` | No output. The backup's SHA256 is the old `055FEBC6...7162` |
| Copy the new config (host) | `& $vmrun -T ws -gu eli -gp $pw CopyFileFromHostToGuest $vmx "E:\Claude general\lab\configs\sysmonconfig.xml" "C:\telos\sysmonconfig.xml"` | No output |
| Check the copy (guest) | `Get-FileHash C:\telos\sysmonconfig.xml` | `02C43AC8...B3AD` |
| Load it (guest) | `C:\telos\Sysmon64.exe -c C:\telos\sysmonconfig.xml` | `Configuration file validated.` then `Configuration updated.` |
| Prove it (guest) | `C:\telos\Sysmon64.exe -c` | `Config hash: SHA256=02C43AC8...B3AD`; `ProcessAccess onmatch: include`, `TargetImage filter: is value: 'C:\Windows\system32\lsass.exe'` |
| Read the audit state (guest) | `auditpol /get /subcategory:"Process Creation","Credential Validation"` | Before: both `No Auditing`. After: `Success`, and `Success and Failure` |
| Process creation (guest) | `auditpol /set /subcategory:"Process Creation" /success:enable` | `The command was successfully executed.` |
| Credential validation (guest) | `auditpol /set /subcategory:"Credential Validation" /success:enable /failure:enable` | `The command was successfully executed.` |
| Command lines in 4688 (guest) | `reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f` | `The operation completed successfully.` Before, `reg query` gave `ERROR: The system was unable to find the specified registry key or value.` |
| Proof, 4688 (guest) | `Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4688} -MaxEvents 1 \| Format-List TimeCreated, Message` | A 4688 with a `Process Command Line:` line |
| Proof, Sysmon 10 (guest) | `Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -FilterXPath "*[System[EventID=10]]" -MaxEvents 2 \| Format-List TimeCreated, Message` | `svchost.exe` to `lsass.exe`, `GrantedAccess: 0x1000`, background activity |

**Undo.** Sysmon: `C:\telos\Sysmon64.exe -c C:\telos\sysmonconfig.xml.telos-pre-item18`. Audit: the same two
`auditpol` lines with `disable`, then `reg delete` of the same value with `/f`. All are safe to re-run.

**Archive check, the same day (Part 3.7 method).** SIEM-01 had to be started first (`vmrun -T ws start
"F:\TeLoS Homelab\SIEM-01\SIEM-01.vmx" nogui`). Pattern files with LF only, copied with `scp`, counted with
`telos-archive count <file> 2026-11-03`: 4688 `117`, Sysmon 10 `121`, 4776 `0`. The guest had no 4776 even after a
screen unlock with the password; one host call, `& $vmrun -T ws -gu eli -gp $pw listProcessesInGuest $vmx`, wrote
two, and the count became `2`. `show <file> 1 <date>` printed one archived event 10 with `lsass.exe`. The CIS values (Process Creation: Success; Credential Validation: Success and Failure) are general
knowledge, to be matched against the benchmark text when the change scripts are written.

### 2.12 The C5 RDP test and the NLA on test (2026-11-11 to 2026-11-12)

Purpose: prove that a local-account RDP sign-in from the host fires rule 92653 (DECISIONS 2026-11-11). Result and
findings: OPEN-QUESTIONS 37. `$vmrun`, `$win` and `$siem` are the `vmrun.exe` path and the two `.vmx` files on F:.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Revert (2026-11-11) | host, Claude | `& $vmrun -T ws revertToSnapshot $win pre-lsass-trial-2026-11-03` | Exit 0. The 3.3 GB trial delta `000004.vmdk` gone; new `000006.vmdk`, 10 MB |
| Start both (2026-11-11) | host, Claude | `& $vmrun -T ws start $siem nogui`, then `& $vmrun -T ws start $win` | `Total running VMs: 2`. Both VMs were later suspended, not shut down |
| Restart with a correct clock (2026-11-12) | host, **student** (the same command was refused by the app for Claude) | revert `$win` again; `start $siem nogui` (resumes), wait for `checkToolsState` = `running`, `stop $siem soft`, `start $siem nogui`; `start $win` | All exit 0, `vmss left: 0`. SIEM-01 `date -u` 13:22:35Z against host 13:22:36Z |
| Read RDP state (guest) | guest, student | `Get-ItemProperty` of `fDenyTSConnections` and `RDP-Tcp\UserAuthentication`; `Test-Path` of the policy key; `Get-Service TermService`; `Get-NetFirewallRule -DisplayGroup 'Remote Desktop'`; `Get-NetConnectionProfile` | `1`; `1`; `True`, but `Get-ItemProperty` on it gave no output (empty key); `Stopped`; 3 rules, all `False`; `NAT` and `LAB` both `Public` |
| Turn RDP on, NLA off (guest) | guest, student | `Set-ItemProperty ... fDenyTSConnections -Value 0`; `Set-ItemProperty ... UserAuthentication -Value 0`; `Get-NetFirewallRule -DisplayName 'Remote Desktop - User Mode (TCP-In)' \| Set-NetFirewallRule -Enabled True -RemoteAddress 10.20.10.1`; `Start-Service TermService` | No output. Checks: `0`, `0`, `RemoteAddress 10.20.10.1`, listening on `0.0.0.0:3389` and `[::]:3389` |
| Port test | host, Claude | `Test-NetConnection 10.20.10.20 -Port 3389` | `TcpTestSucceeded : True`, source `10.20.10.1` |
| Sign-in | host, student | `mstsc /v:10.20.10.20`, as `.\eli` | Twice with `eli` signed in at the console (type 7), once after signing out (type 10) |
| Guest events | guest, student | `Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625; StartTime=[datetime]'2026-11-12T13:42:00Z'}`, fields read from the event XML | See OPEN-QUESTIONS 37 |
| Archive | host, Claude | `ssh ... "mkdir -p /home/eli/c5"`; `scp` of the pattern file `"ipAddress":"10.20.10.1"` (LF, 0 CR) to `/home/eli/c5/p-hostip.txt`; `telos-archive show /home/eli/c5/p-hostip.txt 60` | 15 lines; rule ID read from each line's `rule.id`. 92653 on both type 10 lines |

**The NLA on test (2026-11-12, all times UTC).** Same VM state as above. Purpose: OPEN-QUESTIONS 37, point 3.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Client file | host, Claude | wrote `lab/configs/c5-client-no-nla.rdp`: `full address:s:10.20.10.20`, `username:s:.\eli`, `enablecredsspsupport:i:0`, `prompt for credentials:i:0` | A client that does not check the password before the session |
| Run A: NLA off, no-check client | host, student | `mstsc "E:\Claude general\lab\configs\c5-client-no-nla.rdp"` | Clipboard box, then two prompts answered yes; the Windows sign-in screen inside the session; desktop. 14:31:29Z |
| Turn NLA on | guest, student, Terminal (Admin) | `Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name UserAuthentication -Value 1`, then read back | No output, then `1`. TermService **not** restarted. Console signed out |
| Run B: NLA on, default client | host, student | `mstsc /v:10.20.10.20`, as `.\eli` | Signed in and out. 15:10:20Z to 15:10:24Z |
| Run C: NLA on, no-check client | host, student | `mstsc "E:\Claude general\lab\configs\c5-client-no-nla.rdp"` | Refused: "The remote computer requires Network Level Authentication, which your computer does not support." `Error code: 0xb09`, `Extended error code: 0x0`, 18:29:42 |
| Clocks | host, Claude | `(Get-Date).ToUniversalTime()`; `ssh ... "date -u"` | Host 18:30:38, SIEM-01 18:30:37 |
| Archive | host, Claude | `telos-archive show /home/eli/c5/p-hostip.txt 200`; `telos-archive count /home/eli/c5/p-hostip.txt`; `telos-archive tail 2000`, kept only `agent.name = WIN-EP-01` (filtered on the host) | `count` 23, so `show` returned every match. **`show` returns the first N matches, not the last.** Events per run: OPEN-QUESTIONS 37. Run C: one Sysmon event 3 only |

**The unattended sign-in test (2026-11-12, times UTC).** Same VM state (NLA on). Purpose: OPEN-QUESTIONS 37, point 3,
the sign-in with no person at the keyboard.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| VMs running | host, Claude | `& $vmrun -T ws list` | `Total running VMs: 2` |
| Store the password | host, **student** (types the password) | `cmdkey /generic:TERMSRV/10.20.10.20 /user:WIN-EP-01\eli /pass` | Asked for the password, then `CMDKEY: Credential added successfully.` |
| Check it | host, student | `cmdkey /list:TERMSRV/10.20.10.20` | `Target: TERMSRV/10.20.10.20`, `Type: Generic`, `User: WIN-EP-01\eli` |
| Two tries | host, student, console signed out first | `mstsc /v:10.20.10.20`, nothing clicked; signed out inside after each | **No box at all on either try** (no password box, no certificate box). 19:03:23Z and 19:05:27Z |
| Clocks | host, Claude | `(Get-Date).ToUniversalTime()`; `ssh ... "date -u"` | Both 19:16:35 |
| Archive | host, Claude | `telos-archive count` and `show` with `/home/eli/c5/p-hostip.txt` | Count 23 to 33. Each try: two type 3 NTLM (92657), one 4648, two type 10 (92653), the same as run B |

**The session checks (2026-11-12, times UTC).** Purpose: OPEN-QUESTIONS 37, ending the session. Does a fresh boot,
or a `vmrun` guest call, leave an `eli` session that turns the C5 sign-in into type 7? Claude ran every step except
the `vmrun` guest call, which uses the guest password.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Restart 1 | host, Claude | `& $vmrun -T ws reset $win soft` | Exit 0 at 19:30:06. Tools state never seen as stopped (5-second checks). Proof from the archive: no WIN-EP-01 lines from 19:30:08 to 19:31:12; Sysmon 1 for `vmtoolsd.exe`, `Sysmon64.exe`, `wazuh-agent.exe` at 19:30:23; after it only type 5 (service) logons by SYSTEM, no `eli` logon |
| Check (a) | host, Claude | `Start-Process mstsc -ArgumentList '/v:10.20.10.20'` (stored password), then `Stop-Process` | 19:35:29 to 19:35:30: two type 3 NTLM (92657), one 4648, **two type 10 (92653)** |
| Restart 2 | host, Claude | `& $vmrun -T ws reset $win soft` | Exit 0 at 19:35:56; Sysmon 1 for `wazuh-agent.exe` at 19:36:16 |
| `vmrun` guest call | host, **student** (uses the password file) | `$pw = Get-Content "$env:USERPROFILE\.telos\WIN-EP-01.pw"; & $vmrun -T ws -gu eli -gp $pw listProcessesInGuest $win \| Select-String -Pattern 'explorer.exe','Process list'` | `Process list: 95`, no `explorer.exe`. Archive: two 4624 **type 4** by `vmtoolsd.exe` (rule **67022**, level 3, "Non network or service local logon."), two 4648 by `vmtoolsd.exe`, 19:42:53 to 19:42:54 |
| Check (b) | host, Claude | `Start-Process mstsc ...`, then `Stop-Process` | 19:43:34 to 19:43:35: the same as check (a), **two type 10 (92653)** |
| Boot events | host, Claude | `telos-archive tail 6000`, WIN-EP-01 lines with event time 19:30:09 to 19:35:00 | 457 lines; event 6005: 0; Wininit: 0; System channel: 6 (OPEN-QUESTIONS 28) |

**Undo.** A revert to `pre-lsass-trial-2026-11-03` removes every guest change above, including NLA on. On SIEM-01:
`rm -r /home/eli/c5`. On the host: `cmdkey /delete:TERMSRV/10.20.10.20` removes the stored password. All steps are
safe to re-run.

---

### 2.13 LSASS trial part 2, Defender off (2026-11-13, times UTC)

Purpose: OPEN-QUESTIONS 35, which `GrantedAccess` each LSASS test asks for and whether rule 92900 fires, in Config S
(DECISIONS 2026-11-03). Two runs: `lsass-trial-on-2` (LSA Protection on, C3's "after") and `lsass-trial-off-1` (LSA
Protection off, the decided baseline, C3's "before"). Claude ran the host steps; the student ran the guest steps in an
Administrator PowerShell in the VM window. Trial part 1's commands were taken from chat 27d2595d's transcript.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Find state | host, Claude | `vmrun -T ws list`; `Get-ChildItem ... -Filter *.vmss` | `Total running VMs: 0`; SIEM-01 **suspended** (`SIEM-01-2be98078.vmss`, 04:49 local) |
| Power-cycle SIEM-01 | host, Claude | `vmrun start $siem nogui` (resume), wait for Tools, `vmrun stop $siem soft`, `vmrun start $siem nogui` | All exit 0; SIEM-01 07:55:32 = host 07:55:32; no `.vmss` left |
| Revert and start | host, Claude | `vmrun revertToSnapshot $win pre-lsass-trial-2026-11-03`; `vmrun start $win gui`; `vmrun disconnectNamedDevice $win ethernet0` | All exit 0. Guest: `NAT Disconnected`, `LAB Up` |
| Agent check | host, Claude | `telos-archive tail 2000`, WIN-EP-01 lines | 383 lines, newest 07:55:42 |
| Starting state | guest, student | `(Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa).RunAsPPL`; `Get-WinEvent` Wininit 12, newest | `2`; event 12 at 07:54:40, "protected process with level: 4" |
| Defender off | guest, student | `Set-MpPreference -DisableRealtimeMonitoring $true -DisableBehaviorMonitoring $true -DisableScriptScanning $true -DisableIOAVProtection $true`; `Get-MpComputerStatus \| Select-Object RealTimeProtectionEnabled, BehaviorMonitorEnabled, IoavProtectionEnabled, IsTamperProtected` | `False False False False` |
| Run `on-2` | guest, student | `Set-ExecutionPolicy -Scope Process Bypass -Force; Import-Module C:\AtomicRedTeam\invoke-atomicredteam\Invoke-AtomicRedTeam.psd1 -Force`, then `C:\telos\telos-fence.exe START lsass-trial-on-2; Invoke-AtomicTest T1003.001 -TestNumbers 1,2,13 -PathToAtomicsFolder C:\AtomicRedTeam\atomics; Invoke-AtomicTest ... -Cleanup; C:\telos\telos-fence.exe END lsass-trial-on-2` | Fences 07:58:35.60Z to 07:58:41.82Z. ProcDump `Error opening lsass.exe (896): Access is denied.`; comsvcs exit 0; rdrleakdiag "Minidump file ... can be found" |
| LSA off | guest, student | `Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\Lsa -Name RunAsPPL -Value 0; Restart-Computer` | Boot 08:25:52. Then `RunAsPPL 0`, **`RunAsPPLBoot 0`** (was 2; changed by itself); newest event 12 still 07:54:40, so none at this boot |
| Defender off again | guest, student | the same `Set-MpPreference` line, then `Get-MpComputerStatus` | **`True True True False`**: no effect. `Get-MpPreference` showed all four `Disable...` values `True`. After `Start-Sleep 20`, the same `Set-MpPreference`, `Start-Sleep 5`: `False False False False` |
| Run `off-1` | guest, student | the same two lines with `lsass-trial-off-1` | Fences 08:28:10.16Z to 08:28:13.81Z. ProcDump "Dump 1 complete: 79 MB written in 0.4 seconds"; comsvcs exit 0; rdrleakdiag "Minidump file ... can be found" |
| Archive | host, Claude | `telos-archive tail 3000` to `8000`, WIN-EP-01 lines filtered by event time on the host | Results in OPEN-QUESTIONS 35, "Trial part 2". The first read listed only Sysmon 10 and 1 and missed Sysmon 8 (rule 92403); corrected the same day |
| Defender check | guest, student | `Get-MpComputerStatus \| Select-Object ...` | `False False False False` |
| Test 9 prereqs | guest, student | `Invoke-AtomicTest T1003.001 -TestNumbers 9 -CheckPrereqs -PathToAtomicsFolder C:\AtomicRedTeam\atomics` | `Prerequisites met: T1003.001-9 Create Mini Dump of LSASS.exe using ProcDump` |
| Run `off-t9` | guest, student | `C:\telos\telos-fence.exe START lsass-trial-off-t9; Invoke-AtomicTest T1003.001 -TestNumbers 9 ...; ... -Cleanup; C:\telos\telos-fence.exe END lsass-trial-off-t9` | Fences 08:32:23.69Z to 08:32:24.26Z. `Multiple processes match the specified name.`, exit code -2. Archive: `procdump.exe -accepteula -mm lsass.exe ...` started, no access to `lsass.exe` |
| Count `lsass.exe` | guest, student | `Get-Process lsass \| Select-Object Id, StartTime, Path` | Two: PID 904 (08:25:56, boot) and PID 1840 (08:29:12). Archive: 1840 started by `lsass.exe` 904, rule 61625 |

**Undo.** A revert to `pre-lsass-trial-2026-11-03` removes every guest change (LSA off, Defender off, the console
session); `vmrun connectNamedDevice $win ethernet0` reconnects NAT. The tests' dumps were deleted by `-Cleanup`. All
steps are safe to re-run.

---

### 2.14 The C1 trial, WDigest (2026-11-13, times UTC)

Purpose: does C1 (`UseLogonCredential = 0`) change what a console sign-in writes, and rule 60118? Same guest state as
2.13 (LSA Protection off, Defender off). The student did every guest step and sign-in; Claude read the archive.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Rule 60118 today | host, Claude | archive, WIN-EP-01 since 07:54 | Fired on each console sign-in: two 4624 type 2 per sign-in (07:57:09, 08:26:04), level 3, "Windows Workstation Logon Success", T1078 |
| Read the value | guest, student | `Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest' -ErrorAction SilentlyContinue \| Select-Object UseLogonCredential` | Empty: the value did not exist |
| First try | guest, student | `New-ItemProperty ... -Name UseLogonCredential -PropertyType DWord -Value 1 -Force`, then `Set-ItemProperty ... -Value 0` | `1`, then `0`, 8 seconds apart (Sysmon 13 at 08:42:04 and 08:42:12) with **no sign-in between**: nothing measured |
| `wdigest-on` | guest, student | `Set-ItemProperty ... -Value 1`; sign out; sign in | Value set 08:43:49.754; sign-in 08:44:44.207 |
| `wdigest-off` (C1) | guest, student | `Set-ItemProperty ... -Value 0` in a new Terminal; sign out; sign in | Value set 08:45:01.985; sign-in 08:46:23.693 |
| Compare | host, Claude | archive, 30 seconds after each sign-in, counted by event ID and channel; every field of the first 4624 | Results in OPEN-QUESTIONS 1, "The C1 trial" |

**Undo.** `Remove-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest' -Name
UseLogonCredential`, or a revert to `pre-lsass-trial-2026-11-03`. Safe to re-run.

---

### 2.15 Export the Wazuh rules from SIEM-01 (2026-11-13)

Purpose: the rule export DECISIONS 2026-10-01 asks for, read by the rule-to-key index (`src/telos/index.py`).

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Power-cycle SIEM-01 | host, Claude | `vmrun start` (resume), `vmrun stop soft`, `vmrun start` | It had been **suspended again** (`.vmss` 17:13 local). All exit 0; SIEM-01 11:30:03 against host 11:30:04 |
| Read access | host, Claude | `ssh ... "ls -ld /var/ossec ..."` | `drwxr-x--- 20 root wazuh ... /var/ossec`; `ls: cannot access '/var/ossec/ruleset': Permission denied`. So `sudo` is needed. (One slip: `\$(...)` inside the command was run by PowerShell on the host; it failed with "Could not find a part of the path 'E:\dev\null'" and changed nothing.) |
| Pack the rules | host terminal, **student** (types the SIEM-01 password) | `ssh -t -i "$env:USERPROFILE\.telos\siem01_ed25519" eli@10.20.10.10 "sudo tar czf /home/eli/wazuh-rules-4.14.7.tar.gz -C /var/ossec ruleset/rules etc/rules && sudo chown eli:eli /home/eli/wazuh-rules-4.14.7.tar.gz && ls -l /home/eli/wazuh-rules-4.14.7.tar.gz && sha256sum /home/eli/wazuh-rules-4.14.7.tar.gz"` | `-rw-r--r-- 1 eli eli 205080 Nov 13 11:31 ...`; `6fca773be3ffb59ee5745f92ee75e4a94b8f321093aab6bedc35bac3e09267ae` |
| Copy and unpack | host, Claude | `scp ... eli@10.20.10.10:/home/eli/wazuh-rules-4.14.7.tar.gz "E:\Claude general\data\rules\wazuh-rules-4.14.7.tar.gz"`; `Get-FileHash`; `tar -xzf ... -C "E:\Claude general\data\rules\wazuh-4.14.7"` | Same SHA256; 169 files (168 in `ruleset/rules`, 1 in `etc/rules`). The first `scp` failed: a target ending in `\"` lost its closing quote in PowerShell 5.1; the full file name worked |
| Folder hash | host, Claude | SHA256 over the sorted lines "file SHA256, two spaces, relative path" | `a3f9749e...2939` (DECISIONS, pinned table) |

**Undo.** On SIEM-01: `rm /home/eli/wazuh-rules-4.14.7.tar.gz`. On the host: delete `data\rules\`. Safe to re-run.

---

### 2.16 The golden snapshot `golden-base` (2026-11-13 to 2026-11-16, times UTC)

Purpose: runbook Phase 5, the state every capture run reverts to (DECISIONS 2026-11-16).

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Write the baseline | host, Claude | `lab/scripts/baseline-golden.ps1` (sets the decided baseline, prints a 20-row check) | All 5 guest scripts parse with 0 errors |
| VMs (2026-11-16) | host, Claude | `vmrun list`; `.vmss` check | Both off, no `.vmss` |
| Start, clean revert | host, Claude | `vmrun start $siem nogui`; `vmrun revertToSnapshot $win pre-lsass-trial-2026-11-03`; `vmrun start $win gui`; `checkToolsState`; `disconnectNamedDevice $win ethernet0` | All exit 0; `vmrun start ... gui` hung in the command (the VM did start) and the command was stopped; the rest was run separately. SIEM-01 06:52:27 against host 06:52:28 |
| Copy scripts in | host, **student** (guest password) | `vmrun -gu eli -gp $pw CopyFileFromHostToGuest` for the 5 scripts into `C:\telos\` | 5 lines `exit 0` |
| Set the baseline | guest, student, Terminal (Admin) | `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -WDigest On` | **19 of 20**: every row True except "Wininit event 12 since this boot" (`yes`, LSA Protection still active until the restart). All three pinned hashes matched |
| Restart and verify | guest, student | `Restart-Computer`; the same script with `-Verify -WDigest On` | Reported "done"; **output not seen** |
| Sign out, shut down, NAT | guest and VMware settings, student | Sign out; Shut down from the sign-in screen; VM Settings, NAT adapter: untick Connected and Connect at power on | `.vmx`: `ethernet0.startConnected = "FALSE"`; WIN-EP-01 off, no `.vmss` |
| Snapshot | host, Claude | `vmrun -T ws snapshot $win golden-base`; `vmrun -T ws listSnapshots $win` | Exit 0 at 06:59:45; `Total snapshots: 6`, `golden-base` last |

**Test boot of `golden-base` (2026-11-16):**

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Revert and start | host, Claude | `vmrun revertToSnapshot $win golden-base`; ``Start-Process -FilePath $vmrun -ArgumentList @('-T','ws','start',"`"$win`"",'gui') -WindowStyle Hidden`` (not waited on, because `start ... gui` hung inside a command before). **Corrected 2026-11-26 from the chat:** this row had lost the escaped quotes around `$win`, which the space in the path needs; `checkToolsState` | Revert exit 0; start 07:02:06; Tools running 07:02:22 |
| Check | guest, student, Terminal (Admin) | `baseline-golden.ps1 -Verify -WDigest On`; `query user`; `Get-NetAdapter \| Select-Object Name, Status` | **`checks passed: 20 of 20`** (Wininit event 12 since boot: `none`); `eli console 1 Active ... 7:08 AM` only; `NAT Disconnected`, `LAB Up` |
| Archive | host, Claude | `telos-archive tail 6000`, WIN-EP-01 lines since 07:02:06, 4624 for `eli` | 694 lines from 07:02:22; the only `eli` logons are two type 2 at 07:08:06 (rule 60118), the student's sign-in. Nothing signed `eli` in at boot |

**Undo.** `vmrun -T ws deleteSnapshot $win golden-base`. Do not take a second snapshot with the same name.

---

### 2.17 The first real harness run, `test-pre-1` (2026-11-16, times UTC)

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Capture | host, **student** (the harness passes the guest password) | `cd "E:\Claude general"; .\.venv\Scripts\python.exe src\capture.py --run-id test-pre-1 --phase pre` | Every lab step worked: `after-boot: config-S exit 0`; tests 1, 2, 13 and cleanup each exit 0 in about 5 s; `guest calls: 7`; export of 2026-11-16, 6,775 lines, hash checked. **`valid: False`**: `window not readable: no START fence for run 'test-pre-1'` |
| Find the cause | host, student (Claude's command checker was failing) | `python -c` reading `data\runs\test-pre-1\archive-2026-11-16.json.gz` for `telos-fence` | Command line `"C:\telos\telos-fence.exe" "START" "test-pre-1"`: **vmrun quotes every argument**. START 07:32:45.26, END 07:35:45.30 (180 s). Each fence also appears as a 4688, and a `conhost.exe 0xffffffff -ForceV1` starts with each guest call |
| Fix | host, Claude | `archive.py` drops quotes before matching; test with the real line, failing first with the same error | 131 passed |
| Recount | host, Claude | `harness.recount()` (tests failing first; 133 passed); `.\.venv\Scripts\python.exe src\capture.py --run-id test-pre-1 --recount` | `valid True`; window 07:32:45.2599503Z to 07:35:45.2974529Z, 284 events, 19 keys, 0 broken lines; Sysmon-8 2, Sysmon-10 75; fired 92403 ×2, 61625 ×1, 92027 ×4, 92032 ×1, 92052 ×2 |

**Undo.** Delete `data\runs\test-pre-1\` (not in git). A recount can be run again; it adds a note each time.

---

### 2.18 `golden-base-v2`: Phases A to D (from 2026-11-26, times UTC)

Purpose: `docs/GOLDEN-BASE-V2.md` (DECISIONS 2026-11-26). One row per step, added as it happens. Evidence for the
first five rows: `data/summaries/host-hypervisor-check-2026-11-26.txt`.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Pre-flight before A1 | host, Claude (read only) | `vmrun -T ws list`; `vmrun -T ws listSnapshots $win`; VMnet2 IPv4; `HypervisorPresent`; `git log -1 --oneline`; `git status --short` | `Total running VMs: 0`; 6 snapshots, `golden-base` once; `10.20.10.1`; **`True`**; `bfdad21`; only the 4 known untracked files. **Phase A not started** |
| Why the hypervisor is on | host, Claude (read only) | System log: oldest event, `Kernel-General` 12, `Hyper-V-Hypervisor` events; `HKLM:\SYSTEM\Setup\Source OS*`; `CurrentVersion`; `Get-HotFix`; `Win32_DeviceGuard`; `vmware.exe` version; `Get-Service AVP*, WinDefend` | Log kept from 2026-11-23 12:52; 7 host starts, hypervisor event 1 at each; `Source OS (Updated on 11/23/2026 13:11:49)`: old build 26200.9457, now 26200.9974, installed 2026-11-23 12:59; 4 updates, all 2026-11-23 or 24; VBS 2, no services; `17.5.1 build-23298084`; `AVP21.27` Running, `WinDefend` Stopped |
| The spike's state | host, Claude (read only) | the `Monitor Mode` line in each `vmware*.log` of both VMs | All 8 say `CPL0`: WIN-EP-01 at 11:32:59, 11:41:35, 11:54:10 and 12:06:44 on 2026-11-16; SIEM-01 at 06:42:14 on 2026-11-16 (one power-on until 13:22:41) and three on 2026-11-13 |
| Keep the logs | host, Claude | `Copy-Item` of the 8 logs into `data\runs\host-vmware-logs-2026-11-16\` (gitignored); `Get-FileHash` | 8 hashes |
| `ULM` check | host, Claude | ``Start-Process -FilePath $vmrun -ArgumentList @('-T','ws','start',"`"$win`"",'nogui') -WindowStyle Hidden``; wait for `Monitor Mode` in the new `vmware.log`; `vmrun -T ws stop $win hard`; `vmrun -T ws list`; copy that log | Start 07:19:51; **`Monitor Mode: ULM`** at 07:19:52; `stop exit 0`; `Total running VMs: 0`; copy `WIN-EP-01-ULM-check-2026-11-26.log` |
| The fix | host, **student**, Terminal (Admin) | `bcdedit /enum '{current}'`; `bcdedit /set hypervisorlaunchtype off` (Part 1.1); host restart | Outputs not reported. Host started again at 10:48:32 |
| After the restart | host, Claude (read only) | `HypervisorPresent`; `Win32_DeviceGuard`; `Hyper-V-Hypervisor` events since the start; `vmrun -T ws list`; `listSnapshots`; VMnet2 IPv4; `git log -1`, `git status --short` | **`False`**; VBS **0**; none; `Total running VMs: 0`; `golden-base` once; `10.20.10.1`; `a8c1e89`, only the 4 known untracked files |
| Start SIEM-01 | host, Claude | `& $vmrun -T ws start $siem nogui`; `checkToolsState` every 5 s; `Monitor Mode` in the new `vmware.log` | Exit 0 at 10:52:23; **`Monitor Mode: CPL0`** (10:52:24); Tools `installed` for over 3 minutes |
| SIEM-01 health | host, Claude (read only) | `Test-NetConnection 10.20.10.10 -Port 22`; `ssh -i $key -o BatchMode=yes eli@10.20.10.10 "uptime; systemctl is-system-running; systemctl is-active open-vm-tools wazuh-manager wazuh-indexer wazuh-dashboard"`; later `date -u` and `journalctl -u open-vm-tools -b` | `True`; up 3 min, `running`, 4 × `active` (10:56:17). Tools `running` at 10:58:16: `vmware.log` showed Tools connected at 10:52:35 with heartbeat "never received" (on 2026-11-16 it came at once). Clock 10:58:18 against host 10:58:17. Tools log: one start line, no errors |
| A1 | host, Claude | `revertToSnapshot $win golden-base`; ``Start-Process -FilePath $vmrun -ArgumentList @('-T','ws','start',"`"$win`"",'gui') -WindowStyle Hidden``; `checkToolsState` every 5 s; `Monitor Mode`; `vmrun list` | Revert exit 0; start 10:57:23; Tools `running` 10:57:44; **`Monitor Mode: CPL0`** (10:57:29); 2 VMs running |
| A3, host side | host, Claude (read only) | `Get-FileHash "$repo\lab\scripts\*.ps1" -Algorithm SHA256` | The 8 hashes below |
| A2 | host, **student** (guest password) | the A2 loop, `CopyFileFromHostToGuest` for the 8 scripts | Exit lines not pasted. A3 proves the copies arrived |
| A3, guest side | guest, student (read only) | `Get-FileHash C:\telos\*.ps1 -Algorithm SHA256 \| Format-Table Hash, Path -AutoSize` | **8 of 8 match** the hashes below, all 64 characters. `C:\telos` holds 26 `.ps1` files; the other 18 are older build scripts (for example `art-install.ps1`) |
| A4 and K2, typed on the host by mistake | host, student, Terminal (Admin) | the A4 line; `$s = 'C:\telos\change-K2-cmdline-off.ps1'` and its three lines | `The argument 'C:\telos\baseline-golden.ps1' to the -File parameter does not exist.`; the same for K2 three times, exit code `-196608`. **Nothing ran:** `Test-Path C:\telos` on the host gives `False` (Claude). Had the baseline run there, it would have turned WDigest caching on, LSA Protection off, and Remote Desktop on with NLA off, on the host |
| Boot setting | host, student, Terminal (Admin) | `bcdedit /enum` | `{current}`: `hypervisorlaunchtype Off`. Not stated whether read before or after the fix |
| The guard (student: "Yes, add the guard") | host, Claude | the guard line in the 8 scripts; a test in `tests/test_catalog.py`; `.gitattributes`: `lab/scripts/*.ps1 text eol=lf` | DECISIONS 2026-11-26 |
| Its checks | host, Claude (read only) | the guest's name: `telos-archive tail 300` over SSH, `computer` field counted on the host; PowerShell's parser on the 8 scripts; `git ls-files --eol`; `pytest tests -q`; the new check on the `git show HEAD` copies; C1 `-Verify` on the host | `WIN-EP-01` (277 of 300 lines, no other name); 8 × 0 errors; 8 × `i/lf w/lf attr/text eol=lf`; **156 passed**; 8 × "no guard, so the test fails"; the guard's message and **exit 3** |
| A2 again | host, **student** (guest password) | the A2 loop, with the 8 scripts after the guard | 8 lines, each ending `exit 0` |
| A3 again, guest side | guest, student (read only) | `hostname`; `Get-FileHash C:\telos\*.ps1 -Algorithm SHA256 \| Format-Table Hash, Path -AutoSize` | `WIN-EP-01`; 26 `.ps1` files, as before |
| A3 again, compared | host, Claude (read only) | `Get-FileHash "$repo\lab\scripts\*.ps1" -Algorithm SHA256`, compared by a script with the 8 pasted guest hashes (exact, case-sensitive); `git log -1 --oneline`; `git status --short`; `vmrun -T ws list` | **8 × `match`** with the hashes after the guard (12:52:14); `819aa85`, only the 4 known untracked files; 2 VMs running |
| A4 | guest, student, Terminal (Admin) | `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -WDigest On` | **`checks passed: 25 of 25`**, every row `True`. The new rows: `NLA off by policy, Policies UserAuthentication` `0`; `Audit Logon` `Success and Failure`. No restart needed: `Wininit event 12 since this boot` `none`, `TermService` `Running` |
| A5, K2 | guest, student | `$s = 'C:\telos\change-K2-cmdline-off.ps1'`, then `-Verify`, apply, `-Verify` | `before: 1`, `apply:  0`, `after:  0`. **In effect without a restart:** the check found a new `cmd.exe` 4688 event with no command line |
| A5, K1 | guest, student | the same three lines with `change-K1-audit-logon-off.ps1` | `before: 1`, `apply:  0`, `after:  0` |
| A5, K3 | guest, student | the same three lines with `change-K3-audit-process-creation-off.ps1` | `before: 1`, `apply:  0`, `after:  0` |
| A6 step 1 | host, student | `mstsc "$repo\lab\configs\c5-client-no-nla.rdp"` | "Connected remotely" (student); sign-in screen or desktop not stated |
| A6 step 2 | guest, student | the same three lines with `change-C5-rdp-nla.ps1` | `before: 1`, `apply:  0`, `after:  0` (this check reads the registry value only) |
| Host Remote Desktop client log | host, Claude (read only) | `Get-WinEvent` on `Microsoft-Windows-TerminalServices-RDPClient/Operational` since 10:57, event 1029 left out (it holds a hash of the user name) | 14 events, one connection: attempt 13:00:40; first try ended `Reason= 263` at 13:00:45 (meaning unverified); `has connected to the server` 13:00:45; disconnected `Reason= 2` at 13:01:23. **No attempt after that** (read 13:03:28), so A6 step 3 had not run |
| A6 step 3 | host, student | the same `mstsc` line | **Refused:** "The remote computer requires Network Level Authentication, which your computer does not support.", `Error code: 0xb09`, `Extended error code: 0x0`, `Timestamp (UTC): 11/26/26 01:08:15 PM`. After C5, with no restart: the policy value works at once |
| A7 | host, Claude | `& $vmrun -T ws revertToSnapshot $win golden-base`; `vmrun -T ws list`; `listSnapshots` | Exit 0 at 13:16:05; `Total running VMs: 1` (SIEM-01); 6 snapshots, `golden-base` once. **Phase A passed** |
| B1 | host, Claude | `HypervisorPresent`; `revertToSnapshot $win golden-base`; ``Start-Process -FilePath $vmrun -ArgumentList @('-T','ws','start',"`"$win`"",'gui') -WindowStyle Hidden``; `checkToolsState` every 5 s; `Monitor Mode`; `vmrun list` | `False`; revert exit 0; start 13:19:16; Tools `running` 13:19:38; **`Monitor Mode: CPL0`** (13:19:22); 2 VMs running |
| B2 | host, **student** (guest password) | the A2 loop | 8 lines, each ending `exit 0` |
| B3 | guest, student (read only); compared on the host by Claude | `hostname`; `Get-FileHash C:\telos\*.ps1 -Algorithm SHA256 \| Format-Table Hash, Path -AutoSize`; the same script compare as in A3 | `WIN-EP-01`; 26 files; **8 × `match`** (13:24:34) |
| B4 | guest, student, Terminal (Admin) | `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -WDigest On` | **`checks passed: 25 of 25`**, every row `True` |
| B5 | guest, student | `Restart-Computer`; sign in; `hostname`; `powershell -NoProfile -ExecutionPolicy Bypass -File C:\telos\baseline-golden.ps1 -Verify -WDigest On` | `WIN-EP-01`; **`checks passed: 25 of 25` after a restart**, every row `True` (`Wininit event 12` `none`, `TermService` `Running`). First time this output was seen for a golden image |
| B6 | guest and VMware, student | sign out; Shut down from the sign-in screen; VM Settings, NAT adapter, untick "Connect at power on" | "done, VM is off and NAT unticked" (student) |
| B7 | host, Claude (read only) | `vmrun -T ws list`; `Test-Path 'F:\TeLoS Homelab\WIN-EP-01\*.vmss'`; the `ethernet*` lines of the `.vmx`; `listSnapshots` | `Total running VMs: 1` (SIEM-01); `False`; `ethernet0` `VMnet8` (NAT) `startConnected = "FALSE"`, `ethernet1` `VMnet2` with no `startConnected` line (connects); 6 snapshots (13:31:36) |
| B8 | host, Claude | `& $vmrun -T ws snapshot $win golden-base-v2`; UTC time; `listSnapshots` | Exit 0; **`2026-11-26T13:31:48Z`**; 7 snapshots, `golden-base-v2` last, once. **Phase B passed** |
| C1 | host, Claude | `HypervisorPresent`; `revertToSnapshot $win golden-base-v2`; the A1 `Start-Process` line; `checkToolsState` every 5 s; `Monitor Mode`; `vmrun list` | `False`; revert exit 0; **start 13:33:29**; Tools `running` 13:33:45; **`Monitor Mode: CPL0`** (13:33:31); 2 VMs running |
| C2 | guest, student (read only) | `hostname`; `baseline-golden.ps1 -Verify -WDigest On`; `query user`; `Get-NetAdapter \| Select-Object Name, Status` | `WIN-EP-01`; **`checks passed: 25 of 25`**; `eli console 1 Active ... 1:34 PM` only; `NAT Disconnected`, `LAB Up` |
| C3 | host, Claude (read only) | `ssh -i $key -o BatchMode=yes eli@10.20.10.10 "sudo -n /usr/local/sbin/telos-archive tail 6000"`, parsed on the host: WIN-EP-01 lines with event time since 13:33:29, 4624 events | Oldest line read 11:11:17, so the boot is covered; 725 lines from 13:33:45 to 13:35:36; 4624: `SYSTEM` 16, `eli` 2, both type 2 at 13:34:18 (rule 60118), the student's sign-in. **Nothing signed `eli` in at boot** |
| C4 | host, Claude | `src/telos/catalog.py`: `GOLDEN_SNAPSHOT = "golden-base-v2"`, `GOLDEN_BASE_TAKEN = "2026-11-26T13:31:48Z"`, docstring; `pytest tests -q` | **156 passed**; the catalog prints `golden-base-v2 2026-11-26T13:31:48Z`. `src/spike.py` still names `golden-base` (the spike). **Phase C passed** |
| D1, revert and start | host, Claude | the C1 commands | `False`; revert exit 0; start 13:42:49; Tools `running` 13:43:05; **`CPL0`** (13:42:50) |
| D1, scan | guest and dashboard, student | D0 (SCA on, `Restart-Service -Name WazuhSvc`); Configuration Assessment, WIN-EP-01, export of the checks table as `checks.csv` | Export saved 14:10:02. Kept as `data\runs\scans-2026-11-26\D1-baseline-checks.csv` (gitignored), SHA256 `E4F897AA88A68F1F372BBA43593B9D3C163F2FAB63CBA511986312667DAA61D3` |
| D1, read | host, Claude (read only) | a Python `csv` reader on the export: the 6 checks; all results counted | 482 checks, policy `cis_win11_enterprise`: 349 failed, 124 passed, 9 not applicable. **26177 failed, 26270 failed, 26426 failed, 26148 passed, 26222 passed, 26144 passed: all 6 as predicted** (EXPECTED-RESULTS 6). 26222's condition, not read before: `all` (key, value, value 1). 26426's: `any` |
| Scan results from the archive | host, Claude (read only) | `telos-archive tail 20000` over SSH, saved to the scratchpad; a Python reader of WIN-EP-01's `decoder.name = sca` lines (`full_log` types `summary` and `check`) | D1 scan `1070968410`: start 13:44:33, end 13:44:44 (11 s); 124 passed, 349 failed, 9 not applicable, 482: **the same as the dashboard export, and the same 6 results.** From D2 on, Claude reads the results this way; the dashboard is not needed. Unverified: that the agent sends every check on each scan (it did here) |
| D2 C1, revert and start | host, Claude | the C1 commands | `False`; revert exit 0; start 14:13:49; Tools `running` 14:14:05; `CPL0` |
| D2 C1, apply and scan | guest, student | `hostname`; `change-C1-disable-wdigest.ps1`; D0 | `WIN-EP-01`; `C1 apply: 0`; no output |
| D2 C1, read | host, Claude (read only) | the archive reader | Scan `1778313197`: 14:16:13 to 14:16:24; 125 passed, 348 failed, 9 not applicable. **26177 passed**, 26270 failed, 26426 failed, 26148 passed, 26222 passed, 26144 passed: **as predicted, 6 of 6**; one check moved. All checks sent again |
| Evidence | host, Claude | WIN-EP-01's `sca` lines of the tail into `data\runs\scans-2026-11-26\archive-sca.jsonl` (gitignored) | 972 lines (D1 and C1), SHA256 `05DB5100B04C38917B0A2B99C4E8204BC8F6AE90EE9E027EE9EAC0072623BAD5` |
| D2 C3, revert and start | host, Claude | the C1 commands | `False`; revert exit 0; start 14:17:08; Tools `running` 14:17:24; `CPL0` |
| D2 C3, apply and scan | guest, student | `hostname`; `change-C3-lsa-protection.ps1`; D0's file edit; `Restart-Computer` | "restart done" (student); the apply line's output not pasted |
| D2 C3, read | host, Claude (read only) | the archive reader; WIN-EP-01 events since 14:17 naming `RunAsPPL` or Wininit | Sysmon 13 at 14:18:28: `...\Control\Lsa\RunAsPPL` `DWORD (0x00000002)`, so C3 applied. Scan `199139473`: 14:18:48 to 14:19:01, after the restart; 124 passed, 349 failed, 9 n/a. 26177 failed, **26270 failed**, 26426 failed, 26148 passed, 26222 passed, 26144 passed: **as predicted, 6 of 6; the scan does not see C3.** Wininit 12 not found in the archive |
| Evidence | host, Claude | the same filter, plus the `RunAsPPL` line | `archive-sca.jsonl` overwritten: 1461 lines (D1, C1, C3), SHA256 `A7B9CF6644E533E9FB8F29139EA4BCF9C50A1DC85C7B7D79E7988B8829A5B30A` |
| D3, Kaspersky exclusion | host, student | Kaspersky settings, the exclusion list | "exclusion is there" (student): `E:\TeLoS-artifacts` still excluded after the 2026-11-23 reinstall |
| D3, `trial-C5-1` | host, **student** (guest password) | `.\.venv\Scripts\python.exe src\capture.py --run-id trial-C5-1 --phase post --change C5` | **`valid: True`**, no void reasons; config-S 0; the 5 stimulus steps exit 0 (`rdp-signin-30s` 30.3 s); window 14:29:24 to 14:32:24, 718 events, 0 broken lines; 524.5 s. Manifest: `snapshot` `golden-base-v2`, `golden_base` `2026-11-26T13:31:48Z`, C5 script `a511f40d...`, `change_confirmed` true, **`parameters_sha256` `9895d0cf7c5854231710f0af733e248cd62bfa7a8ca154a3c29bab11c53b14cd`** |
| D3, C5 counts | host, Claude (read only) | `counts.json`, the 4624, 4648, 4672 keys | 4624 NTLM 2, type 10 2 (as OPEN-QUESTIONS 37), type 2 3, other 20; 4648 13; 4672 27 |
| D3 C5, start without revert | host, Claude | A1's `Start-Process` line; `checkToolsState` | start 14:35:15; Tools `running` 14:35:32; `CPL0` |
| D3 C5, NLA check | host, student | `mstsc "E:\Claude general\lab\configs\c5-client-no-nla.rdp"` | **Refused**, `0xb09`, `Timestamp (UTC): 11/26/26 02:36:34 PM`: NLA still on after the run |
| D3 C5, scan and read | guest, student (D0); host, Claude (the archive reader) | D0; `telos-archive tail 20000` | Scan `1174249244`: 14:37:44 to 14:37:55; 125 passed, 348 failed. 26177 failed, 26270 failed, **26426 passed**, 26148 passed, 26222 passed, 26144 passed: **as predicted, 6 of 6**. Kept: `archive-sca-2.jsonl`, 1943 lines, SHA256 `EBC8686F10309F16E144CDACD60EA08E180DAFD8E2097BC3301F9D2C8BCD0A9C` |
| D3, `trial-K1-1` | host, **student** (guest password) | `capture.py --run-id trial-K1-1 --phase post --change K1` | **`valid: True`**, no void reasons; the 5 stimulus steps exit 0 (`rdp-signin-30s` 30.3 s); window 14:43:53 to 14:46:53, 671 events. Manifest: `golden-base-v2`, K1 script `91d7302c...`, `change_confirmed` true, `parameters_sha256` `9895d0cf...` (the same as C5) |
| D3, K1 counts | host, Claude (read only) | `counts.json`, keys 4624, 4625, 4648, 4672 | **No `Security-4624` key and no `Security-4648` key** (C5's run: 4624 in 4 keys, 4648 13); `Security-4672[]` 27, the same as C5's run |
| D3 K1, start without revert | host, Claude | A1's `Start-Process` line; `checkToolsState` | start 14:49:41; Tools `running` 14:49:57; `CPL0` |
| D3 K1, sign-in proof | guest, student (read only) | `Get-WinEvent -LogName 'Microsoft-Windows-TerminalServices-LocalSessionManager/Operational' -MaxEvents 20 \| Where-Object Id -in 21,22,25` | **Event 21 at 2:43:56 PM** (VM clock, UTC), inside the run's window 14:43:53 to 14:46:53: the trial's Remote Desktop sign-in worked while Audit Logon was off. 21 and 22 at 2:51:06 PM: the student's sign-in |
| D3 K1, scan and read | guest, student (D0); host, Claude (the archive reader, read twice: 26426 arrived 3 s after the first read) | D0; `telos-archive tail 20000` | Scan `3532105`: 14:51:32 to 14:51:44; 123 passed, 350 failed. 26177 failed, 26270 failed, 26426 failed, **26148 failed**, 26222 passed, 26144 passed: **as predicted, 6 of 6**. Kept: `archive-sca-3.jsonl`, 2430 lines, SHA256 `32024AD0F629005DE25948C009F3792E42C15361A26089A2E1EE6A30952E530A` |
| D3, `trial-K2-1` | host, **student** (guest password) | `capture.py --run-id trial-K2-1 --phase post --change K2` | **`valid: True`**, no void reasons; the 5 stimulus steps exit 0; window 14:56:49 to 14:59:49, 788 events. Manifest: `golden-base-v2`, K2 script `aeb4759a...`, **`change_confirmed` true with no restart**, `parameters_sha256` `9895d0cf...` |
| D3, K2 counts | host, Claude (read only) | `counts.json`, the 4688 keys of `trial-K2-1` and `trial-C5-1` | K2: `Security-4688[NewProcessName,ParentProcessName]` 165; C5's run: `Security-4688[CommandLine,NewProcessName,ParentProcessName]` 143. **The 4688 key lost its `CommandLine` field** |
| D3 K2, start without revert | host, Claude | A1's `Start-Process` line; `checkToolsState` | start 15:04:22; Tools `running` 15:04:38; `CPL0` |
| D3 K2, scan and read | guest, student (D0); host, Claude (the archive reader, read twice) | D0; `telos-archive tail 20000` | Scan `462484261`: 15:14:36 to 15:14:47; 123 passed, 350 failed. 26177 failed, 26270 failed, 26426 failed, 26148 passed, **26222 failed**, 26144 passed: **as predicted, 6 of 6**. Kept: `archive-sca-4.jsonl`, 2916 lines, SHA256 `B7AC4FD276B881AB088B0535B3760B7B7FA661166C18F37CA57C5B5E8C30D7AC` |
| D3, `trial-K3-1` | host, **student** (guest password) | `capture.py --run-id trial-K3-1 --phase post --change K3` | **`valid: True`**, no void reasons; the 5 stimulus steps exit 0; window 15:19:56 to 15:22:56, 558 events, **`broken_lines: 1`**. Manifest: `golden-base-v2`, K3 script `fb2cf4bc...`, `change_confirmed` true, `parameters_sha256` `9895d0cf...` |
| D3, K3 counts | host, Claude (read only) | `counts.json` | **No `Security-4688` key**; Sysmon 1 still there (`[CommandLine,Hashes,Image,OriginalFileName,ParentImage]` 70, without `ParentImage` 26) |
| D3, the broken line | host, Claude (read only) | a Python reader on `trial-K3-1\archive-2026-11-26.json.gz` | The last line, 28966 of 28966, 260 characters, cut off: SIEM-01's own systemd message at 15:25:05, after the window's end (15:22:56). `broken_lines` counts the whole export (`archive.py` line 150). **No WIN-EP-01 event in the window lost** |
| D3 K3, start without revert | host, Claude | A1's `Start-Process` line; `checkToolsState` | start 15:25:31; Tools `running` 15:25:47; `CPL0` |
| D3 K3, scan and read | guest, student (D0); host, Claude (the archive reader, after a 20 s wait) | D0; `telos-archive tail 20000` | Scan `264650422`: 15:27:54 to 15:28:06; 123 passed, 350 failed. 26177 failed, 26270 failed, 26426 failed, 26148 passed, 26222 passed, **26144 failed**: **as predicted, 6 of 6**. Kept: `archive-sca-5.jsonl`, 3261 lines (all 7 scans), SHA256 `E7DEB1F787930FA6C38ABC3153B0456A0DA1E72EA6C43FF1BC9BFD51B6F84190`. **Phase D: 7 states, 42 of 42 as predicted; 4 trial runs valid** |

**The 8 repo hashes before the guard (2026-11-26, SHA256; superseded the same day, A2 and A3 repeated):**

```
1D5DD96AA98F9E7A5B080AE5F761FA0562DD0E6836E72AA74626C85247CD1B9A  baseline-golden.ps1
CFB33DD622609BCC9AD8531FDD8B8796BFF34E0C5AA8EE51A25BA2AD07A719FD  change-C1-disable-wdigest.ps1
AC10E7BEAF766C145115EA62B75D59912B54FDF4D982623EA2A172FEC0A21FAA  change-C3-lsa-protection.ps1
FE1585AD957AB3DD571E73BBC28AD2D759404ABCBA8E45C069FAAB3144E966C5  change-C5-rdp-nla.ps1
6421827359C8B297CAB0B62935270106621715BCE9CF3E557F7BA36AB3507CFD  change-K1-audit-logon-off.ps1
FFE2D302C185A602B91CF52B78AEC54EF234E7197863C17F2F4D26290A026E18  change-K2-cmdline-off.ps1
8B7CCC9A30679573531C10BD488DC4F8DD8186E5714EE701A79CED8AADB087E9  change-K3-audit-process-creation-off.ps1
DE393E50D701D3FE212100EDCCCAA1E8A19F31D3B5014CC2D9958F93AB3F8FE2  config-S-defender-off.ps1
```

**The 8 repo hashes after the guard (2026-11-26, SHA256; A3 compares with these):**

```
DC2A007F8807137E68C537F713D8E1A67B9554A30441D5E4149C3108E9B6647B  baseline-golden.ps1
6A269612B13C77100908D6B0154293296441F172EFDE18A9E78CB88436114A4D  change-C1-disable-wdigest.ps1
C5A4B8CCC28CC57A1632060F15CD501F14D5BF31B706D64702783DF930E5B62A  change-C3-lsa-protection.ps1
A511F40D038A0A798E11434916EA0E20A470A62777AD3A29DBFE54BDEFCD8C4A  change-C5-rdp-nla.ps1
91D7302C43B343BB673C9B88EED827F57FDDEC86B854C43EBBFB0E13A7B21F4E  change-K1-audit-logon-off.ps1
AEB4759AAD6FCB618AC7EFAFD56BD793FD80FA2BF14D9CBF62178A5D4ABD58E7  change-K2-cmdline-off.ps1
FB2CF4BC6A632A0641D5ECBBDA78969653AFC4E3C1D4106E6878E3706266CEAA  change-K3-audit-process-creation-off.ps1
34B39FA12BF446F36C790A9849D40DD497FF9EC8A90284B849DB0F9228D392DE  config-S-defender-off.ps1
```

**Reading.** `CPL0`: VMware runs directly on the hardware. `ULM`: it runs on top of the Windows hypervisor. Checked on
this host by the `ULM` row; VMware community threads say the same (no official VMware page found). So the spike ran
with the hypervisor off, and it came back between 2026-11-16 13:22 and 2026-11-23 12:51. No lab run happened in
between.

**Undo.** Delete `data\runs\host-vmware-logs-2026-11-16\` (not in git). The `ULM` check left WIN-EP-01 off; A1's
revert removes its short start.

### 2.19 Phase E: the evaluation runs (from 2026-11-26 16:10 UTC)

Purpose: `docs/EXPECTED-RESULTS.md` section 5. First the 5 control runs with the pinned attack list; from them the
student decides item 22's void rule and the runs per phase (STATUS, "The spike"); then the before and after runs.

| Step | Where, by whom | Command | Result seen |
|---|---|---|---|
| Pre-flight | host, Claude (read only) | `vmrun -T ws list`; `listSnapshots`; VMnet2 IPv4; `HypervisorPresent`; `git log -1 --oneline`; `git status --short`; host start time | `Total running VMs: 0`; 7 snapshots, `golden-base-v2` once; `10.20.10.1`; **`False`**; `a1c318e`, only the 4 known untracked files; host started 2026-11-26 15:51:18 |
| Start SIEM-01 | host, Claude | `& $vmrun -T ws start $siem nogui`; `checkToolsState` every 5 s; `Monitor Mode` | Exit 0 at 16:14:01; **`CPL0`**; Tools still `installed` at 16:17:15 (late again, as at 10:52) |
| SIEM-01 health | host, Claude (read only) | `Test-NetConnection 10.20.10.10 -Port 22`; `ssh ... "uptime; systemctl is-system-running; systemctl is-active open-vm-tools wazuh-manager wazuh-indexer wazuh-dashboard; date -u"` | `True`; up 3 min, `running`, 4 × `active`; clock 16:17:36, host 16:17:36 |
| `eval-ctl-1`, first attempt | host, **student** (guest password) | `capture.py --run-id eval-ctl-1 --phase control` | **`STOPPED before producing data: VMware Tools not running after 300 s`**. No `data\runs\eval-ctl-1` folder was written. WIN-EP-01 powered on 16:22:10 |
| Why Tools was "not running" | host, Claude (read only, then one program start) | `checkToolsState` on both VMs; the `running status` lines of both `vmware.log`; `Test-NetConnection 10.20.10.20 -Port 3389`; `Get-Process vmware*`; `vmrun getGuestIPAddress`; then `Start-Process vmware.exe` (the Workstation window) and `checkToolsState` every 5 s | Both `installed`; WIN-EP-01's log shows the same status steps (0 to 1, 1 to 2, 2 to 1, by 16:22:24) as the working run of 15:25; port 3389 `True`; only `vmware-authd`, `vmware-usbarbitrator64` and 2 × `vmware-vmx` running; `getGuestIPAddress` "The VMware Tools are not running". **Window opened 16:30:17; both `running` at 16:30:23**, with `vmware-tray` and `vmware-unity-helper` now running. **Cause: after a host restart, `vmrun` sees Tools only while VMware Workstation's window program runs.** The same explains SIEM-01's late Tools at 10:52 (`running` 53 s after WIN-EP-01 was opened with a window) and at 16:14 |
| `eval-ctl-1`, second attempt | host, **student** (guest password) | the same command | **`STOPPED before producing data: VMware Tools not running after 300 s`** again; no folder written. WIN-EP-01 powered on 16:33:27 |
| Why, again | host, Claude (read only, then one tab opened) | `Get-Process vmware*`; `checkToolsState`; the `running status` lines; then `Start-Process vmware.exe -ArgumentList "`"$win`""` (opens WIN-EP-01 as a tab, no power change) and `checkToolsState` every 5 s | The window was open (`vmware` since 16:30:17); SIEM-01 `running`, WIN-EP-01 `installed`, its log normal. **Tab opened 16:52:26; WIN-EP-01 `running` at 16:52:32.** **Corrected cause: `vmrun` sees a VM's Tools only while that VM is open as a tab in the VMware window.** The window alone covered only the VMs that were running when it opened. On 2026-11-26 the trial runs worked because WIN-EP-01 had a tab from its `gui` starts |
| Double check before a third attempt (student: "double check again") | host, Claude (read only) | `ipconfig`; `ssh ... "date -u; date +%Z%z; telos-archive disk; telos-archive dated-list"`; host free bytes; `cmdkey /list:TERMSRV/10.20.10.20`; `Test-Path` of the password file (not read); the Windows Update restart keys and pause value; `powercfg` sleep and display; screen saver keys; the parameter hash in Python; `Test-Path data\runs\eval-ctl-1` | `10.20.10.1` present; SIEM-01 **`UTC+0000`**, disk 14%, `Nov/ossec-archive-26.json` present (154 MB); 2.28 TB free; `TERMSRV/10.20.10.20`, user `WIN-EP-01\eli`; `True`; no restart pending, **updates not paused**; sleep never, display never off, no secure screen saver; **`9895d0cf...14cd`**, the trials' hash; `False` |
| The harness's reset, repeated by hand | host, Claude | `revertToSnapshot $win golden-base-v2`; `start $win nogui`; `checkToolsState` every 5 s up to 300 s (the harness's own steps); then `getGuestIPAddress $win -wait` | 17:10:33 start; **`installed` after 328 s** with the WIN-EP-01 tab open; then the IP `10.20.10.20` |
| Start with a window, then the harness's reset | host, Claude | revert; the A1 `Start-Process ... gui` line; wait; then revert, `start nogui`, wait up to 300 s | With a window: `running` after 17 s. Then **`nogui`: `installed` after 327 s.** Logs: the window start has `MKSControlMgr: connected`; the `nogui` start has none; both show the same Tools steps (0 to 1, 1 to 2, 2 to 1 within 11 s) |
| What wakes the status | host, Claude (read only) | on the `nogui` VM: `checkToolsState`; `getGuestIPAddress` without and with `-wait`; `checkToolsState` | `installed`; without `-wait`: "The VMware Tools are not running"; **with `-wait`: `10.20.10.20` in 0.4 s; then `running`.** **Cause: Tools is ready within seconds, but `checkToolsState` reports `running` only after something waits on Tools (`-wait`) or VMware's window connects to the VM. The harness only polls `checkToolsState` (`harness.py` line 158), so after this host start it can never pass.** Why the same code passed on 2026-11-26 (4 trials) and 2026-11-16 (19 runs) is not known; those logs have rotated away. **This supersedes the two "Cause" lines above** (the window, then the tab) |
| The fix (student: "Yes, fix the harness wait") | host, Claude | `src/telos/harness.py`: `wait_tools()` runs `vmrun getGuestIPAddress <vmx> -wait` (limit 300 s) when the first `checkToolsState` is not `running`, then checks as before; `run_command(args, timeout)` returns 124 at the limit. Four tests in `tests/test_harness.py` | DECISIONS 2026-11-27 |
| Its checks | host, Claude | `pytest tests\test_harness.py -q` on the old code; then `pytest tests -q`; the parameter hash in Python; `git diff --stat` | Old code: **3 failed, 19 passed** (the stuck-status test with today's own error). New code: **160 passed**; hash **`9895d0cf...14cd`**, unchanged; 3 files |
| The fixed reset on the real lab | host, Claude (no guest call; the password file named does not exist) | a Python script: `Lab(cfg).reset_to_known_state()` with `settle_s=0`, then `lab.stop()`, then the reset again; every `vmrun` call timed | Reset 1: revert exit 0 (17:50:46), start exit 0, `checkToolsState` `installed`, **`getGuestIPAddress -wait` exit 0 after 10.7 s**, `checkToolsState` `running`: passed in 14.5 s. Stop exit 0 (8.6 s). Reset 2: the same, `-wait` 10.8 s, passed in 13.2 s. **0 guest calls** |
| Windows Update | host, student | Settings, Windows Update, Pause updates | "paused updates" (student), before `eval-ctl-1` |
| **`eval-ctl-1`** | host, **student** (guest password) | `capture.py --run-id eval-ctl-1 --phase control` (code `d16d3bf`) | **`valid: True`**, no void reasons; config-S 0; the 5 stimulus steps exit 0 (`rdp-signin-30s` 30.3 s); 7 guest calls; window 17:58:43 to 18:01:43, 710 events; 517.5 s. Manifest: `control`, no change, `golden-base-v2`, **`9895d0cf...14cd`** |
| `eval-ctl-1`, read | host, Claude (read only) | `run_manifest.json`; `counts.json`; the broken-line reader on the export | 4624: NTLM 2, **type 10 2** (the sign-in happened), type 2 3, other 20; 4688 with `CommandLine` 141; Sysmon 1: 71, 28, 1. The 1 broken line: the export's last line (39123), SIEM-01's own systemd message at 18:03:52, after the window: harmless, as in `trial-K3-1` |
| **`eval-ctl-2`** | host, **student** | `capture.py --run-id eval-ctl-2 --phase control` | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 18:08:44 to 18:11:44, 815 events, 0 broken lines; 521.3 s; `control`, **`9895d0cf...14cd`**. Counts: 4624 NTLM 2, type 10 2, type 2 3, other 25; 4688 with `CommandLine` **165** (`eval-ctl-1`: 141); Sysmon 1: 77, 40, 1 |
| **`eval-ctl-3`** | host, **student** | `capture.py --run-id eval-ctl-3 --phase control` | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 18:18:20 to 18:21:20, 805 events, 0 broken lines; 516.3 s; `control`, **`9895d0cf...14cd`**. Counts: 4624 NTLM 2, type 10 2, type 2 3, other 24; 4688 with `CommandLine` 164; Sysmon 1: 77, 41, 1 |
| `eval-ctl-3`, pasted again | host, Claude (read only) | the manifests' write times; `vmrun -T ws list` | The same output pasted twice; `eval-ctl-3` unchanged (manifest 18:23:32), no `eval-ctl-4` yet, WIN-EP-01 off (18:30:44) |
| **`eval-ctl-4`** | host, **student** | `capture.py --run-id eval-ctl-4 --phase control` | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 18:34:39 to 18:37:39, 713 events, 0 broken lines; 516.4 s; `control`, **`9895d0cf...14cd`**. Counts: 4624 NTLM 2, type 10 2, type 2 3, other 20; 4688 with `CommandLine` 143; Sysmon 1: 72, 27, and **no `Sysmon-1[CommandLine,Hashes,Image]` key** (1 in runs 1 to 3) |
| **`eval-ctl-5`** | host, **student** | `capture.py --run-id eval-ctl-5 --phase control` | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 18:44:34 to 18:47:34, 798 events, 1 broken line (the export's last line, SIEM-01's own systemd message at 18:49:47: harmless); 519.5 s; `control`, **`9895d0cf...14cd`**. **5 of 5 control runs valid** |
| The 5 control runs, summary | host, Claude (read only) | a Python reader of the 5 `counts.json`: per key the 5 counts, mean and CoV; Sysmon 1 per run | Events 710, 815, 805, 713, 798. 35 keys, 18 with CoV 0. **Two groups:** runs 1 and 4 low, runs 2, 3 and 5 high, in the same keys: `Application-1001[]` 0 against 3, `Security-5379[]` 50 against 70 to 74, 4688 141 to 143 against 163 to 165, `Sysmon-10` 109 to 111 against 121 to 131, `Security-4672[]` 27 against 31 to 32. Sign-in keys constant (4624 NTLM 2, type 10 2). **Sysmon 1 per run (item 22's fingerprint): 100, 118, 119, 99, 118; mean 110.8, sd 10.3, CoV 9.3%** (spike, trial stimulus: 37 to 44) |
| False-finding check (student: "Yes, run the check") | host, Claude (read only) | a Python script with the project's `analyse`, `VarianceModel.from_control` and `load_phase` on the 5 control runs: (1) the spike's Q3, every pair of single runs, both directions; (2) every 2-vs-2 split; (3) Q4; then (4) out of sample: the noise model from 3 runs, the other 2 compared 1 against 1, both directions | (1) 20 comparisons, **0 false findings**; (2) 30 comparisons, **0**, including before 2+3 (high) against after 1+4 (low) and the reverse; (3) 35 keys, **15 testable** (spike: 11 of 20); (4) 20 comparisons, **0**. Any LOST or REDUCED here would be false, because nothing changed |
| The proposed void rule against all 9 runs | host, Claude (read only) | Sysmon 1 per window and the `rdp-signin-30s` exit code of the 5 control runs and the 4 trial runs | Sysmon 1: 100, 118, 119, 99, 118 (controls); 99, 98, 118, 96 (C5, K1, K2, K3 trials): **all inside 80 to 142** (mean plus or minus 3 sd); `rdp-signin-30s` exit 0 in all 9 |
| The two decisions (student: "Yes, accept both") | host, Claude | DECISIONS 2026-11-27: 3 runs per phase; item 22's void rule | Range computed from the 5 fingerprints: 110.8 ± 3 × 10.33 = **79.8 to 141.8** (80 to 141 pass; first told to the student as "80 to 142", corrected before the build) |
| The void rule, built | host, Claude | `harness.RunChecks`, `catalog.CONTROL_FINGERPRINTS` and `RUN_CHECKS`, `capture.py`; 5 tests; `pytest tests\test_harness.py -q` before the code; `pytest tests -q`; the hash; the rule on the 9 saved runs; `capture.py --help` | Before the code: **5 failed, 22 passed**. After: one test had its own setup error (2 folders missing), fixed; **165 passed**; hash **`9895d0cf...14cd`**; the 9 runs: fingerprints 100, 118, 119, 99, 118, 99, 98, 118, 96, **all pass**; the usage text |
| **`eval-pre-1`** | host, **student** (guest password) | `capture.py --run-id eval-pre-1 --phase pre` (code `b0c6770`) | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 19:43:12 to 19:46:12, 700 events, 0 broken lines; **fingerprint 96** (range 79.8 to 141.8); 516.2 s; `pre`, **`9895d0cf...14cd`**. Counts: type 10 2; 4688 138; 5379 47; no `Application-1001` (a "low" run) |
| **`eval-pre-2`** | host, **student** | `capture.py --run-id eval-pre-2 --phase pre` | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 20:02:30 to 20:05:31, 706 events, 0 broken lines; **fingerprint 98**; 518.2 s; `pre`, **`9895d0cf...14cd`**. Counts: type 10 2; 4688 142; 5379 47; no `Application-1001` (low) |
| `eval-pre-3`, first attempt | host, **student** | `capture.py --run-id eval-pre-3 --phase pre` | **`STOPPED before producing data: vmrun start failed`**; no run folder |
| Why | host, Claude (read only) | `vmrun -T ws list`; the newest `vmware.log` (power and error lines); the `.lck` files; host start time; free space on F: | WIN-EP-01 **running**: `VMAutomation_PowerOn` at 20:09:46 with `success=1`, Tools' `OS_PowerOn` script at 20:09:57; at 20:09:46.442 **`VmdbPipeStreamsOvlError Couldn't read: (109) The pipe has been ended`**: vmrun's connection broke, so it reported a failure for a start that worked. Locks: those of a running VM. Host start still 15:51:18; F: 138.3 GB free. **A one-off** (first in 30 runs); if it repeats, the harness could check `vmrun list` after a failed start. `eval-pre-3` is still unused |
| **`eval-pre-3`** | host, **student** | the same command, again | **`valid: True`**, no void reasons; the 5 steps exit 0; 7 guest calls; window 20:14:35 to 20:17:35, 695 events, 1 broken line (the export's last line, SIEM-01's own systemd message at 20:19:44: harmless); **fingerprint 97**; 519.7 s; `pre`, **`9895d0cf...14cd`**. Counts: type 10 2; 4688 137; 5379 47; no `Application-1001` (low). **3 of 3 before runs valid, all three "low"** (695 to 706 events; the controls had 2 low, 3 high) |
| **`eval-post-C1-1`** | host, **student** | `capture.py --run-id eval-post-C1-1 --phase post --change C1` | **`valid: True`**, no void reasons; the 5 steps exit 0; 9 guest calls; window 20:25:12 to 20:28:12, 710 events, 0 broken lines; **fingerprint 98**; `post`, C1 script `6a269612...`, **`change_confirmed` true**, **`9895d0cf...14cd`**. Counts: type 10 2; 4688 139; 5379 54; no `Application-1001` (low) |
| The batch (student: "can this be done in simultaneous so I can leave my PC", then "Yes, build it") | host, Claude | `src/telos/evaluation.py` (the plan of all 26 runs); `src/evaluate.py` (the spike's `run_batch`, `capture.lab_config`, the pinned stimulus, `RUN_CHECKS`); `capture.py` refactored to `lab_config()`; 5 tests in `tests/test_evaluation.py`; `pytest`; both `--help`; the plan against `data\runs` | Not in parallel: one WIN-EP-01. Tests: failed first (no module), then **170 passed**; the batch's settings equal `capture.py`'s and give **`9895d0cf...14cd`**; both commands start; **9 done, 17 to run**, from `eval-post-C1-2` to `eval-post-K3-3` |
| **`eval-post-C1-2`** | host, **student**, by hand (not the batch) | `capture.py --run-id eval-post-C1-2 --phase post --change C1` (code `b3c3bca`) | **`valid: True`**, no void reasons; the 5 steps exit 0; 9 guest calls; window 20:45:59 to 20:48:59, 717 events, 0 broken lines; **fingerprint 99**; `post`, C1, **`change_confirmed` true**, **`9895d0cf...14cd`**. Counts: type 10 2; 4688 143; 5379 54; no `Application-1001` (low). The batch skips it: 16 left |
| **The batch** | host, **student** | `.\.venv\Scripts\python.exe src\evaluate.py` | Ran `eval-post-C1-3` (finished 21:05:15) to `eval-post-K2-2` (22:53:46): **13 runs, all valid** |
| **Power cut** | host (the student unplugged the PC by accident) | — | System log: Kernel-Power **41 at 22:55:26**, EventLog 6008 at 22:55:38; host started again 23:15:02. Lost: `eval-post-K2-3`, in progress, **no folder written** (a run writes its folder only after the stop) |
| After the power cut | host, Claude (read only) | host start time; `HypervisorPresent`; VMnet2 IPv4; `vmrun list`; event 41 and 6008; every `eval-*` folder; `.lck` files; `git status` | `False`; `10.20.10.1`; 0 VMs; **22 runs with a manifest, all valid**; old `.lck` files in both VM folders; the repo and the unsaved COMMANDS rows intact |
| SIEM-01 after the cut | host, Claude | `vmrun -T ws start $siem nogui`; port 22; `ssh ... "uptime; systemctl is-system-running; systemctl is-active ...; journalctl -b ..."` | Exit 0 at 23:19:33 (VMware cleared the old locks itself); port 22 at 23:19:55; `running`, 4 × `active`; `/dev/sda2: clean`; errors only the usual VM hardware messages (SMBus, Bluetooth) |
| The 13 batch runs, read | host, Claude (read only) | each `run_manifest.json` and `counts.json` | All `9895d0cf`, all `change_confirmed` true, fingerprints 97 to 121; **K1 runs: 0 type 10 logons** (others 2); C3 runs 12.7 min (the restart), others 8.7 to 8.8; groups mixed: high C1-3, C5-1, K1-1, K1-2 (and C3-2, C3-3 high in 4688 without `Application-1001`); **4 left: K2-3, K3-1 to K3-3** |

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

### 3.7 Counting event IDs in the archive, from the host (added 2026-09-26)

Used for the OPEN-QUESTIONS 21 check. One pattern file per event ID, written on the host with Unix
line endings, copied to SIEM-01, then counted per date. Only file names appear on the `sudo` line.

```bash
printf '"eventID":"4776"\n' > p4776.txt        # Git Bash on the host. One ID per file.
```
```powershell
$key = "$env:USERPROFILE\.telos\siem01_ed25519"
scp -i $key p4776.txt eli@10.20.10.10:/home/eli/item21/
ssh -i $key eli@10.20.10.10 "sudo -n /usr/local/sbin/telos-archive dated-list"
ssh -i $key eli@10.20.10.10 "sudo -n /usr/local/sbin/telos-archive count /home/eli/item21/p4776.txt 2026-09-02"
ssh -i $key eli@10.20.10.10 "sudo -n /usr/local/sbin/telos-archive show /home/eli/item21/p4624.txt 5000 2026-09-02" | Out-File -Encoding utf8 e4624.jsonl
```

| | |
|---|---|
| **What** | Lists the dated archives, counts lines matching one event ID on one date, and downloads matching events for grouping on the host. |
| **Why** | `count` with a multi-line pattern file returns **one total** for all patterns. One file per ID gives one number per ID. |
| **Correct result** | A number per date. On 2026-09-26: 4768, 4769 and 4776 were `0` on every date; 4624 was `1764`, `140` and `988` on 09-02, 09-03 and 09-10. |
| **Traps** | A pattern file with Windows line endings matches nothing, because the `\r` becomes part of the pattern. Check with `od -c`. `dated-list` exits `1` even when it works, from its last test line. SIEM-01's dates are UTC, so a morning run in the Philippines lands on the previous date. **A loop passed inline from PowerShell to `ssh` loses its quotes and spaces** and the output runs together. Put the loop in a `.sh` file with Unix line endings, `scp` it, and run `ssh ... "bash /home/eli/item21/count.sh"`. |
| **Safe to re-run** | Yes. Read only. |

**Grouping the downloaded logons (added 2026-09-28).** This is the step that produced the logon table
in OPEN-QUESTIONS 21. Run it in Git Bash in the folder holding the `e4624-<date>.jsonl` downloads:

```bash
.venv/Scripts/python.exe - <<'EOF'
import json, glob, collections
for f in sorted(glob.glob("e4624-*.jsonl")):
    c = collections.Counter()
    for line in open(f, encoding="utf-8-sig"):
        if line.strip():
            e = json.loads(line)["data"]["win"].get("eventdata", {})
            c[(e.get("logonType"), e.get("authenticationPackageName"), e.get("targetUserName"))] += 1
    print(f, sum(c.values()))
    for (t, pkg, user), n in c.most_common():
        print(f"  {n:5d} type={t} pkg={pkg} user={user}")
EOF
```

| | |
|---|---|
| **What** | Counts the downloaded 4624 events by logon type, authentication package and target user. Reads files only. |
| **Why** | A search pattern can give a false zero. `"authenticationPackageName":"NTLM"` returned 0 because the local package is named `MICROSOFT_AUTHENTICATION_PACKAGE_V1_0`. Grouping shows every value that occurs, and the groups must add up to the 4624 total. |
| **Correct result** | On the 2026-09-02 download: `1764`, then `1641 type=4 pkg=MICROSOFT_AUTHENTICATION_PACKAGE_V1_0 user=eli`, `119 type=5 pkg=Negotiate user=SYSTEM`, `4 type=2 pkg=Negotiate user=eli`. Re-run and matched on 2026-09-28. |
| **Safe to re-run** | Yes. |

---

## Part 4: The five commands used from now on

### Run the system

```bash
.venv/Scripts/python.exe src/demo.py
```
**Correct result.** The noise floor table, the analysis, then the Stage D comparison:
`naive differencing  3  7  0  30.0%  100.0%  0.462` and `proposed system  3  0  0  100.0%  100.0%  1.000`.
Checked 2026-09-28. *(Until then this line said "naive at 20.0% precision", which the demo has not
printed since its scenario changed.)*

**To refresh `docs/demo-output.txt`**, which the READMEs link to, use Git Bash, not PowerShell:

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe src/demo.py > docs/demo-output.txt
```

PowerShell's `>` rewrites the encoding and would change every byte of the file. The Git Bash command
above reproduced the committed file byte for byte on 2026-09-28. Without `PYTHONIOENCODING=utf-8`,
Python on this host may fail on the non-ASCII characters in the output.

### Run the tests

```bash
.venv/Scripts/python.exe -m pytest tests -v
```
**Correct result.** `58 passed` (checked 2026-09-28).
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

Run all five before starting a runbook phase. All five must pass.

```bash
"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws list
```
Expect `Total running VMs: 0`

```powershell
(Get-CimInstance Win32_ComputerSystem).HypervisorPresent
```
Expect `False`. **If it says True, the hypervisor came back and timing is compromised.**
Re-run the Part 1.1 command and restart.
**2026-11-26:** it said `True`. Windows had been reinstalled in place on 2026-11-23, and the hypervisor has started at
every host start since then (COMMANDS 2.18). Check it again after any Windows reinstall or feature update.

```bash
.venv/Scripts/python.exe -m pytest tests -q
```
Expect the number in CLAUDE.md's Commands section (`170 passed` on 2026-11-26 after the evaluation batch; `165` after
the void rule; `160` after the
Tools-wait fix; `156` before it; it was `58 passed` on 2026-09-28)

```bash
git status --short
```
Expect blank

```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "VMware Network Adapter VMnet2").IPAddress
```
Expect `10.20.10.1`. **Anything else, or an error, means the host has lost the lab network.** Fix
it with Part 1.3 and 1.4 first. Added 2026-09-26, OPEN-QUESTIONS 27.

**No VMware-window check is needed (DECISIONS 2026-11-27).** A check that the VMware window and the VM tabs are open
was added here on 2026-11-26 after two stopped runs, and removed the same evening: the real cause was that
`checkToolsState` stays at `installed` until something waits on Tools, and the harness now does that wait itself
(COMMANDS 2.19). If a run ever stops again with "VMware Tools not running", run
`& $vmrun -T ws getGuestIPAddress $win -wait`: an IP means Tools runs, and the cause is elsewhere.
