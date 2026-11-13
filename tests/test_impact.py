"""Tests for impact ranking (DECISIONS 2026-11-13: a ranking by blind techniques,
highest severity and number of rules; surviving coverage counts rules that did
fire after the change, not rules that could fire).

The rules are cut down from the real export (92900, 92403) plus one made-up
Sysmon 1 rule (99001) that covers the same technique as 92900 from another
event type.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos import Classification, Phase
from telos.impact import rank_impact
from telos.index import build_index, load_rules
from telos.model import AnalysisResult, Finding, ProfileOutcome

RULES = """
<group name="windows,">
  <rule id="60000" level="0">
    <decoded_as>windows_eventchannel</decoded_as>
    <description>Group of windows rules.</description>
  </rule>
  <rule id="60004" level="0">
    <if_sid>60000</if_sid>
    <field name="win.system.channel">^Microsoft-Windows-Sysmon/Operational$</field>
    <description>Sysmon channel</description>
  </rule>
  <rule id="61603" level="0">
    <if_sid>60004</if_sid>
    <field name="win.system.eventID">^1$</field>
    <description>Sysmon - Event 1</description>
    <group>sysmon_event1,</group>
  </rule>
  <rule id="61610" level="0">
    <if_sid>60004</if_sid>
    <field name="win.system.eventID">^8$</field>
    <description>Sysmon - Event 8</description>
    <group>sysmon_event8,</group>
  </rule>
  <rule id="61612" level="0">
    <if_sid>60004</if_sid>
    <field name="win.system.eventID">^10$</field>
    <description>Sysmon - Event 10</description>
    <group>sysmon_event_10,</group>
  </rule>
  <rule id="92403" level="12">
    <if_group>sysmon_event8</if_group>
    <field name="win.eventdata.targetImage" type="pcre2">(?i)lsass\\.exe</field>
    <description>LSASS accessed, possible code injection</description>
    <mitre><id>T1055</id></mitre>
  </rule>
  <rule id="92900" level="12">
    <if_group>sysmon_event_10</if_group>
    <field name="win.eventdata.grantedAccess" type="pcre2">(?i)(0x1010|0x40)</field>
    <description>Lsass process was accessed with read permissions</description>
    <mitre><id>T1003.001</id></mitre>
  </rule>
  <rule id="99001" level="6">
    <if_group>sysmon_event1</if_group>
    <field name="win.eventdata.commandLine" type="pcre2">(?i)procdump</field>
    <description>Made-up: ProcDump command line</description>
    <mitre><id>T1003.001</id></mitre>
  </rule>
</group>
"""

LSASS_READ = "Sysmon-10[GrantedAccess=0x1010,SourceImage,TargetImage]"
INJECTION = "Sysmon-8[]"
PROCESS = "Sysmon-1[CommandLine,Hashes,Image,OriginalFileName,ParentImage]"
NO_RULE = "Sysmon-13[Details,EventType,TargetObject]"


@pytest.fixture
def index(tmp_path):
    (tmp_path / "rules.xml").write_text(RULES, encoding="utf-8")
    return build_index(load_rules(tmp_path))


def result(*pairs):
    return AnalysisResult(outcome=ProfileOutcome.CHANGED, outcome_reason="test",
                          findings=[Finding(key=k, classification=c) for k, c in pairs])


def post(counts):
    return Phase(name="post", counts={k: [v, v, v] for k, v in counts.items()})


def test_a_technique_no_rule_fired_for_after_the_change_is_blind(index):
    r = result((LSASS_READ, Classification.LOST))
    [hit] = rank_impact(r, post({LSASS_READ: 0, PROCESS: 0}), index, fired_after={})
    assert hit.key == LSASS_READ
    assert hit.rules == ["92900"]
    assert hit.max_level == 12
    assert hit.blind_techniques == ["T1003.001"]


def test_a_rule_for_the_technique_that_fired_after_the_change_keeps_it_covered(index):
    r = result((LSASS_READ, Classification.LOST))
    [hit] = rank_impact(r, post({LSASS_READ: 0, PROCESS: 5}), index, fired_after={"99001": 3})
    assert hit.blind_techniques == []
    assert hit.surviving == {"T1003.001": ["99001"]}


def test_a_rule_that_only_could_fire_is_context_not_coverage(index):
    """Sysmon 1 events survive and 99001 reads them, but 99001 did not fire."""
    r = result((LSASS_READ, Classification.LOST))
    [hit] = rank_impact(r, post({LSASS_READ: 0, PROCESS: 5}), index, fired_after={})
    assert hit.blind_techniques == ["T1003.001"]
    assert hit.could_fire == {"T1003.001": ["99001"]}


def test_a_reduced_key_whose_own_rule_still_fired_is_covered(index):
    r = result((INJECTION, Classification.REDUCED))
    [hit] = rank_impact(r, post({INJECTION: 2}), index, fired_after={"92403": 1})
    assert hit.blind_techniques == []


def test_blind_techniques_rank_before_severity(index):
    r = result((LSASS_READ, Classification.LOST), (INJECTION, Classification.REDUCED))
    ranked = rank_impact(r, post({LSASS_READ: 0, INJECTION: 2, PROCESS: 5}), index,
                         fired_after={"99001": 2})
    assert [h.key for h in ranked] == [INJECTION, LSASS_READ]


def test_only_lost_and_reduced_keys_are_ranked(index):
    r = result((LSASS_READ, Classification.UNCHANGED), (INJECTION, Classification.NEW),
               (PROCESS, Classification.INCONCLUSIVE))
    assert rank_impact(r, post({LSASS_READ: 3, INJECTION: 1, PROCESS: 5}), index, fired_after={}) == []


def test_a_lost_key_no_rule_reads_is_listed_last_with_no_rules(index):
    r = result((NO_RULE, Classification.LOST), (LSASS_READ, Classification.LOST))
    ranked = rank_impact(r, post({NO_RULE: 0, LSASS_READ: 0}), index, fired_after={})
    assert [h.key for h in ranked] == [LSASS_READ, NO_RULE]
    assert ranked[-1].rules == [] and ranked[-1].max_level == 0 and ranked[-1].blind_techniques == []
