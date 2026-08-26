from pathlib import Path

import frontmatter
import pytest

from intaglio.callout_styles import CALLOUT_CSS
from intaglio.config import Config
from intaglio.fs_ops import copy_images, ensure_css_exists, setup_dir
from intaglio.process_images import process_embedded_images


@pytest.fixture
def css_mock(tmp_path, monkeypatch):
    return Config(vault_dir=tmp_path / "vault", jekyll_dir=tmp_path)


@pytest.fixture
def vault_images(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "chart.png").write_bytes(b"IMG")
    (vault / "Photo.JPG").write_bytes(b"IMG2")
    return {"chart.png": vault / "chart.png", "photo.jpg": vault / "Photo.JPG"}


def test_setup_dir_creates_folders(tmp_path, capsys):
    post_dir = tmp_path / "out/posts"
    img_dir = tmp_path / "out/assets/img"

    assert not post_dir.exists()

    setup_dir([post_dir, img_dir], dry=False)

    assert post_dir.exists()
    assert img_dir.exists()

    captured = capsys.readouterr()
    assert "Destination folder not found, creating" in captured.out


def test_setup_dir_respects_dry_run(tmp_path):
    post_dir = tmp_path / "posts"
    img_dir = tmp_path / "img"

    setup_dir([post_dir, img_dir], dry=True)

    assert not post_dir.exists()


def test_ensure_css_exists_writes_file(css_mock, tmp_path):
    css_name = "test-callouts.css"
    expected_path = tmp_path / "_includes" / css_name

    ensure_css_exists(css_name, css_mock, dry=False)

    assert expected_path.exists()

    assert expected_path.read_text(encoding="utf-8") == CALLOUT_CSS


def test_ensure_css_skips_if_already_exists(tmp_path, css_mock, capsys):
    css_name = "existing.css"
    includes = tmp_path / "_includes"
    includes.mkdir()

    (includes / css_name).write_text("OLD CONTENT", encoding="utf-8")

    ensure_css_exists(css_name, css_mock, dry=False)

    assert (includes / css_name).read_text(encoding="utf-8") == "OLD CONTENT"

    captured = capsys.readouterr()
    assert "Creating default callout CSS" not in captured.out


def test_external_image_url_does_not_crash(tmp_path):
    post = frontmatter.Post("![](https://cdn.example.com/x.png)")
    copy_images(post, {}, tmp_path)


HOSTILE = [
    pytest.param("![](https://cdn.example.com/x.png)", id="external-url"),
    pytest.param("![](\x00URL_0\x00)", id="shielded-url"),
    pytest.param("![](//cdn.example.com/x.png)", id="protocol-relative"),
    pytest.param("![[missing.png]]", id="not-in-vault"),
    pytest.param("![[note.pdf]]", id="non-image"),
    pytest.param("![[]]", id="empty-embed"),
    pytest.param("", id="empty-content"),
]


class TestCopyImages:
    @pytest.mark.parametrize("content", HOSTILE)
    def test_copy_images_skips_unresolvable(self, tmp_path, postify, content):
        out = tmp_path / "out"
        out.mkdir()
        copy_images(postify(content), {}, out)
        assert list(out.iterdir()) == []

    @pytest.mark.parametrize(
        "content, expected",
        [
            ("![[chart.png]]", ["chart.png"]),
            ("![[chart.png|300x200]]", ["chart.png"]),
            ("![架構圖|400](chart.png)", ["chart.png"]),
            ("![[photo.JPG]]", ["photo.JPG"]),
            ("![[chart.png]] ![[missing.png]]", ["chart.png"]),
        ],
    )
    def test_copy_images_writes_expected(
        self, tmp_path, postify, vault_images, content, expected
    ):
        out = tmp_path / "out"
        out.mkdir()
        copy_images(postify(content), vault_images, out)
        assert sorted(p.name for p in out.iterdir()) == expected

    @pytest.mark.parametrize(
        "content",
        [
            "![[chart.png]]",
            "![[missing.png]]",
            "![](https://a/b.png)",
            "![[note.pdf]]",
            "![](\x00URL_0\x00)",
            "![架構圖|400](chart.png)",
        ],
    )
    def test_copy_and_rewrite_agree(self, tmp_path, postify, vault_images, content):
        out = tmp_path / "out"
        out.mkdir()

        copy_images(postify(content), vault_images, out)
        copied = bool(list(out.iterdir()))

        rewritten = (
            "{% link"
            in process_embedded_images(
                postify(content), vault_images, Path("assets/images/obsidian")
            ).content
        )

        assert copied == rewritten
