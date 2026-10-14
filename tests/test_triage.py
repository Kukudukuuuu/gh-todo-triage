"""Tests cross module Interfaces only: triage(), to_tickets(), write_markdown(), adapters."""
import json

from typer.testing import CliRunner

from triage.classify import triage
from triage.cli import app
from triage.render import write_markdown
from triage.slice import to_tickets
from triage.sources import from_gh_json, from_paste

runner = CliRunner()


def test_roles_fire():
    assert triage({"title": "Crash on save", "body": "Steps to repro: open, save. Expected ok, actual crash."})["role"] == "ready-for-agent"
    assert triage({"title": "Dup of #12", "body": "Same as #12, duplicate report here."})["role"] == "wontfix"
    assert triage({"title": "It broke?", "body": "What version fixes this? Which OS?"})["role"] == "needs-info"
    assert triage({"title": "x", "body": "y"})["role"] == "needs-info"
    assert triage({"title": "RFC: new API shape", "body": "Should we adopt this design? Decision needed."})["role"] == "ready-for-human"
    assert triage({"title": "Please decide X", "body": "Team, decide the default for the new flag please."})["role"] == "ready-for-human"
    assert triage({"title": "Dark mode please", "body": "Would love a dark theme option."})["role"] == "needs-triage"
    assert triage({"title": "Crash", "body": "Steps:\n1. open\n2. save\nExpected ok."})["role"] == "ready-for-agent"


def test_tie_prefers_safer_role():
    v = triage({"title": "Repro unclear?", "body": "What are the steps? Which version shows the error log?"})
    assert v["role"] == "needs-info"


def test_gh_adapter():
    raw = json.dumps([{"number": 3, "title": "Bug", "body": "Steps to repro: x. Expected y, actual z."}])
    issues = from_gh_json(raw)
    assert issues == [{"id": "3", "title": "Bug", "body": "Steps to repro: x. Expected y, actual z."}]


def test_gh_adapter_rejects():
    for bad in ["not json", '{"a": 1}']:
        try:
            from_gh_json(bad)
        except ValueError:
            continue
        raise AssertionError("should raise " + bad)


def test_paste_adapter():
    issues = from_paste("### Crash on save\nSteps to repro: x. Expected y, actual z.\n### Typo\nFix label.")
    assert [i["title"] for i in issues] == ["Crash on save", "Typo"]
    assert from_paste("- dark mode\n- crash")[0]["title"] == "dark mode"


def test_slice_orders_blockers_first():
    tickets = to_tickets([
        {"title": "Add dark mode toggle", "body": "Add toggle."},
        {"title": "Fix CI setup", "body": "CI is red."},
        {"title": "Add login tests", "body": "Cover login."},
    ])
    titles = [t["title"] for t in tickets]
    assert titles[0] == "Fix CI setup"
    assert titles[-1] == "Add login tests"
    assert tickets[1]["blocked_by"] == ["Fix CI setup"]
    assert "Fix CI setup" in tickets[-1]["blocked_by"]
    assert tickets[0]["blocked_by"] == []  # fixes are the frontier


def test_render_template():
    files = write_markdown(to_tickets([{"title": "Fix CI setup", "body": "CI red."}]), "demo")
    assert list(files) == [".scratch/demo/issues/01-fix-ci-setup.md"]
    text = files[".scratch/demo/issues/01-fix-ci-setup.md"]
    assert "**Status:** ready-for-agent" in text and "- [ ]" in text


def test_cli_triage_json():
    raw = json.dumps([{"number": 1, "title": "Crash", "body": "Steps to repro: a. Expected b, actual c."}])
    res = runner.invoke(app, ["triage", "--json"], input=raw)
    assert res.exit_code == 0, res.output
    assert json.loads(res.output)[0]["role"] == "ready-for-agent"


def test_cli_to_tickets_skips_non_ready(tmp_path):
    raw = json.dumps([
        {"number": 1, "title": "Crash on save", "body": "Steps to repro: open. Expected ok, actual boom."},
        {"number": 2, "title": "Dark?", "body": "Would love it."},
    ])
    import os
    p = os.path.join(str(tmp_path), "in.json")
    open(p, "w").write(raw)
    res = runner.invoke(app, ["to-tickets", p, "--feature", "demo", "--out-dir", str(tmp_path)])
    assert res.exit_code == 0, res.output
    assert "1 tickets" in res.output and "1 non-ready skipped" in res.output
