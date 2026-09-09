import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Bash only runs on macOS"
)


@pytest.fixture
def cli(tmp_path):
    # temp vault + jekyll dir to run the intaglio CLI"""

    class CLI:
        def __init__(self):
            self.vault = tmp_path / "vault"
            self.jekyll = tmp_path / "jekyll"
            self.posts = self.jekyll / "_posts"
            self.images = self.jekyll / "assets/images/obsidian"
            for d in (self.vault, self.posts, self.images, self.jekyll / "_includes"):
                d.mkdir(parents=True)

        def note(self, name, body="Content", share=True, date="2013-01-01"):
            fm = "---\n"
            if share:
                fm += "share: true\n"
            if date:
                fm += f"date: {date}\n"
            (self.vault / name).write_text(fm + "---\n" + body, encoding="utf-8")

        def run(self, *args, stdin="", vault=None, jekyll=None):
            env = {
                **os.environ,
                "VAULT_DIR": str(vault if vault is not None else self.vault),
                "JEKYLL_DIR": str(jekyll if jekyll is not None else self.jekyll),
                "POST_FOLDER": "_posts",
                "IMG_FOLDER": "assets/images/obsidian",
                "INCLUDES_FOLDER": "_includes",
                "MATH_RENDERING_MODE": "inject_cdn",
                "PREVENT_DOUBLE_BASEURL": "false",
            }
            return subprocess.run(
                [sys.executable, "-m", "intaglio", *args],
                cwd=REPO,
                env=env,
                input=stdin,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
                check=False,
            )

    return CLI()


REJECTED = [
    pytest.param(["update", "--dry"], id="update+dry"),
    pytest.param(["clean", "--dry"], id="clean+dry"),
    pytest.param(["update", "--only", "a.md"], id="update+only"),
    pytest.param(["clean", "--only", "a.md"], id="clean+only"),
    pytest.param(["run", "--nonexistent-flag"], id="unknown-flag"),
]


@pytest.mark.parametrize("args", REJECTED)
def test_invalid_flag_combos_are_rejected(cli, args):
    r = cli.run(*args)
    assert r.returncode == 2
    assert not list(cli.posts.iterdir())


def test_missing_vault_exits_nonzero(cli, tmp_path):
    r = cli.run("run", vault=tmp_path / "does-not-exist")
    assert r.returncode == 1
    assert "VAULT_DIR" in r.stdout + r.stderr


def test_only_with_unshared_file_fails_cleanly(cli):
    cli.note("unshared.md", share=False, date="2013-01-01")
    r = cli.run("run", "--only", "unshared.md")

    assert r.returncode != 0
    assert "Traceback" not in r.stderr
    assert not list(cli.posts.iterdir())


def test_dry_writes_nothing(cli):
    cli.note("a.md", date="2013-01-01")
    cli.run("run", "--dry")
    assert list(cli.posts.iterdir()) == []
    assert list(cli.images.iterdir()) == []
    assert not (cli.jekyll / "_includes" / "obsidian-callouts.html").exists()


def test_cleanup_abort_removes_nothing(cli):
    cli.note("a.md", date="2013-01-01")
    cli.run("run", "--force")
    cli.run("clean", stdin="n\n")
    assert (cli.posts / "2013-01-01-a.md").exists()


def test_running_twice_is_idempotent(cli):
    body = "$$x$$\n> [!note] Callout Title\n> Callout Content\n\n==highlight=="
    cli.note("a.md", body=body, date="2013-01-01")
    cli.run("run", "--force")
    first = {p.name: p.read_text() for p in cli.posts.iterdir()}
    cli.run("run", "--force")
    second = {p.name: p.read_text() for p in cli.posts.iterdir()}
    output = cli.posts / "2013-01-01-a.md"
    content = output.read_text()
    assert output.exists()
    assert "<script" in content
    assert "<mark>" in content
    assert r"{% include" in content
    assert first == second


# legacy flag-only form — drop these when rewrite_legacy() is removed


def test_legacy_flags_still_run_with_deprecation_warning(cli):
    cli.note("a.md", date="2013-01-01")
    r = cli.run("--dry")
    assert r.returncode == 0
    assert "deprecated" in r.stderr
    assert list(cli.posts.iterdir()) == []


def test_legacy_command_flags_cannot_be_combined(cli):
    r = cli.run("--cleanup", "--update")
    assert r.returncode == 2
    assert not list(cli.posts.iterdir())
