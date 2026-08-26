import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
ACTION = REPO / "action.yml"


@pytest.fixture(scope="module")
def action():
    return yaml.safe_load(ACTION.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def raw():
    return ACTION.read_text(encoding="utf-8")


def test_every_referenced_input_exists(action, raw):
    declared = set(action["inputs"])
    referenced = set(re.findall(r"inputs\.([a-z0-9-]+)", raw))
    assert referenced <= declared, f"Undefined input: {sorted(referenced - declared)}"


def test_no_unused_inputs(action, raw):
    declared = set(action["inputs"])
    referenced = set(re.findall(r"inputs\.([a-z0-9-]+)", raw))
    assert declared <= referenced, f"Unused input: {sorted(declared - referenced)}"


def test_outputs_reference_existing_steps(action):
    ids = {s["id"] for s in action["runs"]["steps"] if "id" in s}
    for name, spec in action.get("outputs", {}).items():
        m = re.search(r"steps\.([\w-]+)\.outputs\.", spec["value"])
        assert m, f"output {name} didn't reference any step"
        assert m.group(1) in ids, (
            f"output {name} references to non-existent step id: {m.group(1)}"
        )


def test_every_run_step_declares_shell(action):
    for step in action["runs"]["steps"]:
        if "run" in step:
            assert "shell" in step, f"{step.get('name', '(unnamed)')} lacks a shell"


def test_both_repos_are_checked_out(action):
    checkouts = [
        s
        for s in action["runs"]["steps"]
        if str(s.get("uses", "")).startswith("actions/checkout")
    ]
    assert len(checkouts) == 2, f"2 checkouts expected, getting {len(checkouts)}"
    assert any("repository" in c.get("with", {}) for c in checkouts), (
        "Missing Jekyll repo checkout"
    )


def test_python_settings_are_passed_to_sync(action):
    expected = {
        "VAULT_DIR",
        "JEKYLL_DIR",
        "POST_FOLDER",
        "IMG_FOLDER",
        "INCLUDES_FOLDER",
        "MATH_RENDERING_MODE",
        "PREVENT_DOUBLE_BASEURL",
    }
    sync = next(s for s in action["runs"]["steps"] if s.get("id") == "sync")
    assert expected <= set(sync.get("env", {})), (
        f"Sync step missing: {sorted(expected - set(sync.get('env', {})))}"
    )


def test_config_keys_match_action_inputs():
    cfg = (REPO / "intaglio" / "config.py").read_text(encoding="utf-8")
    known = set(re.findall(r'^\s+"([A-Z_]+)",$', cfg, re.MULTILINE))
    action = yaml.safe_load(ACTION.read_text(encoding="utf-8"))
    sync = next(s for s in action["runs"]["steps"] if s.get("id") == "sync")
    assert known == set(sync.get("env", {})), (
        f"Only in config: {sorted(known - set(sync['env']))}, Only in action: {sorted(set(sync['env']) - known)}"
    )
