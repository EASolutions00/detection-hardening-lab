"""Tests for the rule-to-key index: which Wazuh rules read which event key.

The XML below is cut down from the real rule files exported from SIEM-01 on
2026-11-13 (Wazuh 4.14.7): the 4624 chain 60000 > 60001 > 60103 > 60106 > 60118
and > 92651 > 92653, and the Sysmon chain 60000 > 60004 > 61600 > 61610 / 61612,
with 92403 and 92900 attached by group.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.index import build_index, load_rules, osregex_to_python

BASE = """
<group name="windows,">
  <rule id="60000" level="0">
    <decoded_as>windows_eventchannel</decoded_as>
    <field name="win.system.providerName">\\.+</field>
    <description>Group of windows rules.</description>
  </rule>
  <rule id="60001" level="0">
    <if_sid>60000</if_sid>
    <field name="win.system.channel">^Security$</field>
    <description>Group of Windows rules for the security channel.</description>
  </rule>
  <rule id="60004" level="0">
    <if_sid>60000</if_sid>
    <field name="win.system.channel">^Microsoft-Windows-Sysmon/Operational$</field>
    <description>Group of Windows rules for the sysmon channel.</description>
  </rule>
</group>
"""

SECURITY = """
<group name="windows,windows_security,">
  <rule id="60103" level="0">
    <if_sid>60001</if_sid>
    <field name="win.system.severityValue">^AUDIT_SUCCESS$|^success$</field>
    <description>Windows audit success event</description>
  </rule>
  <rule id="60106" level="3">
    <if_sid>60103</if_sid>
    <field name="win.system.eventID">^528$|^540$|^673$|^4624$|^4769$</field>
    <description>Windows Logon Success</description>
    <mitre><id>T1078</id></mitre>
  </rule>
  <rule id="60118" level="3">
    <if_sid>60106</if_sid>
    <field name="win.eventdata.workstationName">\\.+</field>
    <field name="win.eventdata.logonType">^2$</field>
    <description>Windows Workstation Logon Success</description>
    <mitre><id>T1078</id></mitre>
  </rule>
  <rule id="92651" level="0">
    <if_sid>60106</if_sid>
    <field name="win.eventdata.ipAddress" type="pcre2">(?:[0-9]{1,3}\\.){3}[0-9]{1,3}</field>
    <field name="win.eventdata.ipAddress" type="pcre2" negate="yes">127\\.0\\.0\\.1</field>
    <description>Successful Remote Logon</description>
  </rule>
  <rule id="92653" level="3">
    <if_sid>92651</if_sid>
    <field name="win.eventdata.logonType" type="pcre2">10</field>
    <description>User logged using Remote Desktop Connection (RDP)</description>
    <mitre><id>T1021.001</id><id>T1078.002</id></mitre>
  </rule>
</group>
"""

SYSMON = """
<group name="windows,sysmon,">
  <rule id="61600" level="0">
    <if_sid>60004</if_sid>
    <field name="win.system.severityValue">^INFORMATION$</field>
    <description>Windows Sysmon informational event</description>
  </rule>
  <rule id="61610" level="0">
    <if_sid>61600</if_sid>
    <field name="win.system.eventID">^8$</field>
    <description>Sysmon - Event 8</description>
    <group>sysmon_event8,</group>
  </rule>
  <rule id="61612" level="0">
    <if_sid>61600</if_sid>
    <field name="win.system.eventID">^10$</field>
    <description>Sysmon - Event 10</description>
    <group>sysmon_event_10,</group>
  </rule>
</group>
<group name="sysmon,sysmon_eid8_detections,windows,">
  <rule id="92403" level="12">
    <if_group>sysmon_event8</if_group>
    <field name="win.eventdata.targetImage" type="pcre2">(?i)lsass\\.exe</field>
    <description>LSASS process was accessed, possible code injection for credential dumping</description>
    <mitre><id>T1055</id></mitre>
  </rule>
  <rule id="92900" level="12">
    <if_group>sysmon_event_10</if_group>
    <field name="win.eventdata.targetImage" type="pcre2">(?i)lsass\\.exe</field>
    <field name="win.eventdata.grantedAccess" type="pcre2">(?i)(0x1010|0x40)</field>
    <field name="win.eventdata.sourceImage" type="pcre2" negate="yes">(?i)(C:\\\\Program Files|wmiprvse\\.exe)</field>
    <description>Lsass process was accessed with read permissions, possible credential dump</description>
    <mitre><id>T1003.001</id></mitre>
  </rule>
</group>
"""

# The same group name, defined by an old syslog-format rule with no Windows event
# ID (0330-sysmon_rules.xml). It must not give 92403 a second event type.
OLD_SYSMON = """
<group name="sysmon,">
  <rule id="185006" level="0">
    <if_sid>18100</if_sid>
    <match>Microsoft-Windows-Sysmon/Operational: INFORMATION(8)</match>
    <description>Sysmon - Event 8</description>
    <group>sysmon_event8,</group>
  </rule>
</group>
"""


@pytest.fixture
def index(tmp_path):
    for name, text in [("0575-win-base_rules.xml", BASE), ("0580-win-security_rules.xml", SECURITY),
                       ("0595-win-sysmon_rules.xml", SYSMON), ("0330-sysmon_rules.xml", OLD_SYSMON)]:
        (tmp_path / name).write_text(text, encoding="utf-8")
    return build_index(load_rules(tmp_path))


def ids(rules):
    return sorted(r.rule.id for r in rules)


# --- reading the files --------------------------------------------------------

def test_files_with_several_top_level_groups_are_read(tmp_path):
    """Wazuh rule files have several <group> elements and no single root."""
    (tmp_path / "a.xml").write_text(SECURITY, encoding="utf-8")
    rules = load_rules(tmp_path)
    assert {"60103", "60106", "60118", "92651", "92653"} <= set(rules)
    assert rules["60118"].level == 3
    assert rules["92653"].mitre == ("T1021.001", "T1078.002")


def test_osregex_dot_means_any_character():
    """In Wazuh's own regex, \\. is any character, so \\.+ means 'not empty'."""
    import re
    assert re.search(osregex_to_python(r"\.+"), "WIN-EP-01")
    assert not re.search(osregex_to_python(r"\.+"), "")


# --- event type, by following parents ---------------------------------------

def test_event_type_is_inherited_through_parent_rules(index):
    assert index.rule("60118").event_types == {"Security-4624", "Security-4769", "Security-528",
                                               "Security-540", "Security-673"}
    assert "Security-4624" in index.rule("92653").event_types


def test_a_rule_testing_non_windows_fields_is_not_placed(tmp_path):
    """0330-sysmon_rules.xml tests fields such as sysmon.parentImage, which Windows
    event-channel events never carry, so its rules cannot fire here even though they
    borrow the group sysmon_event1 (found 2026-11-13 on the real export)."""
    old = """
<group name="sysmon,">
  <rule id="184666" level="12">
    <if_group>sysmon_event1</if_group>
    <field name="sysmon.image">svchost.exe</field>
    <description>Sysmon - Suspicious Process - svchost.exe</description>
    <mitre><id>T1055</id></mitre>
  </rule>
</group>
"""
    sysmon1 = SYSMON.replace('<rule id="61610"', """<rule id="61603" level="0">
    <if_sid>61600</if_sid>
    <field name="win.system.eventID">^1$</field>
    <description>Sysmon - Event 1</description>
    <group>sysmon_event1,</group>
  </rule>
  <rule id="61610\"""")
    for name, text in [("base.xml", BASE), ("sysmon.xml", sysmon1), ("old.xml", old)]:
        (tmp_path / name).write_text(text, encoding="utf-8")
    idx = build_index(load_rules(tmp_path))
    assert "61603" in idx.rules
    assert "184666" not in idx.rules


def test_event_type_is_found_through_a_parent_group(index):
    assert index.rule("92403").event_types == {"Sysmon-8"}
    assert index.rule("92900").event_types == {"Sysmon-10"}


# --- fields read, own and inherited -----------------------------------------

def test_fields_include_the_parents_conditions_in_key_names(index):
    """92653 fires only if 92651 matched, so it also reads IpAddress."""
    fields = {c.field for c in index.rule("92653").conditions}
    assert fields == {"IpAddress", "LogonType"}


# --- which rules read a key -------------------------------------------------

def test_rules_reading_a_type_2_logon(index):
    key = "Security-4624[AuthenticationPackageName=other,LogonType=2,TargetUserName]"
    assert ids(index.rules_reading(key)) == ["60106", "60118"]


def test_rules_reading_a_type_10_logon(index):
    key = "Security-4624[AuthenticationPackageName=NTLM,LogonType=10,TargetUserName]"
    # 60118 needs logon type 2, so it cannot fire on this key.
    assert ids(index.rules_reading(key)) == ["60106", "92653"]


def test_92900_needs_one_of_its_access_values(index):
    hit = "Sysmon-10[GrantedAccess=0x1010,SourceImage,TargetImage]"
    miss = "Sysmon-10[GrantedAccess=other,SourceImage,TargetImage]"
    assert ids(index.rules_reading(hit)) == ["92900"]
    assert ids(index.rules_reading(miss)) == []


def test_a_key_with_no_tracked_fields_matches_on_event_type(index):
    """Sysmon 8 has no tracked fields, so the key cannot rule 92403 out."""
    assert ids(index.rules_reading("Sysmon-8[]")) == ["92403"]


# --- what the key map does not track ----------------------------------------

def test_fields_rules_read_but_the_key_map_does_not_track_are_listed(index):
    gaps = index.untracked_fields()
    assert "WorkstationName" in gaps["Security-4624"]
    assert "IpAddress" in gaps["Security-4624"]
    assert "TargetImage" in gaps["Sysmon-8"]
    assert "GrantedAccess" not in gaps.get("Sysmon-10", set())
