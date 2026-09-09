import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
ACTION = yaml.safe_load((REPO / "action.yml").read_text(encoding="utf-8"))


pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Bash only runs on macOS"
)


def step_script(name, inputs=None):
    step = next(s for s in ACTION["runs"]["steps"] if s.get("name") == name)
    script = step["run"]
    for key, value in (inputs or {}).items():
        script = script.replace(f"${{{{ inputs.{key} }}}}", str(value))
    script = re.sub(r"\$\{\{[^}]+\}\}", "", script)
    return script


def run_bash(script, cwd, env=None):
    return subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail"],
        input=script,
        cwd=cwd,
        text=True,
        capture_output=True,
        env={
            **os.environ,
            "GITHUB_OUTPUT": str(Path(cwd) / "_gh_output"),
            **(env or {}),
        },
        timeout=30,
        check=False,
    )


@pytest.fixture
def vault(tmp_path):
    v = tmp_path / "vault"
    v.mkdir()
    return v


def note(vault, name, share="true", date: str | None = "2026-01-15"):
    fm = "---\n"
    if share:
        fm += f"share: {share}\n"
    if date:
        fm += f"date: {date}\n"
    (vault / name).write_text(fm + "---\nContent\n", encoding="utf-8")


def test_date_check_passes_when_all_shared_notes_have_dates(vault):
    note(vault, "a.md")
    note(vault, "b.md")
    note(vault, "private.md", share=False, date=None)
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 0, r.stdout + r.stderr


def test_date_check_fails_on_missing_date(vault):
    note(vault, "ok.md")
    note(vault, "bad.md", date=None)
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 1
    assert "bad.md" in r.stdout


@pytest.mark.parametrize("spelling", ["true", "True", "TRUE", "yes", "on", '"true"'])
def test_date_check_covers_every_truthy_share_value(vault, spelling):
    # intaglio publishes anything YAML reads as true, so a guard that only knows
    # `share: true` lets dateless notes through with an unstable permalink
    note(vault, "bad.md", share=spelling, date=None)
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 1, f"share: {spelling} escaped the date check"
    assert "bad.md" in r.stdout


@pytest.mark.parametrize("spelling", ["false", "False", "no", "off"])
def test_date_check_leaves_unshared_spellings_alone(vault, spelling):
    note(vault, "private.md", share=spelling, date=None)
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 0, f"share: {spelling} should not be treated as shared"


def test_date_check_is_case_sensitive_about_the_key(vault):
    # frontmatter lookups are case-sensitive, so `Share:` is never published —
    # flagging it would fail runs over notes the tool ignores
    (vault / "odd.md").write_text("---\nShare: true\n---\nContent\n", encoding="utf-8")
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 0


def test_date_check_ignores_unshared_notes(vault):
    note(vault, "private.md", share=False, date=None)
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 0, "Notes without share: true should not stop process"


def test_date_check_on_empty_vault(vault):
    r = run_bash(step_script("Require explicit dates"), vault)
    assert r.returncode == 0, "Empty vault should not fail process"


@pytest.fixture
def site(tmp_path):
    s = tmp_path / "site"
    (s / "_posts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=s, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=s, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=s, check=True)
    (s / "_posts" / "2026-01-01-existing.md").write_text("---\n---\nx\n")
    subprocess.run(["git", "add", "-A"], cwd=s, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=s, check=True)
    return s


def read_output(site):
    p = site / "_gh_output"
    if not p.exists():
        return {}
    return dict(
        line.split("=", 1) for line in p.read_text().splitlines() if "=" in line
    )


def test_diff_reports_no_change(site):
    r = run_bash(step_script("Inspect changes", {"max-deletions": "10"}), site)
    assert r.returncode == 0
    assert read_output(site)["changed"] == "false"


def test_diff_reports_change(site):
    (site / "_posts" / "2026-02-02-new.md").write_text("---\n---\nnew\n")
    r = run_bash(step_script("Inspect changes", {"max-deletions": "10"}), site)
    assert r.returncode == 0, r.stdout + r.stderr
    out = read_output(site)
    assert out["changed"] == "true"
    assert out["deletions"].strip() == "0"


def test_diff_counts_deletions(site):
    (site / "_posts" / "2026-01-01-existing.md").unlink()
    _ = run_bash(step_script("Inspect changes", {"max-deletions": "10"}), site)
    assert read_output(site)["deletions"].strip() == "1"


def test_diff_warns_above_threshold(site):
    for i in range(6):
        f = site / "_posts" / f"2026-01-{i + 10}-x.md"
        f.write_text("---\n---\nx\n")
    subprocess.run(["git", "add", "-A"], cwd=site, check=True)
    subprocess.run(["git", "commit", "-qm", "more"], cwd=site, check=True)
    for i in range(6):
        (site / "_posts" / f"2026-01-{i + 10}-x.md").unlink()

    r = run_bash(step_script("Inspect changes", {"max-deletions": "3"}), site)
    assert r.returncode == 0, "Step should not fail"
    assert "::warning::" in r.stdout
