import os
from pathlib import Path
from unittest.mock import patch

import pytest

from intaglio.processor_core import (
    _iter_files,
    _should_proceed,
    _warn_about_fallback_date,
    process_posts,
)


def test_should_proceed_logic(tmp_path):
    src = tmp_path / "source.md"
    dest = tmp_path / "dest.md"
    src.touch()

    assert _should_proceed(src, dest, force=False) == "Creating"

    dest.touch()

    os.utime(src, (100, 100))
    os.utime(dest, (200, 200))
    assert _should_proceed(src, dest, force=False) is False

    assert _should_proceed(src, dest, force=True) == "Force Updating"

    os.utime(src, (300, 300))
    assert _should_proceed(src, dest, force=False) == "Updating"


@pytest.fixture
def mock_files_map():
    return {
        "Post A": {"source_path": Path("a.md"), "dest_path": Path("out/a.md")},
        "Post B": {"source_path": Path("b.md"), "dest_path": Path("out/b.md")},
    }


def test_iter_files_yields_all_by_default(mock_files_map):
    with patch("intaglio.processor_core.frontmatter.load", return_value="dummy_post"):
        results = list(_iter_files(mock_files_map, only_file=None))

    assert len(results) == 2

    assert results[0][0] == Path("a.md")


def test_iter_files_filters_single_file(mock_files_map):
    with patch("intaglio.processor_core.frontmatter.load", return_value="dummy_post"):
        results = list(_iter_files(mock_files_map, only_file="Post B.md"))

    assert len(results) == 1
    assert results[0][0] == Path("b.md")


class TestFallbackDateNotice:
    def _post(self, **metadata):
        import frontmatter

        return frontmatter.Post("body", **metadata)

    def test_notices_a_post_with_no_date(self, capsys):
        _warn_about_fallback_date(self._post(), Path("2026-01-01-hello.md"))

        out = capsys.readouterr().out
        assert "no date in frontmatter" in out
        # the suggested line must be copy-pasteable, i.e. carry the date used
        assert "`date: 2026-01-01`" in out

    def test_stays_quiet_when_the_date_is_explicit(self, capsys):
        _warn_about_fallback_date(
            self._post(date="2026-01-01"), Path("2026-01-01-hello.md")
        )

        assert capsys.readouterr().out == ""

    def test_fires_during_a_dry_run(self, tmp_path, capsys):
        vault, posts = tmp_path / "vault", tmp_path / "_posts"
        vault.mkdir()
        (vault / "hello.md").write_text("---\nshare: true\n---\n\nBody.\n")

        files = {
            "hello": {
                "source_path": vault / "hello.md",
                "dest_path": posts / "2026-01-01-hello.md",
            }
        }
        process_posts(files, cfg=None, dry=True, layout="post", force=False)

        assert "no date in frontmatter" in capsys.readouterr().out
