import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Bash only runs on macOS"
)


@pytest.fixture
def run_pipeline(tmp_path):
    def _run(body, *, date="2026-01-01", stem="note", args=("--force",), env=None):
        vault = tmp_path / "vault"
        site = tmp_path / "site"
        for d in (
            vault,
            site / "_posts",
            site / "_includes",
            site / "assets/images/obsidian",
        ):
            d.mkdir(parents=True, exist_ok=True)

        (vault / f"{stem}.md").write_text(
            f"---\nshare: true\ndate: {date}\n---\n{body}\n", encoding="utf-8"
        )

        full_env = {
            **os.environ,
            "VAULT_DIR": str(vault),
            "JEKYLL_DIR": str(site),
            "POST_FOLDER": "_posts",
            "IMG_FOLDER": "assets/images/obsidian",
            "INCLUDES_FOLDER": "_includes",
            "MATH_RENDERING_MODE": "inject_cdn",
            "PREVENT_DOUBLE_BASEURL": "false",
            **(env or {}),
        }

        r = subprocess.run(
            [sys.executable, "main.py", *args],
            cwd=REPO,
            env=full_env,
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            check=False,
        )
        assert r.returncode == 0, (
            f"main.py {' '.join(args)} exited {r.returncode}\n"
            f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
        )

        dest = site / "_posts" / f"{date}-{stem}.md"
        assert dest.exists(), f"Did not output {dest.name}\n{r.stdout}"
        return dest.read_text(encoding="utf-8")

    return _run


def fake_liquid(src):
    tok = re.compile(r"\{% raw %\}(.*?)\{% endraw %\}|\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)
    out, i = [], 0
    for m in tok.finditer(src):
        out.append(src[i : m.start()])
        if m.group(1) is not None:
            out.append(m.group(1))
        i = m.end()
    out.append(src[i:])
    return "".join(out)


@pytest.mark.parametrize(
    "body, must_survive",
    [
        pytest.param(
            "```yaml\n  token: ${{ secrets.X }}\n```",
            "${{ secrets.X }}",
            id="fenced-yaml",
        ),
        pytest.param(
            "fenced `{{ site.baseurl }}`",
            "`{{ site.baseurl }}`",
            id="inline-code",
        ),
        pytest.param(
            "```liquid\n{% if page.math %}yes{% endif %}\n```",
            "{% if page.math %}yes{% endif %}",
            id="liquid-tutorial",
        ),
        pytest.param(
            "$$\\frac{{a}}{{b}}$$",
            "\\frac{{a}}{{b}}",
            id="math-block",
        ),
        pytest.param(
            "$x_{{i}}$",
            "x_{{i}}",
            id="math-inline",
        ),
    ],
)
def test_liquid_survives_jekyll(run_pipeline, body, must_survive):
    rendered = fake_liquid(run_pipeline(body))
    assert must_survive in rendered, f"Liquid 把它吃掉了\n實際:\n{rendered}"


def test_prose_liquid_is_not_shielded(run_pipeline):
    out = run_pipeline("{{ baseurl }}")
    assert "{% raw %}" not in out
    assert "{{ baseurl }}" in out


def test_generated_liquid_is_not_shielded(run_pipeline):
    out = run_pipeline("see [[other]]")
    assert "{% raw %}{% link" not in out
    assert "{% raw %}{{ site.baseurl }}" not in out
