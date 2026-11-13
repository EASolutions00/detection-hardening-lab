"""The rule-to-key index: which Wazuh rules read which event key.

The analyser reports keys (LOST, REDUCED). This module says which detection rules
depend on a key, so a lost key can be read as "these alerts lost their evidence".
It reads the rule files exported from SIEM-01 (DECISIONS 2026-10-01: Wazuh
4.14.7's shipped rules, exported whole) and needs nothing else.

How a rule is placed.

1. **Event type, by following parents.** Most rules do not name their event.
   60118 says only "parent 60106" and "logonType ^2$"; the event ID 4624 is in
   60106, and the channel (Security) is in 60001 further up. A parent is named by
   `if_sid` (a rule ID) or `if_group` (any rule carrying that group). Only parents
   that lead to a Windows event ID count: the old syslog-format Sysmon rules
   (0330-sysmon_rules.xml) use the same group names with no event ID.
2. **Fields, own and inherited.** A child fires only if its parent matched, so a
   child also reads its parent's fields (92653 reads IpAddress through 92651).
   Inherited only through a single `if_sid` parent; group parents carry only the
   event ID.
4. **Rules that test a field outside `win.*` are not placed**, nor their children.
   The old syslog-format Sysmon rules (0330-sysmon_rules.xml) test `sysmon.image`
   and similar, which Windows event-channel events never carry, so they cannot fire
   here even though they borrow groups such as `sysmon_event1` (found 2026-11-13).
3. **Field names** are turned into the key map's names the same way the archive
   reader does: `win.eventdata.logonType` becomes `LogonType`.

How a rule is matched to a key (`rules_reading`).

- Only alerting rules count (level 1 or more).
- The key's event type must be one of the rule's.
- A negated condition never rules a rule out: the key cannot show the value.
- A field the key map does not track cannot rule a rule out either; it is listed
  by `untracked_fields()` instead, as a gap in the key map.
- A tracked field that is absent from the key rules the rule out: a Wazuh field
  condition fails on a missing field.
- A value-keyed field (eventkey.VALUE_KEYED_FIELDS) is tested by running the rule's
  pattern on the key's class name, for example "2" for LogonType=2. For the class
  "other", the rule is ruled out only if its pattern matches one of the class
  names, that is, only for the rules the classes were built for.

Wazuh patterns. A `<field>` without `type="pcre2"` uses Wazuh's own regex
(OS_Regex), where `\\.` means any character, so `\\.+` means "not empty". Only
that and `\\p` are translated; the rest is read as Python regex `(unverified for
unusual patterns)`. A pattern Python cannot compile is kept as unknown, which
never rules a rule out.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .archive import SOURCE_BY_CHANNEL
from .eventkey import OTHER, VALUE_KEYED_FIELDS, KeyBuilder, parse

_PUNCT = r"[!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]"


def osregex_to_python(pattern: str) -> str:
    """Translate the two OS_Regex escapes that differ from Python regex."""
    out, i = [], 0
    while i < len(pattern):
        if pattern[i] == "\\" and i + 1 < len(pattern):
            nxt = pattern[i + 1]
            out.append("." if nxt == "." else _PUNCT if nxt == "p" else pattern[i:i + 2])
            i += 2
        else:
            out.append(pattern[i])
            i += 1
    return "".join(out)


def _key_name(wazuh_name: str) -> str | None:
    """`win.eventdata.logonType` -> `LogonType`; None for anything else."""
    prefix = "win.eventdata."
    if not wazuh_name.startswith(prefix):
        return None
    name = wazuh_name[len(prefix):]
    return name[:1].upper() + name[1:]


@dataclass(frozen=True)
class Condition:
    """One `<field>` test on an event-data field."""

    field: str            # key-map name, e.g. LogonType
    raw: str              # the pattern as written in the rule file
    pcre2: bool
    negate: bool

    @property
    def regex(self) -> re.Pattern | None:
        text = self.raw if self.pcre2 else osregex_to_python(self.raw)
        try:
            return re.compile(text)
        except re.error:
            return None


@dataclass
class Rule:
    """One `<rule>` as written in a file."""

    id: str
    level: int
    description: str
    file: str
    mitre: tuple[str, ...] = ()
    if_sid: tuple[str, ...] = ()
    if_group: tuple[str, ...] = ()
    groups: frozenset[str] = frozenset()
    channel: str | None = None          # raw pattern on win.system.channel
    event_ids: str | None = None        # raw pattern on win.system.eventID
    conditions: tuple[Condition, ...] = ()
    foreign: bool = False               # tests a field outside win.* (cannot fire on event-channel events)


@dataclass
class IndexedRule:
    """A rule placed on its event types, with its own and inherited conditions."""

    rule: Rule
    event_types: set[str] = field(default_factory=set)
    conditions: list[Condition] = field(default_factory=list)


def _split(text: str | None) -> tuple[str, ...]:
    return tuple(t for t in re.split(r"[,\s]+", text or "") if t)


def _read_file(path: Path) -> list[Rule]:
    text = path.read_text(encoding="utf-8", errors="replace")
    root = ET.fromstring(f"<root>{text}</root>")   # files have several top-level <group>
    rules: list[Rule] = []
    for group_el in root.iter("group"):
        outer = set(_split(group_el.get("name")))
        for el in group_el.findall("rule"):
            own_groups = set()
            for g in el.findall("group"):
                own_groups |= set(_split(g.text))
            channel = event_ids = None
            conds: list[Condition] = []
            foreign = False
            for f in el.findall("field"):
                name, raw = f.get("name", ""), (f.text or "")
                if not name.startswith("win."):
                    foreign = True
                    continue
                pcre2 = f.get("type", "") == "pcre2"
                negate = f.get("negate", "no") == "yes"
                if name == "win.system.channel" and not negate:
                    channel = raw
                elif name == "win.system.eventID" and not negate:
                    event_ids = raw
                elif (key := _key_name(name)) is not None:
                    conds.append(Condition(key, raw, pcre2, negate))
            parents = _split(el.findtext("if_sid")) + _split(el.findtext("if_matched_sid"))
            pgroups = _split(el.findtext("if_group")) + _split(el.findtext("if_matched_group"))
            rules.append(Rule(
                id=el.get("id", ""), level=int(el.get("level", "0")),
                description=(el.findtext("description") or "").strip(), file=path.name,
                mitre=tuple(i.text.strip() for i in el.findall("mitre/id") if i.text),
                if_sid=parents, if_group=pgroups, groups=frozenset(outer | own_groups),
                channel=channel, event_ids=event_ids, conditions=tuple(conds), foreign=foreign))
    return rules


def load_rules(folder: str | Path) -> dict[str, Rule]:
    """Read every rule file under `folder`. Files that are not valid XML are skipped
    and listed in `load_rules.unparsed` (the caller should report them)."""
    rules: dict[str, Rule] = {}
    unparsed: list[str] = []
    for path in sorted(Path(folder).rglob("*.xml")):
        try:
            for r in _read_file(path):
                rules[r.id] = r
        except ET.ParseError:
            unparsed.append(path.name)
    load_rules.unparsed = unparsed
    return rules


load_rules.unparsed = []


def _source(channel_pattern: str) -> str:
    name = channel_pattern.strip().lstrip("^").rstrip("$")
    return SOURCE_BY_CHANNEL.get(name, name)


def _ids(pattern: str) -> set[str] | None:
    """`^528$|^4624$` -> {"528", "4624"}; None if any part is not a plain number."""
    out = set()
    for part in pattern.split("|"):
        p = part.strip().lstrip("^").rstrip("$")
        if not p.isdigit():
            return None
        out.add(p)
    return out


class RuleIndex:
    """Wazuh rules placed on the event keys they read."""

    def __init__(self, rules: dict[str, Rule]):
        self._raw = rules
        self._by_group: dict[str, list[str]] = {}
        for r in rules.values():
            for g in r.groups:
                self._by_group.setdefault(g, []).append(r.id)
        self._memo: dict[str, tuple[set[tuple[str | None, str | None]], list[Condition]]] = {}
        self.rules: dict[str, IndexedRule] = {}
        for rid in rules:
            types, conds = self._resolve(rid, set())
            names = {f"{s}-{e}" for s, e in types if s and e}
            if names:
                self.rules[rid] = IndexedRule(rules[rid], names, conds)

    def _resolve(self, rid: str, seen: set[str]) -> tuple[set[tuple[str | None, str | None]], list[Condition]]:
        """(channel source, event id) pairs this rule can fire on, and its conditions."""
        if rid in self._memo:
            return self._memo[rid]
        r = self._raw.get(rid)
        if r is None or rid in seen or r.foreign:
            return set(), []
        seen = seen | {rid}

        parent_types: set[tuple[str | None, str | None]] = set()
        inherited: list[Condition] = []
        for p in r.if_sid:
            t, c = self._resolve(p, seen)
            parent_types |= t
            if len(r.if_sid) == 1:
                inherited = c
        for g in r.if_group:
            for p in self._by_group.get(g, []):
                t, _ = self._resolve(p, seen)
                parent_types |= {x for x in t if x[1] is not None}   # only parents with an event ID

        if not r.if_sid and not r.if_group:
            parent_types = {(None, None)}
        source = _source(r.channel) if r.channel else None
        ids = _ids(r.event_ids) if r.event_ids else None

        types: set[tuple[str | None, str | None]] = set()
        for ps, pe in parent_types:
            s = source or ps
            if ids is not None:
                types |= {(s, e) for e in ids}
            elif r.event_ids is None:
                types.add((s, pe))
        result = (types, inherited + list(r.conditions))
        self._memo[rid] = result
        return result

    def rule(self, rid: str) -> IndexedRule:
        return self.rules[rid]

    def raw(self, rid: str) -> Rule | None:
        """Any rule as read from the files, placed or not (for its level and techniques)."""
        return self._raw.get(rid)

    def rules_reading(self, key: str, builder: KeyBuilder | None = None) -> list[IndexedRule]:
        """Alerting rules that can fire on events with this key."""
        builder = builder or KeyBuilder()
        spec = parse(key)
        etype = spec.event_type
        tracked = set(builder.tracked_for(etype))
        parts: dict[str, str | None] = {}
        for p in spec.present:
            name, _, cls = p.partition("=")
            parts[name] = cls or None
        classes = VALUE_KEYED_FIELDS.get(etype, {})

        out = []
        for ir in self.rules.values():
            if ir.rule.level < 1 or etype not in ir.event_types:
                continue
            if all(self._may_match(c, tracked, parts, classes) for c in ir.conditions):
                out.append(ir)
        return sorted(out, key=lambda ir: int(ir.rule.id))

    @staticmethod
    def _may_match(c: Condition, tracked: set[str], parts: dict[str, str | None],
                   classes: dict[str, dict[str, str]]) -> bool:
        if c.negate or c.field not in tracked:
            return True
        if c.field not in parts:
            return False                      # a required field is empty in this key
        cls, rx = parts[c.field], c.regex
        if cls is None or rx is None:
            return True
        if cls == OTHER:
            return not any(rx.search(name) for name in classes.get(c.field, {}))
        return bool(rx.search(cls))

    def untracked_fields(self, builder: KeyBuilder | None = None) -> dict[str, set[str]]:
        """Fields that alerting rules read but the key map does not track, by event type."""
        builder = builder or KeyBuilder()
        gaps: dict[str, set[str]] = {}
        for ir in self.rules.values():
            if ir.rule.level < 1:
                continue
            for et in ir.event_types:
                tracked = set(builder.tracked_for(et))
                for c in ir.conditions:
                    if c.field not in tracked:
                        gaps.setdefault(et, set()).add(c.field)
        return gaps


def build_index(rules: dict[str, Rule]) -> RuleIndex:
    return RuleIndex(rules)
