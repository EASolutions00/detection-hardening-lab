"""Tests for field-aware event keys.

The headline test is `test_field_loss_is_invisible_to_event_type_keying`, which
demonstrates the failure the schema decision exists to prevent. If that test is
ever deleted, the reason for the composite key goes with it.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos import Classification, Phase, VarianceModel, analyse
from telos.eventkey import (
    KeyBuilder,
    KeySpec,
    field_loss_pairs,
    group_by_event_type,
    is_populated,
    parse,
)

STABLE = [100, 101, 99, 100, 100]


# --------------------------------------------------------------------------
# What counts as a populated field
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["cmd.exe /c whoami", "C:\\Windows", 0, False, "0"])
def test_real_values_are_populated(value):
    assert is_populated(value)


@pytest.mark.parametrize("value", [None, "", "   ", "\t\n", "-", "N/A", "(null)", "NULL"])
def test_empty_and_placeholder_values_are_not_populated(value):
    """Present-but-empty must count as absent.

    This is the crux of the whole design. A hardening change that strips
    CommandLine usually leaves the field in the event carrying an empty value
    rather than removing the field. Treating that as present would hide exactly
    the loss this study measures.
    """
    assert not is_populated(value)


def test_zero_is_populated_not_empty():
    """A numeric zero is a real value, not a missing one.

    LogonType 0 and GrantedAccess 0 are meaningful. Truthiness testing would
    wrongly discard them, so `is_populated` checks emptiness, not truth.
    """
    assert is_populated(0)


# --------------------------------------------------------------------------
# Key construction
# --------------------------------------------------------------------------

def test_key_lists_only_populated_tracked_fields():
    kb = KeyBuilder({"Security-4688": ["CommandLine", "NewProcessName"]})
    key = kb.build_str("Security", 4688, {
        "CommandLine": "whoami",
        "NewProcessName": "C:\\Windows\\System32\\whoami.exe",
    })
    assert key == "Security-4688[CommandLine,NewProcessName]"


def test_emptied_field_drops_out_of_the_key():
    """The CommandLine case, at the unit level."""
    kb = KeyBuilder({"Security-4688": ["CommandLine", "NewProcessName"]})
    key = kb.build_str("Security", 4688, {
        "CommandLine": "",                       # stripped by the hardening change
        "NewProcessName": "C:\\Windows\\System32\\whoami.exe",
    })
    assert key == "Security-4688[NewProcessName]"


def test_untracked_fields_are_ignored():
    """A field no detection rule reads does not belong in the key.

    Including every field would give almost every event its own key and make
    the counts meaningless.
    """
    kb = KeyBuilder({"Security-4688": ["CommandLine"]})
    key = kb.build_str("Security", 4688, {
        "CommandLine": "whoami",
        "SubjectLogonId": "0x3e7",               # not tracked
        "TokenElevationType": "%%1936",          # not tracked
    })
    assert key == "Security-4688[CommandLine]"


def test_unconfigured_event_type_degrades_to_event_type_only():
    """No configured fields is a valid state, not an error."""
    kb = KeyBuilder({})
    assert kb.build_str("Sysmon", 255, {"Anything": "value"}) == "Sysmon-255[]"


def test_key_is_deterministic_regardless_of_config_order():
    """Two builders configured differently must produce identical keys.

    Stored runs are compared across weeks. A key that depended on dict ordering
    would silently split one event type into two.
    """
    a = KeyBuilder({"Sysmon-1": ["Image", "CommandLine", "ParentImage"]})
    b = KeyBuilder({"Sysmon-1": ["ParentImage", "Image", "CommandLine"]})
    fields = {"Image": "x", "CommandLine": "y", "ParentImage": "z"}
    assert a.build_str("Sysmon", 1, fields) == b.build_str("Sysmon", 1, fields)


# --------------------------------------------------------------------------
# Reading keys back
# --------------------------------------------------------------------------

def test_parse_round_trips():
    spec = KeySpec("Security", "4688", ("CommandLine", "NewProcessName"))
    assert parse(str(spec)) == spec


def test_parse_handles_a_key_with_no_fields():
    assert parse("Sysmon-255[]") == KeySpec("Sysmon", "255", ())


def test_parse_rejects_a_non_key():
    with pytest.raises(ValueError, match="not a TeLoS event key"):
        parse("Security-4688")


def test_event_type_strips_the_field_part():
    assert parse("Security-4688[CommandLine]").event_type == "Security-4688"


def test_group_by_event_type():
    keys = ["Security-4688[CommandLine]", "Security-4688[]", "Sysmon-1[Image]"]
    grouped = group_by_event_type(keys)
    assert len(grouped["Security-4688"]) == 2
    assert len(grouped["Sysmon-1"]) == 1


# --------------------------------------------------------------------------
# Pairing a loss with the key that replaced it
# --------------------------------------------------------------------------

def test_field_loss_pair_is_found():
    lost = ["PowerShell-4104[Path,ScriptBlockText]"]
    new = ["PowerShell-4104[Path]"]
    pairs = field_loss_pairs(lost, new)
    assert len(pairs) == 1
    assert pairs[0][2] == ("ScriptBlockText",)


def test_unrelated_lost_and_new_keys_are_not_paired():
    """A different event type appearing is not a field loss."""
    lost = ["Security-4688[CommandLine]"]
    new = ["Sysmon-1[Image]"]
    assert field_loss_pairs(lost, new) == []


def test_a_new_key_with_more_fields_is_not_a_field_loss():
    """Gaining a field is not losing one.

    The new key must be a strict subset of the lost one. Without that check, a
    change that adds telemetry would be reported as a blind spot.
    """
    lost = ["Sysmon-1[Image]"]
    new = ["Sysmon-1[CommandLine,Image]"]
    assert field_loss_pairs(lost, new) == []


# --------------------------------------------------------------------------
# The reason this schema exists
# --------------------------------------------------------------------------

def test_field_loss_is_invisible_to_event_type_keying():
    """The failure that justifies the composite key. Do not delete this test.

    A hardening change empties ScriptBlockText inside PowerShell 4104. The event
    still fires 838 times per window, exactly as before. Any detection rule
    matching on ScriptBlockText is now blind.

    Keyed on event type alone, the rate never moves and the analyser correctly
    reports UNCHANGED, because on that evidence nothing did change. The blind
    spot is invisible. That is the whole problem.
    """
    vm = VarianceModel.from_control(Phase("control", {
        "PowerShell-4104": STABLE,
        "anchor": STABLE,
    }))
    pre = Phase("pre", {"PowerShell-4104": [838, 838, 838], "anchor": [100, 100, 100]})
    post = Phase("post", {"PowerShell-4104": [838, 838, 838], "anchor": [0, 0, 0]})

    result = analyse(pre, post, vm)
    verdicts = {f.key: f.classification for f in result.findings}
    assert verdicts["PowerShell-4104"] is Classification.UNCHANGED


def test_field_loss_is_caught_by_field_aware_keying():
    """The same change, the same rates, under the composite key.

    Nothing about the statistics changed. Only the key did. The loss now
    produces a LOST and a NEW that pair into an explicit field-level finding.
    """
    full = "PowerShell-4104[Path,ScriptBlockText]"
    reduced = "PowerShell-4104[Path]"

    vm = VarianceModel.from_control(Phase("control", {
        full: STABLE, reduced: [0, 0, 0, 0, 0], "anchor": STABLE,
    }))
    pre = Phase("pre", {
        full: [838, 838, 838], reduced: [0, 0, 0], "anchor": [100, 100, 100],
    })
    post = Phase("post", {
        full: [0, 0, 0], reduced: [838, 838, 838], "anchor": [100, 100, 100],
    })

    result = analyse(pre, post, vm)
    verdicts = {f.key: f.classification for f in result.findings}

    assert verdicts[full] is Classification.LOST
    assert verdicts[reduced] is Classification.NEW

    pairs = field_loss_pairs(
        [f.key for f in result.by_class(Classification.LOST)],
        [f.key for f in result.by_class(Classification.NEW)],
    )
    assert pairs == [(full, reduced, ("ScriptBlockText",))]
