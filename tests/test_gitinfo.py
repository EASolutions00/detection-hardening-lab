"""Tests for the code version recorded in each run (outside review, point 12; DECISIONS 2026-11-28).

A small real git repository is made in a temporary folder, so these tests need git on the PATH.

    .venv/Scripts/python.exe -m pytest tests -v
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from telos.gitinfo import code_version, describe

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True)
    return p.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    for folder in ("src", "lab", "docs"):
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "f.txt").write_text("one\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


def test_a_clean_repository_gives_its_short_commit_and_no_change(repo):
    assert code_version(repo) == (git(repo, "rev-parse", "--short", "HEAD"), False)


def test_an_edited_file_under_src_or_lab_counts_as_a_change(repo):
    (repo / "src" / "f.txt").write_text("two\n")
    assert code_version(repo)[1] is True
    git(repo, "checkout", "--", "src")
    (repo / "lab" / "f.txt").write_text("two\n")
    assert code_version(repo)[1] is True


def test_a_new_file_not_yet_committed_under_src_counts_as_a_change(repo):
    (repo / "src" / "new.py").write_text("x = 1\n")
    assert code_version(repo)[1] is True


def test_a_change_outside_src_and_lab_does_not_count(repo):
    (repo / "docs" / "f.txt").write_text("two\n")
    assert code_version(repo)[1] is False


def test_a_folder_that_is_not_a_repository_gives_unknown(tmp_path):
    assert code_version(tmp_path) == ("unknown", None)


def test_describe_says_what_is_known():
    assert describe("abc1234", False) == "abc1234"
    assert describe("abc1234", True) == "abc1234 (files changed since)"
    assert describe("abc1234", None) == "abc1234"
    assert describe(None, None) == "not recorded"
    assert describe("unknown", None) == "unknown"
