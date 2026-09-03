# RUNBOOK: Build the T1 Homelab From Scratch

Purpose: rebuild the whole lab from a bare host, in order, without remembering anything.
Follow top to bottom. Every phase ends with a check. Do not skip a check.

If you are only doing T2 or T3, skip to Phase 8. Those topics need no lab.

Host: Ryzen 7950X (16C/32T), 64 GB RAM, VMware Workstation 17.5.1 Pro.
Drives: C: NVMe (host, Python) - F: NVMe (all VMs) - E: HDD (this repo, archives, backups).

**The one rule that breaks the thesis if broken: no VM ever runs from E:.**
E: is a hard disk. Its seek delay changes process timing, which changes event
order and counts, which lands straight in the coefficient of variation number
that T1's entire statistics argument rests on. You would be measuring your disk.

---

## Phase 0. Before you start

- [ ] Confirm F: has at least 350 GB free.
- [ ] Confirm virtualization is on in BIOS (AMD SVM).
- [ ] Download ISOs to E:\iso\ : Ubuntu Server 22.04 or 24.04 LTS, Windows 11 Enterprise Eval
      (or Server 2022 Eval).
- [ ] Install Python 3.11+ on C:. Create a venv. Do not use system Python.
- [ ] Note the path to `vmrun.exe`. Default is
      `C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe`.
- [ ] Open `docs/DECISIONS.md` and `docs/WORKLOG.md`. You will write in both as you go.

**Check:** `vmrun.exe -T ws list` runs and prints a total. If it errors, stop and fix VMware first.

---

## Phase 1. Virtual networks

Open VMware Workstation, then Edit menu, then Virtual Network Editor, then Change Settings
for admin rights.

- [ ] `vmnet2` = Host-only. **Turn DHCP OFF.** Subnet 10.20.10.0/24.
      Leave "Connect a host virtual adapter" ON. The harness needs to reach the Wazuh API.
- [ ] `vmnet3` = Host-only. DHCP OFF. Subnet 10.20.20.0/24. Tier B only, skip for now.
      **On this host it has a host adapter connected, at `10.20.20.1/24`, and no VM is attached
      to it.** Verified 2026-09-03. That is deliberate and harmless while nothing uses the
      network. **If `IDS-01` is ever built here as a monitor segment and the thesis claims that
      segment is isolated, untick "Connect a host virtual adapter to this network" first and
      re-verify the claim.** See OPEN-QUESTIONS item 7.
- [ ] `vmnet8` = NAT. Leave default. This is for installing and patching only.

Every VM gets a static IP. DHCP lease renewal is itself a logged event, and it fires
on its own schedule inside your measurement window.

Planned addresses:

| Host | IP |
|---|---|
| Windows host (vmnet2 adapter) | 10.20.10.1 |
| SIEM-01 | 10.20.10.10 |
| WIN-EP-01 | 10.20.10.20 |

**Check:** `ipconfig` on the host shows a VMware adapter on 10.20.10.x.

---

## Phase 2. Build SIEM-01 (Wazuh)

VM spec: 8 vCPU, 16 GB RAM, 200 GB thin disk **single file, not split**, stored on F:. Ubuntu
24.04 LTS.

> **This phase was executed and verified on 2026-09-02.** Every command below produced the
> result it claims. The traps marked **TRAP** were each hit for real. None of them printed an
> error. Full session record in `docs/WORKLOG.md`, reasoning in `docs/DECISIONS.md`, and every
> command with its correct result in `docs/COMMANDS.md` section 2.9.

### 2.1 Create the VM

- [ ] Create it on F:. One adapter, `ethernet0`, on **vmnet8 (NAT)**. You add the lab adapter
      later, deliberately, as the second one.
- [ ] Disk: 200 GB thin, **single file**. F: is NTFS, so the 2 GB split option buys nothing.
- [ ] Use Ubuntu **24.04**, not 26.04. Wazuh officially supports up to 24.04.

### 2.2 Install Ubuntu Server

- [ ] **Decline the installer self-update.** It offers to update itself (24.04.4 to 24.04.4.1).
      Choose **"Continue without updating"**. The installer is fetched live, so accepting it
      makes the build depend on the day it ran. The installed OS is 24.04.4 either way.
- [ ] Type of install: **"Ubuntu Server"**, not minimized. Leave third-party drivers unchecked.
- [ ] Network: leave `ens33` on DHCP. Note the address it gets. That proves NAT works.
- [ ] Storage: "Use an entire disk".

> **TRAP 1. The storage screen silently gives root half the disk.**
> "Set up this disk as an LVM group" is checked by default. With it checked, the installer
> creates a 198 GB volume group and then a root logical volume of only **99 GiB**, leaving the
> rest unallocated. No error. No warning. `df` reports a plausible number and you lose half the
> disk. Either untick LVM, or keep it and run step 2.4 below.

- [ ] **Server name: `SIEM-01`.** The installer lowercases it to `siem-01`. That is fine and
      expected. Lowercase is the Linux convention and it is what every Wazuh event field will
      show. Do not fight it.
- [ ] Username and password: the Phase 6 harness connects with these. Save them now.
- [ ] **Check "Install OpenSSH server".** This is the single easiest step to miss and it fails
      silently until Phase 6 cannot reach the machine.
- [ ] Featured server snaps: select **none**.
- [ ] At the reboot prompt, before pressing Enter, use the VMware menu:
      **VM > Removable Devices > CD/DVD (SATA) > Disconnect.** Otherwise it boots the installer
      again. Confirm afterwards that the `.vmx` contains `sata0:1.startConnected = "FALSE"`.

**Step check:** a `siem-01 login:` prompt, and you can log in.

### 2.3 First login: verify SSH and record the firewall baseline

```bash
ip -brief addr show
systemctl is-enabled ssh.socket
sudo ufw status
```

Expect `ens33` UP with a `192.168.243.x` address, `enabled`, and `Status: inactive`.
**Record the `ufw` result in the worklog.** It is what makes later results interpretable: if a
packet does not arrive in a Phase 6 run, the firewall is not the reason.

> **TRAP 2. `systemctl is-active ssh` returns `inactive` on a healthy machine.**
> Ubuntu 24.04 starts SSH by socket activation. `systemd` holds port 22 and starts `sshd` only
> when a connection arrives, so `ssh.service` is correctly inactive at rest. Check
> **`ssh.socket`**, or just connect. Do not "fix" `ssh.service`.

> **TRAP 3. SSH over NAT times out if VMnet8 has no host adapter.**
> If `ssh <user>@<nat-ip>` times out, run `Get-NetAdapter` on the host. If there is no
> "VMware Network Adapter VMnet8", Windows has no address on that subnet and no route to the VM.
> Fix: Virtual Network Editor, VMnet8, tick **"Connect a host virtual adapter to this network"**.
> This is a host baseline change. Record it.

### 2.4 Give root the whole disk (skip only if you unticked LVM)

```bash
lsblk
df -h /
sudo vgs
```

If `df -h /` shows about **97G** instead of about 195G, TRAP 1 caught you. Fix it online, no
reboot needed:

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
df -h /
```

**Correct result:** `195G` total. **This is one-way.** Shrinking an ext4 root filesystem needs
boot media.

### 2.5 Lab network and static IP

- [ ] Shut down. VM settings, Add, Network Adapter, Custom, **VMnet2**. Boot.
- [ ] **Find the interface name. Do not assume it.**

```bash
ip link show
```

> **TRAP 4. The name is not `ens34`.**
> It comes from the PCI slot in the `.vmx`. `ethernet0.pciSlotNumber = "33"` gives `ens33` and
> `ethernet1.pciSlotNumber = "37"` gives **`ens37`**, which is what this build actually used.
> Read the real name and use it in the file below.

```bash
sudo tee /etc/netplan/01-lab-static.yaml > /dev/null <<'EOF'
network:
  version: 2
  ethernets:
    ens37:
      dhcp4: false
      addresses: [10.20.10.10/24]
EOF
sudo chmod 600 /etc/netplan/01-lab-static.yaml
sudo netplan apply
```

Use a heredoc, not `nano`. YAML depends on exact indentation and an editor can add or drop
spaces invisibly. The `01-` prefix makes netplan read this before the installer's
`50-cloud-init.yaml`, which owns `ens33`. They configure different interfaces and do not fight.

**Step check:**

```bash
ip -brief addr show ens37
ip route
```

`ens37 UP 10.20.10.10/24`, and **exactly one `default` line, on `ens33`**. A second `default`
line on `ens37` means the lab network is carrying internet traffic and isolation is broken.
Then confirm `ssh <user>@10.20.10.10` works from the Windows host.

> If SSH refuses with "REMOTE HOST IDENTIFICATION HAS CHANGED", an earlier machine used this
> address. **Verify before deleting anything:** compare the MAC answering at `10.20.10.10`
> against `ethernet1.generatedAddress` in the `.vmx`. Then `ssh-keygen -R 10.20.10.10`.

Why static: a DHCP lease renewal is itself a logged event firing on its own schedule inside
your measurement window.

### 2.6 Stop apt from updating itself, then patch once

**Do this before the Wazuh install**, so an apt timer cannot take the dpkg lock halfway through
a 20 minute root install.

```bash
sudo systemctl disable --now apt-daily.timer apt-daily-upgrade.timer
sudo sed -i 's/"1"/"0"/' /etc/apt/apt.conf.d/20auto-upgrades
systemctl is-enabled apt-daily.timer apt-daily-upgrade.timer
```

Expect `disabled` twice.

> **TRAP 5. Doing nothing does not freeze the machine.**
> Ubuntu 24.04 installs security updates on its own schedule by default. The choice is not
> "change it or leave it alone". It is "change it now on purpose and write it down" or "let it
> change itself later, mid-run, and discard every run before it".

Then patch once, deliberately:

```bash
sudo apt update
sudo apt list --upgradable      # SAVE THIS OUTPUT. It cannot be recovered afterwards.
sudo apt upgrade -y
apt list --upgradable           # must print only "Listing... Done", nothing kept back
ls /var/run/reboot-required     # silence means no reboot needed
```

Watch the upgradable list for `linux-`, `systemd`, `openssh`, `auditd`, `rsyslog`. Those decide
what the machine logs. After the upgrade and any reboot, re-check `ip route`, `uname -r` and
`timedatectl`. A `cloud-init` major version bump is the one most likely to disturb step 2.5.

### 2.7 Install Wazuh all-in-one

**Download it and read it before running it as root.**

```bash
cd ~ && curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh
ls -lh wazuh-install.sh && sha256sum wazuh-install.sh
grep -n -A 14 "nodes:" wazuh-install.sh
```

Use the pinned **`4.14`** path, not `4.x`. `4.x` returns whatever is newest on the day it runs.
Record the SHA256 in `docs/DECISIONS.md`: it identifies exactly which file you ran.

The `grep` shows the config the script writes. In this build, lines 97 to 106 showed the
all-in-one path issues certificates for **`127.0.0.1`**, which is why the Phase 5 NAT disconnect
cannot break Wazuh component communication. Confirm that is still true before you rely on it.

Run it **inside tmux**:

```bash
tmux new -s wazuh
sudo bash ./wazuh-install.sh -a 2>&1 | tee ~/wazuh-install-console.log
```

> **TRAP 6. A dropped SSH session kills a plain install halfway through.**
> This runs as root for 10 to 20 minutes. Inside tmux, a dropped connection costs nothing:
> reconnect and `tmux attach -t wazuh`. A half-installed Wazuh has no clean uninstall. The fix
> is rebuilding the VM.

- [ ] **Record the version:**

```bash
sudo /var/ossec/bin/wazuh-control info
dpkg -l | grep -i wazuh | awk '{print $2, $3}'
```

Cite the **apt package version** (`4.14.7-1` in this build), not `WAZUH_REVISION`, which read
`rc1` for reasons nobody has explained. Put it in the pinned-versions table in
`docs/DECISIONS.md`.

- [ ] **The admin password goes in a password manager. Never in this repo.** To read it again:

```bash
sudo tar -O -xf ~/wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

`-O` prints to screen instead of unpacking, so no second plaintext copy is left behind.

- [ ] If it fails: `/var/log/wazuh-install.log`. Read the error before retrying. A retry needs
      `-o` to overwrite, and a failed install leaves services running.

### 2.8 Lock the version (three locks, all needed)

```bash
sudo sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
cat /etc/apt/sources.list.d/wazuh.list
sudo apt update
sudo apt-mark hold wazuh-manager wazuh-indexer wazuh-dashboard && apt-mark showhold
```

**Correct result:** the line starts with `#deb`, the `apt update` output contains **no**
`packages.wazuh.com` line, and `showhold` lists all three packages.

> **TRAP 7. Pinning the download does not pin the machine.**
> The installer, fetched from the pinned `4.14` path, configures apt to track **`4.x`**. So the
> repo must be disabled regardless. The `apt-mark hold` is a third lock, because a repo can be
> re-added by a reinstall or by hand and a hold still blocks the upgrade.

### 2.9 Turn on full archiving

**This is the single setting that makes T1 possible.** Without it Wazuh keeps only events that
fired a rule. T1 counts what the machine *emits*, not what alerted.

Look before you edit. Wazuh ships the setting present and set to `no`, so this changes a line
rather than adding one. Adding a duplicate XML tag can stop the manager starting.

```bash
sudo grep -n "logall" /var/ossec/etc/ossec.conf
sudo cp -a /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.pre-logall.bak
sudo sed -i 's|<logall_json>no</logall_json>|<logall_json>yes</logall_json>|' /var/ossec/etc/ossec.conf
sudo grep -n "logall" /var/ossec/etc/ossec.conf
sudo systemctl restart wazuh-manager && sleep 15 && systemctl is-active wazuh-manager
```

Use `cp -a`, not `cp`. `ossec.conf` is `root:wazuh` with restricted permissions, and a restored
backup must still be readable by the manager.

Leave `<logall>` at `no`. It writes a second archive in plain text, roughly doubling disk for
the raw line, while `logall_json` gives the decoded event with its fields, which is what the
unit of analysis needs.

### 2.10 Prove archiving works, correctly

```bash
logger "TELOS-TEST-EVENT-001"
sudo -i
grep -c "TELOS-TEST-EVENT-001" /var/ossec/logs/archives/archives.json
exit
```

**Correct result: exactly `1`.** One emitted event, one archive line. The event matched no rule
and raised no alert, and it was archived anyway. That is the behaviour T1 depends on.

> **TRAP 8, and it is the one that would corrupt results.**
> Do **not** run `sudo grep -c "MARKER" archives.json`. `sudo` writes every command line to
> journald, Wazuh collects journald, so the search creates a new event containing the marker and
> then counts it. One `logger` event returned `2`, then `3`, on repeated searches. Read from a
> `sudo -i` root shell, where individual commands are not logged by `sudo`, or pass the pattern
> from a file with `grep -f`. **The Phase 6 harness must obey this rule too.** See
> OPEN-QUESTIONS 1b.

Also record what this machine can actually see:

```bash
sudo grep -n "location>" /var/ossec/etc/ossec.conf
```

In this build the answer was exactly three sources: **`journald`**,
`/var/ossec/logs/active-responses.log`, and `/var/log/dpkg.log`. There is no `/var/log/syslog`
and no `/var/log/auth.log`. Anything not passing through those three cannot appear in your
results, whatever a hardening change does. journald also drops messages above its rate limit by
design, which is an unmeasured loss channel inside the measurement pipeline. See
OPEN-QUESTIONS 1d.

### 2.11 Disable vulnerability detection

```bash
sudo cp -a /var/ossec/etc/ossec.conf /var/ossec/etc/ossec.conf.pre-vd.bak
sudo sed -i '/<vulnerability-detection>/,/<\/vulnerability-detection>/s|<enabled>yes</enabled>|<enabled>no</enabled>|' /var/ossec/etc/ossec.conf
sudo sed -n '110,120p' /var/ossec/etc/ossec.conf
sudo systemctl restart wazuh-manager && sleep 20 && systemctl is-active wazuh-manager
sudo grep -i "vulnerability" /var/ossec/logs/ossec.log | tail -3
```

**Why:** it ships with `<feed-update-interval>60m</feed-update-interval>` and was observed
downloading a CVE feed hourly, running about 20 minutes, then triggering a full re-scan. It had
consumed 12 GB. It observes package inventory rather than events, so it cannot contribute to the
measurement, and it loses internet at Phase 5 and would then log failures forever.

**Correct result:** the printed block shows vulnerability detection at `no` **and `<indexer>`
still at `yes`**, then the log says `Vulnerability scanner module is disabled.`

> **TRAP 9. The `sed` range is not optional.**
> `ossec.conf` has several `<enabled>yes</enabled>` lines and the `<indexer>` block has one
> immediately below this one. A plain search and replace switches off the indexer too, and Wazuh
> silently stops storing anything. **Always confirm `<indexer>` still reads `yes` afterwards.**

Leave the 12 GB at `/var/ossec/queue/vd` in place. Once the machine is isolated in Phase 5 that
data cannot be downloaded again.

### 2.12 Indexer footprint: verify, do not change

```bash
curl -sk -u admin "https://127.0.0.1:9200/_cluster/health?pretty"
curl -sk -u admin "https://127.0.0.1:9200/_cat/indices?v&h=health,status,index,pri,rep,docs.count,store.size"
curl -sk -u admin "https://127.0.0.1:9200/_template/wazuh?filter_path=**.settings&pretty" | grep -E "shards|replicas"
```

`-u admin` with no password makes curl prompt for it. Always do that: a password on a command
line lands in shell history and is visible to anyone listing processes. `-k` is acceptable here
only because the connection is to `127.0.0.1` on the same machine.

**Replicas were already 0** in this build, for both existing and future indices. Health was
`green` with `active_primary_shards` equal to `active_shards` and `unassigned_shards: 0`, every
index showed `rep 0`, and the `wazuh` template sets `number_of_replicas: "0"` with
`auto_expand_replicas: "0-1"`, which keeps a single node at 0 by itself. **Verify this. Only
change it if the numbers disagree.**

**Retention is deliberately not set here.** The 16 GB and 200 GB figures in the blueprint were
guesses. The measured idle baseline is about **9.7 MB per day** with no agents connected, and
159 GB free after the full build, so the disk is not the near-term risk. The number that matters
is growth under load, which needs a real Phase 6 run. Set retention then, from a measurement.
Until then, **the harness free-space check in Phase 6 is what prevents a filled disk, so it must
actually be implemented.** See OPEN-QUESTIONS item 3.

### Phase 2 check

```bash
sudo ls -lh /var/ossec/logs/archives/
```

`archives.json` present, non-zero, and larger a minute later. `archives.log` at 0 bytes is
correct. Plus the marker test in 2.10 returning exactly `1`.

**Before starting Phase 3, write up the phase** per the rules in `CLAUDE.md`: WORKLOG,
DECISIONS, the pinned-versions table, OPEN-QUESTIONS, COMMANDS, then commit and push.

---

## Phase 3. Build WIN-EP-01 (endpoint)

VM spec: 4 vCPU, 8 GB RAM, 80 GB thin disk, **stored on F:**.

**Rewritten 2026-09-02 to match the build that was actually executed.** Every command with its
explanation, expected output and reversal is in `docs/COMMANDS.md` section 2.10. Every pinned
value is in `docs/DECISIONS.md`.

### 3.0 Decide two things before you start

Both are hard to reverse once the golden snapshot exists.

**Windows edition.** Do **not** use Windows 11 Enterprise Evaluation. It expires after 90 days
and then shuts down once per hour, and reverting a snapshot does not fix it because the grace
period counts from the install date inside the restored image against the real clock. Use
**Windows 11 Education from a retail multi-edition ISO, left unactivated.** Same security feature
set as Enterprise, and no timer at all. Reasoning in DECISIONS.md.

**Firmware.** UEFI with Secure Boot **on**, and **no virtual TPM**. Workstation 17 requires the VM
to be encrypted before it will attach a TPM, and an encrypted VM needs a password at power-on,
which the unattended Phase 6 harness would have to carry in a public repository. Secure Boot
without a TPM still permits VBS, so hardening change #8 stays possible.

### 3.1 Create the VM

- [ ] Create the disk from the command line, not the wizard. The wizard forces a TPM and
      encryption on a Windows 11 guest.

```powershell
vmware-vdiskmanager.exe -c -s 80GB -a lsilogic -t 0 "F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmdk"
```

- [ ] Write the `.vmx` by hand. Two NICs: `ethernet0` on VMnet8 (NAT), `ethernet1` on VMnet2.
      Required settings and why:

| Setting | Value | Reason |
|---|---|---|
| `firmware` | `efi` | Windows 11 requires UEFI |
| `uefi.secureBoot.enabled` | `TRUE` | needed later for VBS |
| `nvme0` | present, disk on `nvme0:0` | Windows 11 has **no in-box LSI SAS driver**. With SCSI, setup does not see the disk. |
| `ethernet*.virtualDev` | `e1000e` | the older `e1000` driver is not in-box on Windows 11 24H2 `(unverified)` |
| `vhv.enable` | **`FALSE`** | without it VBS cannot start, so **change #8 still has something to switch on**. Windows 11 turns VBS on by itself on capable hardware. |
| `tools.syncTime` | `FALSE` | a clock step is itself a logged event |
| `sound.present` | `FALSE` | one less device emitting background events |
| `mks.enable3d` | `FALSE` | removes GPU driver activity |
| `vcpu.hotadd`, `mem.hotadd` | `FALSE` | the device set must not change mid-run |

- [ ] Check the `.vmx` has no UTF-8 byte order mark. Workstation cannot parse the first line if
      it does. First three bytes must be `2E 65 6E`, not `EF BB BF`.

### 3.2 Install Windows

- [ ] **At the first setup screen, press Shift+F10 and set all four bypass values.** This is
      required, not optional. Without them setup stops with `This PC doesn't currently meet
      Windows 11 system requirements`.

```
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassTPMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassRAMCheck        /t REG_DWORD /d 1 /f
reg add HKLM\SYSTEM\Setup\LabConfig /v BypassCPUCheck        /t REG_DWORD /d 1 /f
```

- [ ] Product key screen: **"I don't have a product key"**. Edition: **Windows 11 Education**.
- [ ] Disk: **Custom: Install Windows only**. Do not create partitions by hand.
- [ ] At the sign-in screen use **Sign-in options**, then **Domain join instead**. The label is
      misleading. It joins no domain; it is the supported route to a plain local account on Pro,
      Education and Enterprise. A Microsoft account would bring OneDrive, settings sync and cloud
      telemetry, all firing on their own schedules inside your capture windows.
- [ ] Username `eli`, to match SIEM-01. **Keep the password out of the repository.** The harness
      needs it for `vmrun -gu` and `-gp`. Put it in `C:\Users\<you>\.telos\WIN-EP-01.pw`.
- [ ] Privacy screens: every toggle **off**, diagnostic data **Required only**.
- [ ] Install **VMware Tools**. Required, `vmrun` guest commands do not work without it.

### 3.3 Rename and address the machine, before installing anything else

- [ ] **Rename to `WIN-EP-01` and reboot.** The installer picks a name like `DESKTOP-14G5S5G`,
      the Wazuh agent registers by hostname, and that name then appears on every event in your
      results. Fix it before the agent exists.
- [ ] Set the time zone to **UTC**, matching SIEM-01.
- [ ] Static `10.20.10.20/24` on the VMnet2 adapter, **no gateway, no DNS, DHCP disabled**. No
      gateway means it can never become the default route. DHCP off stops it broadcasting
      requests nobody answers.
- [ ] Match adapters by **MAC address**, not by name. Names change, MACs are set in the `.vmx`.

### 3.4 Patch Windows fully, while NAT is still connected

- [ ] Use the Windows Update COM interface (`Microsoft.Update.Session`), which is built in.
      **Do not install `PSWindowsUpdate`.** It would add third-party software to the golden image
      and to the software inventory Chapter 3 must describe.
- [ ] Repeat passes until one reports `updates found: 0`.
- [ ] **Verify the reboot actually happened** before believing a zero result. Check
      `LastBootUpTime` and both pending-reboot registry keys. A pending reboot makes zero
      meaningless.
- [ ] If Windows Update ever offers a **feature update** to a newer Windows version, **do not
      take it.** That is a version change, not a patch, and your CIS and STIG control IDs are
      tied to a version.

### 3.5 Fetch every artifact to the host and hash it there

Download on the **host**, then copy into the guest. This hashes each artifact before it reaches
the endpoint, keeps download tools off the measured machine, and means Phase 5 can disconnect NAT
without breaking anything.

- [ ] Sysmon from `download.sysinternals.com`
- [ ] The Sysmon config pinned to an **exact commit**, not to a branch
- [ ] The Wazuh agent MSI **matching the manager version exactly**
- [ ] Atomic Red Team and `invoke-atomicredteam`, shallow clones, commits recorded
- [ ] `powershell-yaml`, which `Invoke-AtomicTest` cannot run without

**If the host runs antivirus, exclude the artifact folder first.** Kaspersky blocked 66 Atomic
Red Team files on this host, including three technique definitions. Without the exclusion the
pinned commit stops describing what is on the endpoint. Count the files after packing and confirm
the count matches.

### 3.6 Install Sysmon with a pinned config

```powershell
.\Sysmon64.exe -accepteula -i sysmonconfig.xml
```

- [ ] Copy that exact config into `lab/configs/` and record its SHA256 in DECISIONS.md. A Sysmon
      config change is itself a telemetry change and would silently ruin comparisons across runs.
- [ ] **Prove the sensor is using the committed file.** `Sysmon64.exe -c` prints
      `Config hash: SHA256=...`. Compare it to the file in the repo. Do not assume.
- [ ] Read the rest of that output and write down what it says is **off**. On this build it
      reports `Image loading : disabled`, meaning Sysmon Event ID 7 never appears at all.
- [ ] **Record the event channel's size and mode**:
      `Get-WinEvent -ListLog 'Microsoft-Windows-Sysmon/Operational'`. It defaults to 64 MB and
      `Circular`, which means a busy run can overwrite its own earliest events before the agent
      reads them. That is telemetry lost inside the pipeline. See OPEN-QUESTIONS item 9.

### 3.7 Install the Wazuh agent

- [ ] **Start SIEM-01 first** and confirm ports 1514 and 1515 answer. An agent installed against
      an unreachable manager completes successfully and simply never connects.
- [ ] Install with `WAZUH_MANAGER`, `WAZUH_REGISTRATION_SERVER` and `WAZUH_AGENT_NAME`.
- [ ] Add a `<localfile>` block for `Microsoft-Windows-Sysmon/Operational` with
      `<log_format>eventchannel</log_format>`. Back up the original `ossec.conf` first and record
      both hashes.
- [ ] **Check `client.keys` after starting the service, not before.** Registration happens at
      service start. Checked too early it reads 0 bytes and looks like a failure.
- [ ] Confirm `(4102): Connected to the server` in `ossec.log`.
- [ ] **Read the rest of `ossec.log` and write down every module that starts on a timer.** On
      this build: FIM synchronization every 5 minutes, FIM real time, plus SCA, rootcheck,
      syscollector and a full FIM scan all with `scan_on_start yes`. Every Phase 6 run begins with
      a revert and a boot, so those four run at the start of **every run**. That is noise from the
      measuring instrument landing in the coefficient of variation. See OPEN-QUESTIONS item 8.

### 3.8 Install Atomic Red Team at a pinned commit

Do **not** use `Install-AtomicRedTeam -getAtomics`. It downloads whatever is current and gives you
no commit to record. Clone on the host at a pinned commit and copy the files in.

- [ ] **Add an antivirus exclusion in the guest for the Atomic Red Team folder before
      extracting.** Otherwise Defender quarantines payloads once, at extraction, and those files
      are permanently absent from the golden image. You would not be studying an endpoint where
      antivirus blocks attacks; you would be studying one where an unrecorded subset of test files
      does not exist. Keep the exclusion identical in Config S and Config N so it cancels out.
- [ ] Install `powershell-yaml`. `Invoke-AtomicTest` cannot parse the atomics without it.
- [ ] **Count the extracted files** and compare to what was packed. A partial extraction is the
      failure that looks like success.
- [ ] **The pin is the commit hash plus the file count, not the archive hash.** Transfer archives
      do not preserve timestamps, so their hash changes on every repack.
- [ ] Verify with `Invoke-AtomicTest <T-number> -ShowDetailsBrief`, which reads and prints test
      definitions and executes nothing.

### 3.9 Build and verify the fence tool

A small purpose-built program that prints one line and exits. Source and build instructions are in
`lab/scripts/`.

- [ ] **Build it on the host**, copy the binary in, and pin its SHA256. Building inside the guest
      gives different bytes on every rebuild.
- [ ] **Verify it emits exactly one Sysmon Event ID 1**, and that no other event ID carries the
      run identifier. Launch it through `vmrun` directly, never through `cmd` or `powershell`,
      because those create their own processes and each is another Event ID 1.

### Phase 3 check

Run it as a miniature capture window, not as a bare command, so the harness design is exercised
too:

1. Read the archive size on SIEM-01 first, so growth is measured rather than assumed.
2. Fire the **start fence** with a unique run id.
3. Run **one** atomic test. A harmless discovery technique is enough.
4. Fire the **end fence**.
5. **Drain 120 seconds.** Per-event latency is only about 1.6 to 1.9 seconds, but the agent
   buffers and the manager writes on its own schedule.
6. On the endpoint: find both fences and count the Sysmon events between them.
7. On the manager: count lines in `archives.json` carrying the run id.

**Put the search pattern in a file and pass only the filename.** `sudo` writes every command line
to journald, Wazuh collects journald, so a pattern typed on a `sudo` line creates a new event
containing that pattern and inflates its own count. That is OPEN-QUESTIONS 1b.

**Pass condition:** two fences on the endpoint, a non-zero Sysmon count between them, and a
non-zero count in `archives.json`. **If the manager count is zero, nothing later in this runbook
will work.**

**Before starting Phase 4, write up the phase** per the rules in `CLAUDE.md`: WORKLOG, DECISIONS,
the pinned-versions table, OPEN-QUESTIONS, COMMANDS, then commit and push.

---

## Phase 4. Pin and record everything

Write all of these into `docs/DECISIONS.md` before taking any snapshot:

- [ ] Wazuh version
- [ ] Sysmon binary version and config SHA256
- [ ] Atomic Red Team commit hash
- [ ] Windows build number
- [ ] Harness git commit (once written)

A version bump partway through means every earlier run is no longer comparable and
must be discarded. This list is your defense against that.

---

## Phase 5. Snapshots

**Disconnect the NAT adapter (vmnet8) before the golden snapshot.** If the endpoint can
reach the internet during a capture, Windows Update, Defender cloud lookups, certificate
revocation checks, and time sync all fire on their own schedules. Every one of them injects
noise into the exact window you are measuring.

- [ ] Shut down WIN-EP-01 cleanly.
- [ ] **Disconnect** vmnet8. Do not remove the adapter. Leave vmnet2 as the only connected
      network.

      Disconnect rather than remove because the lab interface is the *second* adapter on
      SIEM-01 (`ethernet0` is NAT, `ethernet1` is vmnet2), and its Linux interface name
      (**`ens37`**, measured 2026-09-02, not the `ens34` originally guessed) is what the
      netplan static-IP config in Phase 2 targets. Deleting
      an adapter can renumber the remaining one and break that config. Unchecking "Connected"
      in VM settings leaves the device present and the name stable. `(unverified whether
      removal actually renumbers on this setup; disconnect is the safe choice either way)`
- [ ] Boot once, confirm no internet, shut down.
- [ ] **Turn Defender Tamper Protection OFF by hand, inside the guest, before the golden
      snapshot.** Windows Security, then Virus and threat protection, then Manage settings,
      then Tamper Protection to Off. **This cannot be done from a script.** While it is on,
      any script that tries to disable Defender fails, and Config S would be a snapshot that
      is not actually suppressed while the analysis assumes it is. See OPEN-QUESTIONS item 10.
- [ ] **Take every snapshot COLD, with the VM powered off.** Not live, not suspended. A cold
      revert boots the guest fresh and VMware sets the virtual clock from the host, so the
      clock is correct without VMware Tools touching it. A live snapshot restores a stale
      clock. All six `time.synchronize.*` switches are already `FALSE` (OPEN-QUESTIONS 6), so
      Tools will not correct it either, which is the intended behaviour and the reason cold is
      required rather than merely preferred.
- [ ] Take snapshot `golden-base`.
- [ ] Boot, apply Config S (Defender off, Windows Update off, scheduled tasks disabled),
      **then read the settings back and confirm they actually took effect**, shut down,
      snapshot `cfg-suppressed`. Never assume a `Set-MpPreference` succeeded.
- [ ] Revert to `golden-base`. Boot, leave defaults on, shut down, snapshot `cfg-natural`.

Tree you should end with:

```
WIN-EP-01
└── golden-base
    ├── cfg-suppressed     (Config S)
    └── cfg-natural        (Config N)
```

- [ ] **Delete the build checkpoints once `golden-base` exists.** Three linear checkpoints were
      taken on each VM during Phases 3 and 4, as insurance while the machines were being built:

      WIN-EP-01 : phase3-complete-2026-09-02, agent-hardened-2026-09-03, tamper-off-2026-09-03
      SIEM-01   : phase3-complete-2026-09-02, timesync-off-2026-09-03,
                  snapd-off-archive-v2-2026-09-03

      They are superseded by `golden-base` and only consume delta space after that.
      `vmrun -T ws deleteSnapshot <vmx> <name>` for each.

      **Do not delete them before `golden-base` is taken and verified.** Each one captures state
      that a revert would otherwise silently undo: Tamper Protection being off, snapd being
      disabled, the archive tool having no `truncate`, and the six `time.synchronize.*` switches.

**Do not make 16 snapshots for the 16 hardening changes.** Revert to a config snapshot and
apply the change by script instead. The script is version controlled and auditable, which is
what your reproducibility claim needs. Sixteen branching snapshot chains would also fill F:.

**Check:** `vmrun -T ws listSnapshots <path-to-vmx>` prints exactly the three above.

---

## Phase 6. The capture harness

Write this in Python on the host, in `src/`. It runs on the **Windows host, not in a VM**,
because `vmrun.exe` is local and the Wazuh API is reachable over vmnet2.

One capture window, in order:

1. `vmrun -T ws revertToSnapshot <vmx> cfg-suppressed`
2. `vmrun -T ws start <vmx> nogui`
3. Wait for VMware Tools, then **settle 180 seconds**. Boot produces an event storm.
   Do not count it.
4. Fire the **start fence**.
5. If this is a post-change run: apply the hardening change by script, reboot if needed,
   settle again.
6. Run the Atomic Red Team suite over the pinned technique list.
7. Fire the **end fence**.
8. **Drain 120 seconds.** The agent buffers and the manager writes to disk. Cutting the
   window at test completion loses the tail.
9. `vmrun -T ws stop <vmx>`
10. Over SSH to SIEM-01, **export by date and never truncate**:

    ```bash
    sudo -n /usr/local/sbin/telos-archive export YYYY-MM-DD
    ```

    It prints the `.gz` path, then `bytes_gz`, `sha256_gz` and `lines`. Copy the file to
    `data/runs/<run_id>/` and **verify it against those three values**. If the window
    crossed midnight, export **both** dates.
11. Write `data/runs/<run_id>/run_manifest.json` with every field listed in Phase 4.

### Why step 10 does not truncate

**Wazuh already rotates at the day boundary, and `archives.json` is a hard link** to the
current day's file under `YYYY/Mon/ossec-archive-DD.json`. The link count of `2` on
`archives.json` is the proof. Two things follow:

- **A run crossing midnight splits across two files.** A 67 hour batch runs overnight. Reading
  `archives.json` would export half a run and report success.
- **Truncating `archives.json` empties the dated archive too**, because it is one file with two
  names. That does not clear a scratch file, it destroys the day's permanent record.

Since nothing truncates, `telos-archive` has **no destructive subcommand at all**, so the
single sudoers rule grants the harness account read and export only. It cannot alter or delete
the evidence store. See OPEN-QUESTIONS item 14.

**Every timestamp the harness uses must come from the endpoint**, the `systemTime` or `utcTime`
inside the event, never the manager's `timestamp` field. SIEM-01's clock free-runs after Phase
5 isolation, and using it would put that drift into the results. See OPEN-QUESTIONS item 6.

Guard the harness: check free space before each run with `telos-archive disk` and on F:, and
abort cleanly if low. Running out of disk halfway through a 67 hour batch is the failure that
hurts most, and it matters more now that nothing is ever truncated.

### Three rules for the campaign, each from something measured

- **SIEM-01 must not be rebooted during a capture campaign.** Only WIN-EP-01 is reverted and
  booted per run. `snapd` makes one failed `api.snapcraft.io` lookup at each SIEM-01 boot and
  then stops, which is harmless only because it happens outside every capture window. If SIEM-01
  ever has to restart mid-campaign, note it in the manifests on either side. See
  OPEN-QUESTIONS 5.
- **Never run `agent_upgrade`, never call the upgrade API, and never click Upgrade in the Wazuh
  dashboard.** The agent-upgrade module cannot be switched off on the agent, and Wazuh never
  upgrades by itself, so the only risk is a person. **Record the agent version in every run
  manifest**, read from the agent at the start of the run, so a bump is visible in the data
  rather than assumed impossible. See OPEN-QUESTIONS 8.
- **Every timestamp comes from the endpoint.** Use `systemTime` or `utcTime` from inside the
  event, never the manager's `timestamp`. See OPEN-QUESTIONS 6.

**Check:** one full unattended run completes and produces a run folder plus a manifest, and the
copied archive matches the `sha256_gz` the export printed.

---

## Phase 7. The feasibility spike (the go/no-go gate)

Do not build Tier B. Do not write the analysis engine yet. Answer two questions.

**Q1. What is the run to run coefficient of variation?**
Run the identical suite 5 times against the same restored snapshot with zero config change.
Do it under Config S and again under Config N. Compute CoV per event type. Save to
`data/summaries/cov_control_runs.csv`.

- CoV above zero under Config N: the statistics layer is justified in the lab, and naive
  differencing will produce measurable false positives. T1's headline result exists.
- CoV near zero under both: the statistics layer buys nothing in the lab. T1's proposal
  already commits to reporting that honestly, but a panel will read it as a null result.

**Q2. What is the real wall clock per run?**
Time 5 unattended end to end runs. Multiply by 101. Save to `data/summaries/run_timings.csv`.
101 runs at 40 minutes is about 67 hours. That works overnight and on weekends only if the
harness is fully unattended. Semi-automated, it does not finish before the defense.

- [ ] Record both answers in `docs/DECISIONS.md`.
- [ ] Make the T1 versus T3 call and write down the reason.

---

## Phase 8. T2 and T3 environment (no lab needed)

Both are offline static analysis. No SIEM, no log ingestion, no network during analysis.
Under 10 GB total. Runs on a laptop.

- [ ] WSL2 Ubuntu, or just the Windows host with Python 3.11+.
- [ ] `pip install lxml pyyaml networkx scikit-learn pandas`
- [ ] Clone the corpora and **pin each to a named commit**, then record the hashes in
      `docs/DECISIONS.md` and in the paper:

```bash
git clone https://github.com/wazuh/wazuh.git
git clone https://github.com/SigmaHQ/sigma.git
```

Pinning is not optional. Both repos change weekly. An unpinned corpus means your numbers
cannot be reproduced by anyone, including you. T3's own literature review cites sigmalint
pinning commit `994da16` for exactly this reason.

- [ ] Optional: one Wazuh VM to spot check T2 findings with `wazuh-logtest`. Not needed
      for the analysis itself.

---

## If something breaks

| Symptom | Most likely cause |
|---|---|
| `vmrun` guest commands fail | VMware Tools not installed, or wrong guest credentials |
| No events in `archives.json` | `logall_json` not set, or manager not restarted |
| Agent shows disconnected | Static IP wrong, or vmnet2 has DHCP still on |
| F: fills mid batch | Archives not truncated after each run (Phase 6 step 10) |
| Counts drift between runs | Something updated. Check the Phase 4 pin list |
| Credential Guard change fails | Nested virtualization not enabled. See OPEN-QUESTIONS.md |
