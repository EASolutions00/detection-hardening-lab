---
name: phase-closeout
description: Closes a completed phase of docs/RUNBOOK-homelab.md by updating WORKLOG, DECISIONS, OPEN-QUESTIONS, STATUS and the pinned-versions table, then committing and pushing. Use this every time a runbook phase is finished, or the user says a phase is done or asks to start the next phase, even if the phase felt small.
---

# Phase closeout

Do all of this before starting the next phase. The record is the point, not the memory.
Explain each command before running it, as the global rules say.

1. **WORKLOG.md (always).** Add an entry, newest first: which phase, what was done, the
   results, and anything that broke with its exact error text. Take the date from
   `git log`, not from file timestamps.
2. **DECISIONS.md (if a choice was made).** Record any hard-to-reverse choice or any
   pinned value set during the phase, with the reason and the cost if wrong. Never delete
   an entry. Supersede it.
3. **OPEN-QUESTIONS.md (if it applies).** Move any answered question to the Answered
   section with the evidence. Add any new unknown the phase revealed.
4. **Pinned-versions table in DECISIONS.md** if the phase produced a version or hash to
   pin (Phase 4 especially).
5. **STATUS.md.** Update the blockers and dates if the phase changed them. Update
   "Last updated".
6. **Commit and push.** So the record is on GitHub, not on one disk only.
   Correct result: `git status` shows "nothing to commit, working tree clean" and
   "Your branch is up to date with 'origin/main'" (or the current branch name).
7. **Defense brief.** A finished phase gets a full brief. Use the `defense-brief` skill.

Before step 6, show me the list of files changed and what changed in each, in one line
per file.
