"""The gate needs its own tests, because it is the thing that runs the others.

`tools/no-mistakes` gates every push (CLAUDE.md §7) and had no coverage at all.
It then shipped broken twice in a row, both times in the same way: the intent
id could not be read from the right commit. First because a `pull_request`
checkout is a merge commit whose subject is GitHub's rather than the author's,
and second because the fix added a ref parameter to the flag and to
`commit_subject` but not to the call between them.

Both are the sort of mistake a test catches in a second and a careful reading
misses twice. CI caught them instead, which is the argument for CI — but a
verification tool with no verification of its own is the wrong place to be
relying on that.

These tests cover the parsing surface only. Whether `ruff` and `pytest`
actually run is checked by the gate running.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "tools" / "no-mistakes"


def _gate_module():
    """Import the extensionless script as a module."""
    spec = importlib.util.spec_from_loader(
        "no_mistakes", importlib.machinery.SourceFileLoader("no_mistakes", str(GATE))
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # @dataclass resolves its own module out of sys.modules, so register first.
    sys.modules["no_mistakes"] = module
    spec.loader.exec_module(module)
    return module


gate = _gate_module()


# --- what counts as an intent id --------------------------------------------


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("S-4: commitment register and hash-chained AR ledger", "S-4"),
        ("§7: run the gate in CI", "§7"),
        ("D-11: settle the compute window", "D-11"),
        ("Q8: resident model on one card", "Q8"),
        ("A-4 tighten the action tier matrix", "A-4"),
        ("ar_01M04CRG: chase the Henderson figures", "ar_01M04CRG"),
        ("S4: the hyphen is optional", "S4"),
    ],
)
def test_an_intent_id_is_found_in_a_real_subject(subject, expected):
    assert gate.intent_in(subject) == expected


def test_a_qualified_section_reference_yields_the_section_alone():
    """A known asymmetry between the two ways of supplying an intent.

    `--intent "BUILD_BRIEF §3.2"` is accepted, because INTENT matches the
    qualified form. `--intent-from-commit` cannot ever return it: `intent_in`
    splits on whitespace before matching, so the document name and the section
    are separate tokens and only the section matches.

    Left as it is rather than fixed. `§3.2` is a valid intent and points at the
    same place, and making the tokenizer reassemble multi-word ids would mean
    guessing at where an id ends inside a sentence. Recorded here so it is a
    known shape rather than a surprise.
    """
    assert gate.intent_in("BUILD_BRIEF §3.2: coverage instrument") == "§3.2"
    assert gate.INTENT.match("BUILD_BRIEF §3.2")


@pytest.mark.parametrize(
    "subject",
    [
        "fix the thing",
        "deploy: target Artifact Registry omniscientai-repo/web-app",
        "Merge c6a7d8e into 65e9103",  # the pull_request checkout, twice shipped
        "",
        "wip",
        "bump deps",
    ],
)
def test_a_subject_without_an_intent_id_yields_none(subject):
    assert gate.intent_in(subject) is None


# --- reading the subject off a named commit ---------------------------------


def test_commit_subject_defaults_to_head():
    expected = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert gate.commit_subject() == expected


def _commit_with_an_intent() -> str | None:
    """A commit in the fetched history whose subject carries an intent id.

    Found rather than hardcoded, and HEAD is never assumed to be one. On a
    `pull_request` run HEAD is the merge commit Actions built, whose subject is
    "Merge <head> into <base>" and carries nothing — an earlier version of this
    file assumed otherwise and turned CI red on a tree that was fine.
    """
    log = subprocess.run(
        ["git", "log", "--format=%H%x00%s", "-20"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if log.returncode != 0:
        return None
    for line in log.stdout.splitlines():
        sha, _, subject = line.partition("\0")
        if gate.intent_in(subject):
            return sha
    return None


def test_commit_subject_reads_the_ref_it_is_given():
    """The bug that shipped: the ref reached the flag but never the call."""
    revs = subprocess.run(
        ["git", "rev-list", "-2", "HEAD"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split()
    if len(revs) < 2:
        pytest.skip("shallow history: no second commit to distinguish from HEAD")
    assert gate.commit_subject(revs[1]) != gate.commit_subject(revs[0])


def test_an_unknown_ref_is_empty_rather_than_an_exception():
    assert gate.commit_subject("no-such-ref-here") == ""


# --- the flag plumbing, end to end ------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the gate with `--intent-only`, which resolves the intent and stops.

    It cannot be the full gate: the gate runs pytest, and pytest would run this
    file, which would invoke the gate. `--intent-only` exists partly for that
    reason and partly because a commit-msg hook wants the same answer fast.
    """
    return subprocess.run(
        [sys.executable, str(GATE), "--intent-only", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_intent_from_commit_uses_the_ref_argument_not_head():
    """End to end, because the unit pieces were both correct while the wiring was not.

    `--intent-from-commit <ref>` must report the intent of *that* commit. The
    shipped bug passed every unit check — the flag accepted a ref and
    `commit_subject` accepted a ref — and still read HEAD, because nothing
    connected them. Only a test that spans both catches it.
    """
    sha = _commit_with_an_intent()
    if sha is None:
        pytest.skip("no commit in the fetched history carries an intent id")

    named = _run("--intent-from-commit", sha)
    assert named.returncode == 0, named.stderr
    assert named.stdout.strip() == gate.intent_in(gate.commit_subject(sha))

    # And the ref genuinely selects: a commit with no intent must fail even
    # when HEAD has one, and vice versa. Whichever way round this checkout is,
    # the two refs must not produce the same answer.
    head = _run("--intent-from-commit")
    if gate.commit_subject("HEAD") != gate.commit_subject(sha):
        assert (head.returncode, head.stdout.strip()) != (
            named.returncode,
            named.stdout.strip(),
        ), "HEAD and a different named ref resolved identically — the ref is ignored"


def test_intent_only_runs_no_checks_and_writes_no_log():
    """It is a parser, not a gate. A run it did not perform must not be logged."""
    log = ROOT / ".no-mistakes" / "runs.jsonl"
    sentinel = "Q97"  # nothing else ever runs under this intent

    def entries() -> int:
        if not log.exists():
            return 0
        # Counted by intent rather than by comparing the whole file: a real
        # gate run in another process appends here too, and this test should
        # fail for the reason it names rather than for someone else's write.
        return sum(1 for line in log.read_text(encoding="utf-8").splitlines() if sentinel in line)

    before = entries()
    result = _run("--intent", sentinel)

    assert result.returncode == 0
    assert result.stdout.strip() == sentinel
    assert entries() == before, "--intent-only appended to the run log"


def test_a_commit_with_no_intent_id_fails_the_gate():
    """The other half of §7: the commit convention is machine-checked."""
    result = _run("--intent-from-commit", "65e9103")
    assert result.returncode == 2
    assert "no intent id in the commit subject" in result.stderr
    assert "65e9103" in result.stderr, "say which commit was read"


def test_neither_intent_flag_is_an_error():
    result = _run()
    assert result.returncode != 0
    assert "--intent" in result.stderr


def test_an_unrecognisable_intent_is_refused():
    result = _run("--intent", "because-i-said-so")
    assert result.returncode == 2
    assert "not a recognisable id" in result.stderr
