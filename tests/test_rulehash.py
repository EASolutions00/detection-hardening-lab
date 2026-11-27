"""Tests for the rule-export hash (outside review, point 12; DECISIONS 2026-11-28).

The hash is SHA256 over the lines "file SHA256, two spaces, relative path", sorted by path, each ending in a line
feed. The first test pins the line format; the second pins the hash of those lines; the last reproduces the value
that DECISIONS pinned on 2026-11-13 from the real export, when it is on this disk.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.rulehash import file_lines, rule_folder_sha256

REAL_EXPORT = Path(__file__).parent.parent / "data" / "rules" / "wazuh-4.14.7"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tiny(root: Path) -> Path:
    """The same shape as the real export: ruleset/rules and etc/rules."""
    (root / "ruleset" / "rules").mkdir(parents=True)
    (root / "etc" / "rules").mkdir(parents=True)
    (root / "ruleset" / "rules" / "0010-a.xml").write_bytes(b"<a/>")
    (root / "ruleset" / "rules" / "0020-b.xml").write_bytes(b"<b/>\r\n")
    (root / "etc" / "rules" / "local_rules.xml").write_bytes(b"<l/>")
    return root


def test_the_lines_are_file_hash_two_spaces_relative_path_sorted_by_path(tmp_path):
    root = tiny(tmp_path)
    crlf = b"<b/>\r\n"
    assert file_lines(root) == [
        f"{sha(b'<l/>')}  etc/rules/local_rules.xml",
        f"{sha(b'<a/>')}  ruleset/rules/0010-a.xml",
        f"{sha(crlf)}  ruleset/rules/0020-b.xml",
    ]


def test_the_hash_is_the_sha256_of_those_lines_each_ending_in_a_line_feed(tmp_path):
    root = tiny(tmp_path)
    crlf = b"<b/>\r\n"
    lines = [f"{sha(b'<l/>')}  etc/rules/local_rules.xml\n",
             f"{sha(b'<a/>')}  ruleset/rules/0010-a.xml\n",
             f"{sha(crlf)}  ruleset/rules/0020-b.xml\n"]
    assert rule_folder_sha256(root) == sha("".join(lines).encode("utf-8"))


def test_the_order_in_which_files_were_made_does_not_matter(tmp_path):
    for name, order in (("a", ("x.xml", "y.xml")), ("b", ("y.xml", "x.xml"))):
        (tmp_path / name).mkdir()
        for n in order:
            (tmp_path / name / n).write_bytes(n.encode())
    assert rule_folder_sha256(tmp_path / "a") == rule_folder_sha256(tmp_path / "b")


def test_one_changed_byte_a_renamed_file_or_an_extra_file_changes_the_hash(tmp_path):
    base = rule_folder_sha256(tiny(tmp_path / "base"))
    changed = tiny(tmp_path / "changed")
    (changed / "ruleset" / "rules" / "0010-a.xml").write_bytes(b"<a />")
    renamed = tiny(tmp_path / "renamed")
    (renamed / "ruleset" / "rules" / "0010-a.xml").rename(renamed / "ruleset" / "rules" / "0011-a.xml")
    extra = tiny(tmp_path / "extra")
    (extra / "etc" / "rules" / "more.xml").write_bytes(b"<m/>")
    others = {rule_folder_sha256(p) for p in (changed, renamed, extra)}
    assert len(others) == 3 and base not in others


def test_a_missing_folder_is_refused_and_not_hashed_as_empty(tmp_path):
    with pytest.raises(ValueError, match="not a folder"):
        rule_folder_sha256(tmp_path / "nope")


@pytest.mark.skipif(not REAL_EXPORT.is_dir(), reason="the rule export is on the author's disk only (data/rules is not in git)")
def test_the_value_pinned_on_2026_11_13_is_the_hash_of_the_real_export():
    """Reproduced 2026-11-28 (WORKLOG): 169 files, 168 in ruleset/rules and 1 in etc/rules."""
    from telos.catalog import parameters
    assert len(file_lines(REAL_EXPORT)) == 169
    assert rule_folder_sha256(REAL_EXPORT) == parameters("S")["rule_folder_sha256"]
