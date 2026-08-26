import re
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

REPO = Path(__file__).resolve().parent.parent


def _pyproject_dependencies():
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^dependencies = \[(.*?)^\]", text, re.MULTILINE | re.DOTALL)
    assert block, "could not find the dependencies array in pyproject.toml"
    return [Requirement(m) for m in re.findall(r'"([^"]+)"', block.group(1))]


def _pinned_requirements():
    pinned = {}
    for line in (REPO / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        req = Requirement(line)
        pinned[canonicalize_name(req.name)] = req
    return pinned


def test_every_runtime_dependency_is_pinned():
    missing = [
        dep.name
        for dep in _pyproject_dependencies()
        if canonicalize_name(dep.name) not in _pinned_requirements()
    ]
    assert not missing, (
        f"{missing} declared in pyproject.toml but absent from requirements.txt — "
        "the Action installs with --no-deps and would fail on import"
    )


@pytest.mark.parametrize("dep", _pyproject_dependencies(), ids=lambda d: d.name)
def test_pinned_version_satisfies_pyproject(dep):
    pinned = _pinned_requirements().get(canonicalize_name(dep.name))
    if pinned is None:
        pytest.skip("covered by test_every_runtime_dependency_is_pinned")

    versions = [s.version for s in pinned.specifier if s.operator == "=="]
    assert versions, f"{dep.name} is not pinned to an exact version"

    assert dep.specifier.contains(Version(versions[0])), (
        f"requirements.txt pins {dep.name}=={versions[0]}, which does not satisfy "
        f"'{dep}' in pyproject.toml"
    )
