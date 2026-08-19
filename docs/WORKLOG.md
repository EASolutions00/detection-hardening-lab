# Work Log

What actually happened, session by session. Newest at the top.

This exists because you forget things. Write an entry every time you sit down, even a short
one. "Tried X, it failed, here is the error" is worth more later than a clean summary.

Template:

```
## YYYY-MM-DD - short title
Did:
Result:
Broke / stuck on:
Next:
```

---

## 2026-08-19 - Reply rules made global

**Did:** Created `C:\Users\Elijah\.claude\CLAUDE.md` holding the full AI rules.

**Why:** The rules were only applying because they were pasted at the start of each chat.
Nothing loaded them automatically. `~/.claude/CLAUDE.md` did not exist, there was no
`settings.json`, no output style, and the memory directory was empty. The project CLAUDE.md
only *linked* to `docs/AI-RULES.txt`, and a link is not a load.

**Result:** Rules now load automatically in every project and every session on this machine.
No more pasting.

**Note for later:** that file is **outside this repo**, so git does not back it up and it will
not follow you to another machine. `docs/AI-RULES.txt` is the versioned copy. Verified the two
are identical apart from a trailing newline. If you edit one, edit both.

---

## 2026-08-19 - CLAUDE.md reviewed and trimmed

**Did:** Reviewed `CLAUDE.md` as an index rather than a document. Cut it from 140 lines to
104. Removed detail that duplicated the runbook (the reasoning behind the silent-failure
rules, the spike Q1/Q2 breakdown), the restated voice rules, and a filler `git status` block.
Created `thesis/README.md` to hold the institutional template and the problem-to-objective
numbering rule, which previously had no home outside `CLAUDE.md`.

**Result:** All 12 internal links verified as resolving. Nothing was lost, only relocated.

**Fixed while reviewing:**
- `CLAUDE.md` said the repo is private on GitHub. It is not. `git remote -v` is empty, no
  GitHub repo exists yet. Now reads "will be created private".
- "end of September" had no year. Now says September 2026.
- "gh is not installed" removed from `CLAUDE.md`. That is machine state, not project state,
  and it is already recorded in this log below.

**Kept deliberately:** the five silent-failure rules stay in `CLAUDE.md` instead of becoming
a pointer. They have to be loaded before deciding which file to read, otherwise a VM ends up
on E: without the runbook ever being opened.

**Next:** unchanged from the entry below.

---

## 2026-08-19 - Repo structure created

**Did:** Turned the folder into an organized git repo. Created `docs/`, `thesis/`, `lab/`,
`src/`, `data/`. Moved the four original documents into place. Wrote `CLAUDE.md` as the
index, `docs/RUNBOOK-homelab.md` as the from-scratch build procedure, and this log.

**Result:** Structure is in place. Nothing about the lab or the thesis has been built yet.
The four source documents are unchanged in content, only moved.

**Broke / stuck on:** `gh` (GitHub CLI) is not installed on this machine, so the repo cannot
be created from the terminal yet. Either install it or create the repo in the browser.

**Next:**
1. Answer the T3 SigmaHQ annotation count question. See `docs/OPEN-QUESTIONS.md`.
   It is offline, takes minutes, and it gates your only fallback.
2. Start Phase 0 of the runbook.
3. Create the private GitHub repo and push.

---

## 2026-08-18 - Source documents written (before this log existed)

**Did:** Wrote the three thesis proposals (T1, T2, T3) and the homelab blueprint.

**Result:** All four are in `thesis/` and `lab/blueprint.md` now.

**Next:** Was superseded by the 2026-08-19 session above.
