"""Tests for the archive reader: Wazuh archive lines in, event-key counts out.

The lines below have the shape of real lines from SIEM-01's archives.json
(read 2026-11-13), cut down to the parts the reader uses. Wazuh writes Windows
field names with a small first letter (logonType), and the key map uses the
Windows names (LogonType), so the reader must translate.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.archive import count_window, key_for, read_lines, to_phase

AGENT = "WIN-EP-01"


def line(channel: str, event_id: str, time: str, eventdata: dict, agent: str = AGENT) -> str:
    """One archive line in Wazuh's shape."""
    return json.dumps({
        "timestamp": "2026-11-13T08:30:00.000+0000",
        "agent": {"id": "001", "name": agent},
        "data": {"win": {
            "system": {"channel": channel, "eventID": event_id, "systemTime": time},
            "eventdata": eventdata,
        }},
    })


SYSMON = "Microsoft-Windows-Sysmon/Operational"


def fence(word: str, run_id: str, time: str) -> str:
    return line(SYSMON, "1", time, {
        "image": "C:\\\\telos\\\\telos-fence.exe",
        "commandLine": f"\\\"C:\\\\telos\\\\telos-fence.exe\\\" {word} {run_id}",
    })


def logon_type2(time: str) -> str:
    return line("Security", "4624", time, {
        "targetUserName": "eli", "logonType": "2",
        "authenticationPackageName": "Negotiate", "logonProcessName": "User32",
    })


def lsass_access(time: str, access: str, source: str = "C:\\\\x\\\\procdump.exe") -> str:
    return line(SYSMON, "10", time, {
        "sourceImage": source, "targetImage": "C:\\\\WINDOWS\\\\system32\\\\lsass.exe",
        "grantedAccess": access,
    })


# --- the key for one line ---------------------------------------------------

def test_wazuh_field_names_are_matched_to_the_key_map():
    """logonType must count as LogonType, or every 4624 key loses its fields."""
    rec = json.loads(logon_type2("2026-11-13T08:44:44.2070000Z"))
    assert key_for(rec) == "Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]"


def test_lsass_access_value_classes_follow_rule_92900():
    """0x1fffff (ProcDump) is not a 92900 value; 0x101000 (Defender) is, because the
    rule's pattern has no anchors (OPEN-QUESTIONS 35, seen 2026-11-13)."""
    tool = json.loads(lsass_access("2026-11-13T08:28:10.9950000Z", "0x1fffff"))
    defender = json.loads(lsass_access("2026-11-13T08:26:10.4870000Z", "0x101000"))
    assert key_for(tool) == "Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]"
    assert key_for(defender) == "Sysmon-10[GrantedAccess=0x1010,SourceImage,TargetImage]"


def test_a_channel_with_no_tracked_fields_keys_by_event_type():
    rec = json.loads(line("System", "7001", "2026-11-13T08:44:50.0000000Z", {"param1": "x"}))
    assert key_for(rec) == "System-7001[]"


# --- reading lines ----------------------------------------------------------

def test_broken_lines_are_counted_and_non_windows_lines_dropped():
    """A line cut off mid-write is a warning sign and is counted; SIEM-01's own
    lines are normal and are simply not Windows events."""
    raw = [
        logon_type2("2026-11-13T08:44:44.2070000Z"),
        '{"timestamp": "2026-11-13T08:30:00", "agent": {"name": "siem-01"}, "full_log": "x"}',
        '{"timestamp": "2026-11-13T08:30:00", "agent": {"name": "WIN-EP-01"',  # cut off mid-write
        "",
    ]
    records, broken = read_lines(raw)
    assert len(records) == 1
    assert broken == 1


# --- one capture window -----------------------------------------------------

def test_only_events_between_the_fences_of_this_run_and_this_agent_count():
    raw = [
        logon_type2("2026-11-13T08:28:09.0000000Z"),                     # before START
        fence("START", "run-a", "2026-11-13T08:28:10.1623743Z"),
        lsass_access("2026-11-13T08:28:10.9950000Z", "0x1fffff"),
        lsass_access("2026-11-13T08:28:11.0260000Z", "0x1fffff"),
        lsass_access("2026-11-13T08:28:11.5000000Z", "0x1fffff", source="C:\\\\y\\\\other.exe").replace(AGENT, "OTHER-HOST"),
        fence("END", "run-a", "2026-11-13T08:28:13.8095911Z"),
        lsass_access("2026-11-13T08:29:12.8640000Z", "0x1fffff"),       # after END
    ]
    w = count_window(raw, AGENT, "run-a")
    assert w.counts["Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]"] == 2
    assert "Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]" not in w.counts
    # The two fence events are inside the window and are counted like any event.
    assert sum(w.counts.values()) == 4
    assert w.start == "2026-11-13T08:28:10.1623743Z"
    assert w.end == "2026-11-13T08:28:13.8095911Z"


def test_a_window_uses_event_time_not_line_order():
    """The agent can deliver lines late and out of order; the window is cut on the
    event's own time (CLAUDE.md rule 5: fence in telemetry, not host clock)."""
    raw = [
        lsass_access("2026-11-13T08:28:11.0000000Z", "0x1fffff"),        # inside, but delivered first
        fence("START", "run-a", "2026-11-13T08:28:10.0000000Z"),
        fence("END", "run-a", "2026-11-13T08:28:13.0000000Z"),
    ]
    w = count_window(raw, AGENT, "run-a")
    assert w.counts["Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]"] == 1


def test_another_runs_fences_do_not_open_this_window():
    raw = [
        fence("START", "run-a-2", "2026-11-13T08:28:10.0000000Z"),
        fence("END", "run-a-2", "2026-11-13T08:28:13.0000000Z"),
    ]
    with pytest.raises(ValueError, match="no START fence for run 'run-a'"):
        count_window(raw, AGENT, "run-a")


def test_a_missing_end_fence_is_an_error_not_an_open_window():
    """A capture that died before its END fence must not be read as a short run."""
    raw = [fence("START", "run-a", "2026-11-13T08:28:10.0000000Z"),
           lsass_access("2026-11-13T08:28:11.0000000Z", "0x1fffff")]
    with pytest.raises(ValueError, match="no END fence for run 'run-a'"):
        count_window(raw, AGENT, "run-a")


def test_two_start_fences_for_one_run_is_an_error():
    raw = [fence("START", "run-a", "2026-11-13T08:28:10.0000000Z"),
           fence("START", "run-a", "2026-11-13T08:28:11.0000000Z"),
           fence("END", "run-a", "2026-11-13T08:28:13.0000000Z")]
    with pytest.raises(ValueError, match="2 START fences"):
        count_window(raw, AGENT, "run-a")


def test_rules_that_fired_inside_the_window_are_counted():
    """Wazuh writes the alerting rule on each archive line (rule.id, rule.level).
    Surviving coverage counts the rules that did fire (DECISIONS 2026-11-13)."""
    def alert(text: str, rid: str, level: int) -> str:
        rec = json.loads(text)
        rec["rule"] = {"id": rid, "level": level}
        return json.dumps(rec)

    raw = [
        alert(lsass_access("2026-11-13T08:28:09.0000000Z", "0x1010"), "92900", 12),   # before START
        fence("START", "run-a", "2026-11-13T08:28:10.0000000Z"),
        alert(logon_type2("2026-11-13T08:28:11.0000000Z"), "60118", 3),
        alert(logon_type2("2026-11-13T08:28:11.5000000Z"), "60118", 3),
        alert(lsass_access("2026-11-13T08:28:12.0000000Z", "0x1000"), "99999", 0),   # level 0: no alert
        fence("END", "run-a", "2026-11-13T08:28:13.0000000Z"),
    ]
    w = count_window(raw, AGENT, "run-a")
    assert w.fired == {"60118": 2}


# --- windows into a phase ---------------------------------------------------

def test_windows_become_a_phase_with_zeros_for_missing_keys():
    a = [fence("START", "r1", "2026-11-13T08:00:00.0000000Z"),
         lsass_access("2026-11-13T08:00:01.0000000Z", "0x1fffff"),
         fence("END", "r1", "2026-11-13T08:00:02.0000000Z")]
    b = [fence("START", "r2", "2026-11-13T09:00:00.0000000Z"),
         logon_type2("2026-11-13T09:00:01.0000000Z"),
         fence("END", "r2", "2026-11-13T09:00:02.0000000Z")]
    phase = to_phase("pre", [count_window(a, AGENT, "r1"), count_window(b, AGENT, "r2")], window_minutes=15.0)
    phase.validate()
    assert phase.n_runs == 2
    assert phase.counts["Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]"] == [1, 0]
    assert phase.counts["Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]"] == [0, 1]
