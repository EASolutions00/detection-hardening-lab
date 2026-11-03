"""How a raw event becomes an analysis key.

The unit of analysis is not the event type alone. It is the event type **plus
which tracked fields were actually populated**.

Why this matters, and it is the whole reason this module exists. A hardening
change can leave an event firing at exactly the same rate while emptying a field
inside it. Disabling `ProcessCreationIncludeCmdLine_Enabled` leaves Windows
Security event 4688 firing normally, but every event now carries an empty
CommandLine. Any detection rule that matches on CommandLine is blind. The 4688
rate never moved, so a profile keyed on event type alone reports "unchanged" and
the blind spot is missed entirely.

Keying on (event type, populated tracked fields) turns that into a visible
signal without any change to the statistics:

    Security-4688[CommandLine,ParentProcessName]   1247 -> 0      LOST
    Security-4688[ParentProcessName]                  0 -> 1247   NEW

A LOST and a NEW at the same rate is the signature of a field being removed,
as distinct from an event type stopping altogether.

**Which fields are tracked.** Not all of them. Keying on every field present
would give almost every event its own key and make the counts meaningless. A
field belongs in the key only if some detection rule reads it, because losing a
field that no rule reads blinds nothing.

**A few fields also keep their value** (VALUE_KEYED_FIELDS). Presence alone misses a
change that leaves a field filled but changes what it says: LSA Protection keeps
Sysmon 10 firing with GrantedAccess filled, but with less access granted, and rule
92900 matches exactly the values that disappear. So for a field that a rule matches
by value, the key keeps each value a rule looks for and writes "other" for the rest:
`Sysmon-10[GrantedAccess=0x1010,SourceImage,TargetImage]`.

The map below is a starting point. It is structured so it can later be generated
from the rule set itself (a Sigma rule names the fields it matches on in its
detection block), without changing the key format or invalidating stored runs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field

# Provisional. To be generated from the detection rule set; see OPEN-QUESTIONS 1b.
# Each entry lists the fields that detection rules are known to match on for that
# event type. Order does not matter; keys are built sorted.
DEFAULT_TRACKED_FIELDS: dict[str, list[str]] = {
    # Windows Security log
    "Security-4688": ["CommandLine", "NewProcessName", "ParentProcessName"],
    "Security-4624": ["LogonType", "TargetUserName", "AuthenticationPackageName"],
    "Security-4625": ["LogonType", "TargetUserName", "IpAddress"],
    "Security-4776": ["PackageName", "TargetUserName", "Workstation"],
    "Security-4697": ["ServiceName", "ServiceFileName"],
    # PowerShell operational
    "PowerShell-4104": ["ScriptBlockText", "Path"],
    "PowerShell-4103": ["Payload", "ContextInfo"],
    # Sysmon
    "Sysmon-1": ["Image", "CommandLine", "ParentImage", "OriginalFileName", "Hashes"],
    "Sysmon-3": ["Image", "DestinationIp", "DestinationPort"],
    "Sysmon-7": ["Image", "ImageLoaded", "Signed"],
    "Sysmon-10": ["SourceImage", "TargetImage", "GrantedAccess"],
    "Sysmon-11": ["Image", "TargetFilename"],
    "Sysmon-13": ["EventType", "TargetObject", "Details"],
}

# Value keying (DECISIONS 2026-09-29, item 18; list per 2026-10-01). For these few
# fields a detection rule matches specific values, so the key keeps the value: one
# class per value a rule looks for, and "other" for every value no rule looks for.
# Each class holds the pattern its rule uses (Wazuh 4.14.7's shipped rules, read
# 2026-11-03), so the key and the rule cannot disagree: rule 92900's pattern has no
# anchors, so 0x400 fires it too (OPEN-QUESTIONS 35). The first class whose pattern
# matches wins. To be generated from the rule export later.
VALUE_KEYED_FIELDS: dict[str, dict[str, dict[str, str]]] = {
    # Rule 92900 (LSASS memory read), pattern (?i)(0x1010|0x40). Normal Windows
    # uses 0x1000, which is "other".
    "Sysmon-10": {"GrantedAccess": {"0x1010": r"(?i)0x1010", "0x40": r"(?i)0x40"}},
    # Rule 60118 (logon type 2, ^2$); rules 92653 (10) and 92656 (^10$), the wider
    # one kept; rules 92652 and 92657 (authenticationPackageName NTLM).
    "Security-4624": {"LogonType": {"2": r"^2$", "10": r"10"},
                      "AuthenticationPackageName": {"NTLM": r"NTLM"}},
}
OTHER = "other"


def is_populated(value: object) -> bool:
    """True when a field carries usable content.

    Present-but-empty counts as absent, and this is the point of the module.
    A hardening change that strips CommandLine typically leaves the field in the
    event with an empty value rather than removing it. Treating that as
    "present" would hide exactly the loss this study measures.

    Windows also writes literal placeholders for suppressed values, so those are
    treated as absent too.
    """
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    # Windows placeholders for a value that was not recorded.
    return text not in {"-", "N/A", "(null)", "NULL"}


@dataclass(frozen=True)
class KeySpec:
    """The parts of one analysis key."""

    source: str          # "Security", "Sysmon", "PowerShell"
    event_id: str        # "4688"
    present: tuple[str, ...] = ()   # tracked fields that were populated, sorted

    def __str__(self) -> str:
        return f"{self.source}-{self.event_id}[{','.join(self.present)}]"

    @property
    def event_type(self) -> str:
        """The key without its field part, for grouping and for reports."""
        return f"{self.source}-{self.event_id}"


class KeyBuilder:
    """Turns raw event records into analysis keys."""

    def __init__(self, tracked: dict[str, list[str]] | None = None,
                 value_keyed: dict[str, dict[str, dict[str, str]]] | None = None):
        source_map = DEFAULT_TRACKED_FIELDS if tracked is None else tracked
        # Store sorted, so key text is deterministic regardless of config order.
        self._tracked = {k: sorted(v) for k, v in source_map.items()}
        values = VALUE_KEYED_FIELDS if value_keyed is None else value_keyed
        # event type -> field -> {class: compiled rule pattern}
        self._values = {et: {f: {c: re.compile(p) for c, p in classes.items()}
                             for f, classes in fields.items()}
                        for et, fields in values.items()}

    def _part(self, event_type: str, field: str, value: object) -> str:
        """The key part for one populated field: the name alone, or name=class for
        a value-keyed field."""
        classes = self._values.get(event_type, {}).get(field)
        if classes is None:
            return field
        text = str(value).strip()
        for name, pattern in classes.items():
            if pattern.search(text):
                return f"{field}={name}"
        return f"{field}={OTHER}"

    def tracked_for(self, event_type: str) -> list[str]:
        """Fields tracked for one event type. Empty list if none configured.

        An event type with no configured fields degrades to event-type-only
        keying, which is the correct fallback rather than an error.
        """
        return self._tracked.get(event_type, [])

    def build(self, source: str, event_id: str | int, fields: dict[str, object]) -> KeySpec:
        """Build the key for one event.

        fields is the event's field dictionary as parsed from the archive.
        Only tracked fields are inspected; everything else is ignored.
        """
        event_type = f"{source}-{event_id}"
        tracked = self.tracked_for(event_type)
        present = tuple(self._part(event_type, f, fields.get(f))
                        for f in tracked if is_populated(fields.get(f)))
        return KeySpec(source=source, event_id=str(event_id), present=present)

    def build_str(self, source: str, event_id: str | int, fields: dict[str, object]) -> str:
        """Convenience: the key as the string the profile is keyed on."""
        return str(self.build(source, event_id, fields))


def parse(key: str) -> KeySpec:
    """Read a key string back into its parts.

    Reports group findings by event type, so they need to recover the event type
    from a stored key without re-reading the raw archive.
    """
    if "[" not in key or not key.endswith("]"):
        raise ValueError(f"not a TeLoS event key: {key!r}")
    head, _, tail = key.partition("[")
    fields_text = tail[:-1]
    source, _, event_id = head.rpartition("-")
    if not source:
        raise ValueError(f"key has no source part: {key!r}")
    present = tuple(f for f in fields_text.split(",") if f)
    return KeySpec(source=source, event_id=event_id, present=present)


def group_by_event_type(keys: list[str]) -> dict[str, list[str]]:
    """Group keys by their event type.

    Used to spot the field-loss signature: one key LOST and another NEW under
    the same event type, where the second is the first minus one field.
    """
    out: dict[str, list[str]] = {}
    for k in keys:
        et = parse(k).event_type
        out.setdefault(et, []).append(k)
    return out


def field_loss_pairs(lost: list[str], new: list[str]) -> list[tuple[str, str, tuple[str, ...]]]:
    """Find LOST/NEW pairs that differ only by dropped fields.

    Returns (lost_key, new_key, fields_that_disappeared) for each match.

    This is the field-level blind spot, stated explicitly. Without it a reader
    sees an unexplained LOST next to an unexplained NEW and has to work out the
    relationship by hand.
    """
    pairs: list[tuple[str, str, tuple[str, ...]]] = []
    new_by_type: dict[str, list[KeySpec]] = {}
    for k in new:
        spec = parse(k)
        new_by_type.setdefault(spec.event_type, []).append(spec)

    for lost_key in lost:
        lost_spec = parse(lost_key)
        for new_spec in new_by_type.get(lost_spec.event_type, []):
            lost_set, new_set = set(lost_spec.present), set(new_spec.present)
            # The new key must be a strict subset: same event, fewer fields.
            if new_set < lost_set:
                # Report field names only: "GrantedAccess", not "GrantedAccess=other".
                dropped = tuple(sorted(f.split("=", 1)[0] for f in lost_set - new_set))
                pairs.append((lost_key, str(new_spec), dropped))
    return pairs
