"""Read Wazuh's archive into event-key counts for one capture window.

Wazuh writes every event it receives to `archives.json` on SIEM-01, one JSON
object per line (`logall_json`, CLAUDE.md rule 3). This module turns those lines
into the input the analyser takes: one count per event key for one capture
window, and then a Phase of several windows.

Three rules shape it.

1. **The window is cut on the events' own time.** A run starts and ends with a
   `telos-fence.exe START <run_id>` and `END <run_id>` process (a Sysmon event 1,
   blueprint section 6). The reader takes every event of the agent whose own
   time (`systemTime`, the guest's clock) lies between those two, in any line
   order. The host clock and the order lines arrive in play no part (CLAUDE.md
   rule 5).
2. **A missing or doubled fence is an error.** A capture that died before its END
   fence must not be read as a short run, because a short run looks like loss.
3. **Wazuh's field names are matched to the key map.** Wazuh writes Windows field
   names with a small first letter (`logonType`, `grantedAccess`); the key map in
   eventkey.py uses the Windows names (`LogonType`, `GrantedAccess`). The reader
   raises the first letter. This matches every field seen in the archive on
   2026-11-13; it is not documented by Wazuh (OPEN-QUESTIONS 32, point 3).

The fence events themselves fall inside the window and are counted. They are the
same in every run, so they cancel out.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable

from .eventkey import KeyBuilder
from .model import Phase

# Windows event channel -> the source name used in event keys.
SOURCE_BY_CHANNEL = {
    "Security": "Security",
    "Microsoft-Windows-Sysmon/Operational": "Sysmon",
    "Microsoft-Windows-PowerShell/Operational": "PowerShell",
}

FENCE_IMAGE = "telos-fence.exe"

_TIME = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?Z?$")


def event_time(text: str) -> datetime:
    """Parse a Windows `systemTime` such as 2026-11-13T08:28:10.1623743Z.

    Windows gives 7 digits after the second; Python keeps 6, so the last digit
    (a tenth of a microsecond) is dropped. That cannot move an event across a
    fence written by a separate process.
    """
    m = _TIME.match(text.strip())
    if not m:
        raise ValueError(f"not a Windows event time: {text!r}")
    base = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
    digits = (m.group(2) or "")[:6].ljust(6, "0")
    return base + timedelta(microseconds=int(digits))


def read_lines(lines: Iterable[str]) -> tuple[list[dict], int]:
    """Parse archive lines and keep the Windows events.

    Returns (records, broken). A broken line is one that is not valid JSON, for
    example a line cut off while Wazuh was still writing it; the caller should
    report the count. Blank lines and lines that are not Windows events (SIEM-01's
    own logs) are dropped without counting.
    """
    records: list[dict] = []
    broken = 0
    for raw in lines:
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            broken += 1
            continue
        system = rec.get("data", {}).get("win", {}).get("system")
        if isinstance(system, dict) and system.get("eventID") and system.get("systemTime"):
            records.append(rec)
    return records, broken


def _windows_names(eventdata: dict) -> dict[str, object]:
    """Wazuh's field names (`logonType`) as Windows names (`LogonType`)."""
    return {(k[:1].upper() + k[1:]): v for k, v in eventdata.items()}


def key_for(record: dict, builder: KeyBuilder | None = None) -> str:
    """The event key for one archive record."""
    builder = builder or KeyBuilder()
    system = record["data"]["win"]["system"]
    channel = system.get("channel", "")
    source = SOURCE_BY_CHANNEL.get(channel, channel)
    fields = _windows_names(record["data"]["win"].get("eventdata", {}) or {})
    return builder.build_str(source, system["eventID"], fields)


def _agent(record: dict) -> str:
    return record.get("agent", {}).get("name", "")


def _fences(records: list[dict], word: str, run_id: str) -> list[dict]:
    """The fence events `telos-fence.exe <word> <run_id>`."""
    tail = re.compile(rf"(?:^|\s){word}\s+{re.escape(run_id)}\s*$")
    found = []
    for rec in records:
        system = rec["data"]["win"]["system"]
        if SOURCE_BY_CHANNEL.get(system.get("channel", "")) != "Sysmon" or str(system["eventID"]) != "1":
            continue
        data = rec["data"]["win"].get("eventdata", {}) or {}
        image = str(data.get("image", "")).replace("\\", "/").lower()
        if image.endswith(FENCE_IMAGE) and tail.search(str(data.get("commandLine", ""))):
            found.append(rec)
    return found


def _one_fence(records: list[dict], word: str, run_id: str) -> dict:
    found = _fences(records, word, run_id)
    if not found:
        raise ValueError(f"no {word} fence for run {run_id!r}")
    if len(found) > 1:
        raise ValueError(f"{len(found)} {word} fences for run {run_id!r}; a run id must be used once")
    return found[0]


@dataclass
class WindowCounts:
    """One capture window, counted."""

    run_id: str
    agent: str
    start: str                 # the START fence's systemTime, as Windows wrote it
    end: str                   # the END fence's systemTime
    counts: dict[str, int] = field(default_factory=dict)
    broken_lines: int = 0      # lines that were not valid JSON, in the whole input

    @property
    def n_events(self) -> int:
        return sum(self.counts.values())


def count_window(lines: Iterable[str], agent: str, run_id: str,
                 builder: KeyBuilder | None = None) -> WindowCounts:
    """Count every event of `agent` between the START and END fences of `run_id`."""
    builder = builder or KeyBuilder()
    records, broken = read_lines(lines)
    mine = [r for r in records if _agent(r) == agent]
    start_rec = _one_fence(mine, "START", run_id)
    end_rec = _one_fence(mine, "END", run_id)
    start_text = start_rec["data"]["win"]["system"]["systemTime"]
    end_text = end_rec["data"]["win"]["system"]["systemTime"]
    start, end = event_time(start_text), event_time(end_text)
    if end < start:
        raise ValueError(f"run {run_id!r}: END fence ({end_text}) is before START ({start_text})")

    counts: dict[str, int] = {}
    for rec in mine:
        t = event_time(rec["data"]["win"]["system"]["systemTime"])
        if start <= t <= end:
            k = key_for(rec, builder)
            counts[k] = counts.get(k, 0) + 1
    return WindowCounts(run_id=run_id, agent=agent, start=start_text, end=end_text,
                        counts=counts, broken_lines=broken)


def to_phase(name: str, windows: list[WindowCounts], window_minutes: float) -> Phase:
    """Put several windows of one phase together.

    A key seen in some windows and not others gets a 0 for the others, so every
    key carries one count per window, which Phase.validate() requires.
    `window_minutes` is the pinned window length from the run manifest, the same
    for every window of a comparison.
    """
    keys = sorted({k for w in windows for k in w.counts})
    counts = {k: [w.counts.get(k, 0) for w in windows] for k in keys}
    return Phase(name=name, counts=counts, window_minutes=window_minutes)
