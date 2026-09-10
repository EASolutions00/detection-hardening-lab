# UWF test session prompt

Paste this whole file into a new chat. Select all, copy, paste. Nothing needs trimming.

This is for **one job only**: testing whether the Unified Write Filter can replace snapshot
restore, which is OPEN-QUESTIONS item 19. When that item closes, this prompt is finished with.

It does not repeat the project map. It tells the model to read it. Two copies would drift.

There are no tables in this file on purpose, so it survives being copied from any view.


## What this session is

A **working session**, not a question-and-answer session. You will run commands, change a virtual
machine, and record what happened.

`REPO\docs\PROMPT-new-chat.md` says the session is read only. **This session overrides that**, but
only for the things listed under "What you may do" below. Everything else in that file still
applies, including the routing list, the settled numbers, and the rule that a document is never
evidence about another document.


## 0. Paths

```
REPO = E:\Claude general
DOCS = E:\Elijah MASTER COPY DO NOT DELETE\Documents\New folder (5)
VMRUN = C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe
WIN_EP = F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx
SIEM = F:\TeLoS Homelab\SIEM-01\SIEM-01.vmx
```

Guest login for WIN-EP-01 is user `eli`. The password is read from a file, never typed:

```
$pw = Get-Content "$env:USERPROFILE\.telos\WIN-EP-01.pw" -Raw
```

**Never print that password, never echo it, never put it in a commit, a log entry, or a chat
message.** The `.telos` folder is outside the repository on purpose.


## 1. Read before touching anything

1. `REPO\docs\PROMPT-new-chat.md`
   The project map. Read the whole file. Ignore only its read-only rule, which this session
   replaces.

2. `REPO\docs\OPEN-QUESTIONS.md`, **item 19**, in full.
   This is the actual task. It explains what UWF is, the two jobs it would do, the six ways it
   breaks, and what changes depending on the result. **Do not work from the summary below.
   Read the item.**

3. `REPO\docs\WORKLOG.md`, the newest two entries.

Then run:

```
git -C "E:\Claude general" log --oneline -5
```

Then tell me in four lines: what item 19 asks, which step you would run first, what a pass looks
like, and what a failure would mean. Then stop and wait for my go-ahead.


## 2. The sequence, one line each

The full detail is in item 19. This is only the order.

Step 1. Does the UWF feature exist on this build.
Step 2. Does it enable on unactivated Windows.
Step 3. Does a write made before a reboot actually disappear after it.
Step 4. Does servicing mode let a registry change survive a reboot.
Step 5. Does one full capture run without UWF writing Event ID 2.
Step 6. Does UWF change what Sysmon logs, compared to UWF off.

**Stop at the first failure.** Each step can end the item. Do not run step 4 to see what happens
if step 3 failed.

**Widen the search string in step 1** to `*Filter*`, not `*WriteFilter*`. A narrow search that
returns nothing reads as "not available" when it may mean "wrong search string".


## 3. What you may do

- Run `vmrun` from the host: `list`, `snapshot`, `revertToSnapshot`, `start`, `stop`,
  `runProgramInGuest`, `listSnapshots`.
- Run commands inside WIN-EP-01, including `uwfmgr`, `dism`, and PowerShell.
- Restart WIN-EP-01. The test needs reboots.
- Create snapshots whose names begin with `uwf-test-`.
- Edit `REPO\docs\WORKLOG.md`, `REPO\docs\OPEN-QUESTIONS.md`, `REPO\docs\DECISIONS.md`.
- `git add`, `git commit`, `git push` for those three files.


## 4. What you may not do

- **Do not delete or overwrite these snapshots.** They are project milestones, not test scratch:
  WIN-EP-01: `phase3-complete-2026-09-02`, `agent-hardened-2026-09-03`, `tamper-off-2026-09-03`
  SIEM-01: `phase3-complete-2026-09-02`, `timesync-off-2026-09-03`, `snapd-off-archive-v2-2026-09-03`
- **Do not edit** `REPO\src\`, `REPO\tests\`, or `REPO\thesis\T1\figures\`. Nothing in this test
  touches the analyser or the diagrams.
- **Do not edit the proposal documents in DOCS.** Item 19 says what changes if the test passes.
  That is a separate decision I will make after seeing the result.
- **Never run** `git-filter-repo`, a force push, or any history rewrite.
- **Do not change SIEM-01 at all.** It is only running so telemetry keeps flowing for step 5.


## 5. Before the first change to the VM

Take a fallback snapshot, and tell me before you do:

```
& "C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe" -T ws snapshot "F:\TeLoS Homelab\WIN-EP-01\WIN-EP-01.vmx" "uwf-test-baseline-2026-09-10"
```

Correct result: no output. `vmrun` prints nothing on success.

**Why a new one rather than reusing `tamper-off-2026-09-03`.** That snapshot is a project
milestone. If a UWF step leaves the machine unbootable, reverting to a milestone mixes test
wreckage with real progress and you lose the ability to tell them apart.


## 6. How to run each step

Explain every command before running it, including read-only ones: what it does in plain words,
why it is needed at this point, where it runs (host, or inside WIN-EP-01, and whether admin), what
a correct result looks like as actual text, what failure looks like, how to undo it, and whether
it is safe to run again.

**Say which commands are mine to run and which are yours.** Anything needing an interactive
administrator PowerShell inside the guest is mine.

**After each step, before moving on, tell me three things:** what the output actually said, what
that proves, and whether the item continues or stops.


## 7. Recording

After each step that produces a real result, append to `REPO\docs\WORKLOG.md`. Include the exact
command and the exact output, not a summary of it. A failed step recorded with its error text is
worth more later than a clean description.

When the item finishes, whether it passes or fails:

- Move item 19 to the Answered section of `OPEN-QUESTIONS.md` with the evidence.
- If it passes, add an entry to `DECISIONS.md` recording that a write filter is an accepted
  alternative to snapshot restore, with the reason and the cost if wrong.
- If it fails, record which step failed and why, so nobody retries it in three weeks.
- Then commit and push, so the record is not on one disk only.


## 8. Two things I care about most

**Step 5 matters more than the rest.** If the overlay fills during a capture, UWF writes
Event ID 2 and the run is corrupt while the numbers still look normal. Nothing in the pipeline
currently looks for that event. A silently bad run producing believable output is the exact
failure this whole thesis is about, so finding it here would be a real result.

**Step 2 is the likeliest quiet killer.** `DECISIONS.md:326` records this Windows as Education,
**unactivated**. Whether a DISM optional feature will enable in that state is unverified. Check it
early rather than after an afternoon on the later steps.


## 9. Start

Do section 1. Give me the four lines. Then stop and wait for my go-ahead.
