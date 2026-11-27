"""Evidence for K1's sign-in and C3's block that uses neither the tool's findings nor the detection rules.

    .venv/Scripts/python.exe src/independent_evidence.py --summary data/summaries/eval-2026-11-26/independent-evidence.txt

Why. EXPECTED-RESULTS section 7 calls K1 a blind spot (the attack still worked: the Remote Desktop sign-in opened a
session, although no logon event was written) and C3 prevention (the LSASS dump was attempted and failed). An outside
review (WORKLOG 2026-11-27, point 3) found the first proofs weak: K1's rested on Security-4672[] staying the same, and
C3's on the detection rules that stopped, which is circular. This script checks both claims in the raw events of all
26 evaluation runs.

What it reads. Each run's archive export in data/runs/<run>/, and only WIN-EP-01's events inside the run's own capture
window (record.window in run_manifest.json). It checks that it finds as many events in each window as the harness
recorded. It writes nothing except the --summary file, if one is given.

The sign-in (K1). Where 4624 is still written, the sign-in writes two linked type 10 logons for eli, and the programs of
a new Remote Desktop session (rdpclip.exe, the clipboard program; userinit.exe; explorer.exe) start under the logon ID
of one of them. So these programs mark this sign-in, and not the harness's own guest logons (type 4, by vmtoolsd.exe;
OPEN-QUESTIONS 26). Sysmon writes them whatever the audit policy says, so in K1 they show whether the sign-in opened a
session.

The dump (C3). For each of the three LSASS tests: did its program start (Sysmon 1), did it open lsass.exe (Sysmon 10),
and was its dump file written (Sysmon 11)?
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNS = REPO / "data" / "runs"
GROUPS = {"control": [f"eval-ctl-{i}" for i in range(1, 6)], "before": [f"eval-pre-{i}" for i in range(1, 4)]}
GROUPS.update({case: [f"eval-post-{case}-{i}" for i in range(1, 4)] for case in ("C1", "C3", "C5", "K1", "K2", "K3")})
SYSMON = "Microsoft-Windows-Sysmon/Operational"
SESSION_PROGRAMS = ("rdpclip.exe", "userinit.exe", "explorer.exe")
HOST_IP = "10.20.10.1"     # the lab host, where the Remote Desktop client runs


def norm(path: str | None) -> str:
    """The archive doubles some backslashes; keep one per separator."""
    return re.sub(r"\\+", r"\\", path or "")


def base(path: str | None) -> str:
    return norm(path).split("\\")[-1].lower()


def when(stamp: str) -> datetime:
    """'2026-11-26T19:43:15.1234567Z' to a datetime, to the microsecond."""
    return datetime.strptime(stamp[:26], "%Y-%m-%dT%H:%M:%S.%f")


def window_events(run_id: str) -> tuple[list[dict], dict]:
    """WIN-EP-01's events inside the run's capture window, and the run record."""
    record = json.loads((RUNS / run_id / "run_manifest.json").read_text(encoding="utf-8"))["record"]
    start, end = record["window"]["start"], record["window"]["end"]
    out = []
    for gz in sorted((RUNS / run_id).glob("archive-*.json.gz")):
        with gzip.open(gz, "rt", encoding="utf-8") as fh:
            for line in fh:
                if "WIN-EP-01" not in line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("agent", {}).get("name") != "WIN-EP-01":
                    continue
                s = r.get("data", {}).get("win", {}).get("system", {})
                t = s.get("systemTime")
                if s.get("eventID") and t and start <= t <= end:
                    out.append(r)
    return out, record


def parts(r: dict) -> tuple[str, str, str, dict]:
    s = r["data"]["win"]["system"]
    return s.get("channel", ""), s.get("eventID", ""), s["systemTime"], r["data"]["win"].get("eventdata", {})


def sign_in(events: list[dict], start: str) -> dict:
    """The sign-in's traces: its type 10 logons, the session programs, and where each 4672 comes from."""
    logons: dict[str, tuple] = {}
    n4624 = 0
    type10: list[str] = []
    programs: dict[str, list[dict]] = {p: [] for p in SESSION_PROGRAMS}
    s4672: list[str] = []
    for r in events:
        chan, eid, t, d = parts(r)
        if chan == "Security" and eid == "4624":
            n4624 += 1
            lid = (d.get("targetLogonId") or "").lower()
            logons[lid] = (d.get("logonType"), base(d.get("processName")), d.get("ipAddress"))
            if d.get("logonType") == "10":
                type10.append(lid)
        elif chan == "Security" and eid == "4672":
            s4672.append((d.get("subjectLogonId") or "").lower())
        elif chan == SYSMON and eid == "1" and base(d.get("image")) in programs:
            programs[base(d.get("image"))].append({
                "t": t, "user": norm(d.get("user")).split("\\")[-1], "session": d.get("terminalSessionId"),
                "logon": (d.get("logonId") or "").lower()})
    kinds = Counter()
    for lid in s4672:
        if lid == "0x3e7":
            kinds["SYSTEM"] += 1
        elif lid not in logons:
            kinds["not linkable"] += 1
        else:
            ltype, proc, ip = logons[lid]
            if ltype == "10" or (ltype == "3" and ip == HOST_IP) or (ltype == "2" and proc == "winlogon.exe"):
                kinds["sign-in"] += 1        # its logons, and the new session's window manager and font driver
            elif ltype == "4" and proc == "vmtoolsd.exe":
                kinds["harness"] += 1        # the harness's own guest calls (OPEN-QUESTIONS 26)
            else:
                kinds["other"] += 1
    found = [p[0] for p in programs.values() if len(p) == 1]
    once = len(found) == len(SESSION_PROGRAMS)
    same = once and len({p["logon"] for p in found}) == 1
    return {
        "n4624": n4624,
        "type10": type10,
        "counts": [len(programs[p]) for p in SESSION_PROGRAMS],
        "once": once,
        "session": ",".join(sorted({p["session"] for p in found})) if found else "-",
        "user": ",".join(sorted({p["user"] for p in found})) if found else "-",
        "same_logon": same,
        "linked": (same and found[0]["logon"] in type10) if type10 else None,
        "seconds": (when(programs["rdpclip.exe"][0]["t"]) - when(start)).total_seconds() if programs["rdpclip.exe"] else None,
        "s4672": (len(s4672), kinds),
    }


def dump(events: list[dict]) -> Counter:
    """For each LSASS test: its program started, its lsass.exe accesses, its file written. And all Sysmon 11 files."""
    c = Counter()
    for r in events:
        chan, eid, _t, d = parts(r)
        if chan != SYSMON:
            continue
        img = base(d.get("image"))
        if eid == "1":
            c["procdump start"] += img == "procdump.exe"
            c["helper start"] += img == "procdump64.exe"
            c["comsvcs start"] += img == "rundll32.exe" and "comsvcs" in (d.get("commandLine") or "").lower()
            c["rdrleakdiag start"] += img == "rdrleakdiag.exe"
        elif eid == "10" and base(d.get("targetImage")) == "lsass.exe":
            src = base(d.get("sourceImage"))
            c["procdump lsass"] += src in ("procdump.exe", "procdump64.exe")
            c["comsvcs lsass"] += src == "rundll32.exe"
            c["rdrleakdiag lsass"] += src == "rdrleakdiag.exe"
        elif eid == "11":
            f = norm(d.get("targetFilename")).lower()
            c["files"] += 1
            c["procdump file"] += f.endswith("\\windows\\temp\\lsass_dump.dmp")
            c["helper file"] += bool(re.search(r"\\pdm[0-9a-f]+\.tmp\\procdump64\.exe$", f))
            c["comsvcs file"] += f.endswith("\\lsass-comsvcs.dmp")
            c["rdrleakdiag file"] += "\\t1003.001-13-rdrleakdiag\\" in f
    return c


def lsass_sources(events: list[dict]) -> Counter:
    c = Counter()
    for r in events:
        chan, eid, _t, d = parts(r)
        if chan == SYSMON and eid == "10" and base(d.get("targetImage")) == "lsass.exe":
            c[(base(d.get("sourceImage")), d.get("grantedAccess"))] += 1
    return c


def procdump_order(events: list[dict]) -> list[str]:
    rows = []
    for r in events:
        chan, eid, t, d = parts(r)
        if chan != SYSMON:
            continue
        img, src = base(d.get("image")), base(d.get("sourceImage"))
        if eid == "1" and img in ("procdump.exe", "procdump64.exe"):
            rows.append((t, f"Sysmon 1   {img} starts"))
        elif eid == "10" and src in ("procdump.exe", "procdump64.exe") and base(d.get("targetImage")) == "lsass.exe":
            rows.append((t, f"Sysmon 10  {src} opens lsass.exe (access {d.get('grantedAccess')})"))
        elif eid == "11" and img in ("procdump.exe", "procdump64.exe"):
            rows.append((t, f"Sysmon 11  {img} writes {norm(d.get('targetFilename'))}"))
    return [f"  {t[11:23]}  {what}" for t, what in sorted(rows)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Evidence for K1's sign-in and C3's block from the raw events.")
    ap.add_argument("--summary", help="also write the output to this file")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lines: list[str] = []

    def say(text: str = "") -> None:
        print(text)
        lines.append(text)

    runs = [r for g in GROUPS.values() for r in g]
    case_of = {r: g for g, rs in GROUPS.items() for r in rs}
    data = {}
    for run in runs:
        events, record = window_events(run)
        data[run] = {"events": events, "record": record, "sign_in": sign_in(events, record["window"]["start"]),
                     "dump": dump(events), "lsass": lsass_sources(events)}

    say("INDEPENDENT EVIDENCE, evaluation runs of 2026-11-26 (src/independent_evidence.py)")
    say("It uses no finding of the tool and no detection rule: only the raw Security and Sysmon events in each")
    say("run's own capture window.")
    say()
    say("WINDOWS (events found against the count in the run record)")
    bad = [r for r in runs if len(data[r]["events"]) != data[r]["record"]["window"]["n_events"]]
    say(f"  the same count in {len(runs) - len(bad)} of {len(runs)} runs" + (f"; differ: {', '.join(bad)}" if bad else ""))
    if bad:
        raise SystemExit("the windows do not match the run records; nothing else was computed")
    say()

    say("A. THE SIGN-IN (the first step of every run: Remote Desktop from the host)")
    say("  type 10 = 4624 logons of type 10; programs = Sysmon 1 starts of rdpclip, userinit, explorer;")
    say("  in type 10 = the programs' logon ID is one of the type 10 logon IDs; s = seconds from the window start to")
    say("  rdpclip; 4672 = total: sign-in + harness + SYSTEM + other + not linkable (no 4624 to link to)")
    say(f"  {'run':<16} {'type 10':>7}  {'programs':>8}  {'session':>7}  {'user':<5} {'in type 10':<10} {'s':>5}   4672")
    for run in runs:
        si = data[run]["sign_in"]
        n, k = si["s4672"]
        linked = "-" if si["linked"] is None else ("yes" if si["linked"] else "NO")
        secs = f"{si['seconds']:.1f}" if si["seconds"] is not None else "-"
        say(f"  {run:<16} {len(si['type10']):>7}  {' '.join(map(str, si['counts'])):>8}  {si['session']:>7}  "
            f"{si['user']:<5} {linked:<10} {secs:>5}   {n} = {k['sign-in']} + {k['harness']} + {k['SYSTEM']} + "
            f"{k['other']} + {k['not linkable']}")
    say()

    say("B. THE DUMP (the three LSASS tests: started = Sysmon 1, lsass = Sysmon 10 into lsass.exe, file = Sysmon 11)")
    say(f"  {'':<16} {'ProcDump (test 1)':<24} {'comsvcs (test 2)':<18} {'rdrleakdiag (test 13)':<22} all")
    say(f"  {'run':<16} {'start':>5} {'lsass':>5} {'file':>5} {'helper':>6}  {'start':>5} {'lsass':>5} {'file':>5}  "
        f"{'start':>5} {'lsass':>5} {'file':>5}  {'files':>5}")
    for run in runs:
        c = data[run]["dump"]
        say(f"  {run:<16} {c['procdump start']:>5} {c['procdump lsass']:>5} {c['procdump file']:>5} {c['helper file']:>6}  "
            f"{c['comsvcs start']:>5} {c['comsvcs lsass']:>5} {c['comsvcs file']:>5}  "
            f"{c['rdrleakdiag start']:>5} {c['rdrleakdiag lsass']:>5} {c['rdrleakdiag file']:>5}  {c['files']:>5}")
    say()

    others = [r for r in runs if case_of[r] != "C3"]
    c3 = GROUPS["C3"]
    say("C. SYSMON 10 INTO lsass.exe, by source program and access, mean per run")
    say(f"  {'source':<26} {'access':<10} {f'{len(others)} runs without C3':>20} {'3 C3 runs':>10}")
    total_o, total_c = Counter(), Counter()
    for r in others:
        total_o.update(data[r]["lsass"])
    for r in c3:
        total_c.update(data[r]["lsass"])
    for (src, acc) in sorted(set(total_o) | set(total_c), key=lambda x: -(total_o[x] + total_c[x])):
        say(f"  {src:<26} {acc or '-':<10} {total_o[(src, acc)] / len(others):>20.1f} {total_c[(src, acc)] / len(c3):>10.1f}")
    say(f"  {'all':<26} {'':<10} {sum(total_o.values()) / len(others):>20.1f} {sum(total_c.values()) / len(c3):>10.1f}")
    say()

    say("D. PROCDUMP'S ORDER in eval-pre-1 (why its helper is missing when procdump.exe cannot open lsass.exe)")
    for row in procdump_order(data["eval-pre-1"]["events"]):
        say(row)
    say()

    k1 = GROUPS["K1"]
    not_k1 = [r for r in runs if case_of[r] != "K1"]
    si = {r: data[r]["sign_in"] for r in runs}
    du = {r: data[r]["dump"] for r in runs}
    say("SUMMARY")
    say(f"  the session programs started once each, in one logon session, in session 2, as eli: "
        f"{sum(si[r]['once'] and si[r]['same_logon'] and si[r]['session'] == '2' and si[r]['user'] == 'eli' for r in runs)}"
        f" of {len(runs)} runs")
    say(f"  two type 10 logons: {sum(len(si[r]['type10']) == 2 for r in not_k1)} of {len(not_k1)} runs without K1; "
        f"no 4624 at all: {sum(si[r]['n4624'] == 0 for r in k1)} of {len(k1)} K1 runs")
    say(f"  the programs' logon ID is a type 10 logon ID: {sum(bool(si[r]['linked']) for r in not_k1)} of {len(not_k1)} "
        f"runs that have type 10 logons")
    say(f"  all three test programs started: "
        f"{sum(du[r]['procdump start'] > 0 and du[r]['comsvcs start'] > 0 and du[r]['rdrleakdiag start'] > 0 for r in runs)}"
        f" of {len(runs)} runs")
    say(f"  each test program opened lsass.exe: "
        f"{sum(du[r]['procdump lsass'] > 0 and du[r]['comsvcs lsass'] > 0 and du[r]['rdrleakdiag lsass'] > 0 for r in others)}"
        f" of {len(others)} runs without C3; any of them, in C3: "
        f"{sum(du[r]['procdump lsass'] + du[r]['comsvcs lsass'] + du[r]['rdrleakdiag lsass'] > 0 for r in c3)} of {len(c3)}")
    say(f"  both dump files written: {sum(du[r]['procdump file'] > 0 and du[r]['comsvcs file'] > 0 for r in others)} of "
        f"{len(others)} runs without C3; either, in C3: "
        f"{sum(du[r]['procdump file'] + du[r]['comsvcs file'] > 0 for r in c3)} of {len(c3)}")
    say(f"  ProcDump's helper written: {sum(du[r]['helper file'] > 0 for r in others)} of {len(others)} runs without C3; "
        f"in C3: {sum(du[r]['helper file'] > 0 for r in c3)} of {len(c3)}")
    say(f"  rdrleakdiag's output seen by Sysmon 11: {sum(du[r]['rdrleakdiag file'] > 0 for r in runs)} of {len(runs)} runs")
    say(f"  other files written in the C3 runs (Sysmon 11 still works): {', '.join(str(du[r]['files']) for r in c3)}")

    if a.summary:
        out = Path(a.summary)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
