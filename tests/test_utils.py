from pathlib import Path
from unittest.mock import patch

import pytest

from intaglio.utils import (
    _get_dest_fpath,
    get_valid_files,
    shield_content,
    shield_liquid,
    slugify,
    unshield,
)


class TestSlugify:
    @pytest.mark.parametrize(
        "name, expected",
        [
            ("My New Post", "my-new-post"),
            ("Hello   World", "hello-world"),
            ("C++ Programming", "c-programming"),
            ("File_Name_With_Underscores", "file_name_with_underscores"),
            ("---Trim Dashes---", "trim-dashes"),
        ],
    )
    def test_slugify(self, name, expected):
        assert slugify(name) == expected


class TestShielding:
    def test_shield_code_blocks(self, postify):
        post = postify(
            "```python\nprint(1)\n```\n\n~~~python\nprint(2)\n~~~\n`inline_code`"
        )
        post, stash = shield_content(post, mode="code")

        assert "\x00FENCE_0\x00" in post.content
        assert "\x00FENCE_1\x00" in post.content
        assert "\x00CODE_2\x00" in post.content

        assert "print(1)" not in post.content
        assert "print(2)" not in post.content
        assert "inline_code" not in post.content

        assert stash["\x00FENCE_0\x00"] == "```python\nprint(1)\n```"
        assert stash["\x00FENCE_1\x00"] == "~~~python\nprint(2)\n~~~"
        assert stash["\x00CODE_2\x00"] == "`inline_code`"

    def test_shield_urls(self, postify):
        content = "https://google.com"
        post = postify(content)
        post, stash = shield_content(post, mode="url")

        assert "\x00URL_0\x00" == post.content
        assert stash["\x00URL_0\x00"] == "https://google.com"

    def test_shield_math(self, postify):
        post = postify("$x$\n$$y$$\n$$\nz\n$$")
        post, stash = shield_content(post, mode="math")

        assert "\x00MATH_0\x00" in post.content
        assert "\x00MATH_1\x00" in post.content
        assert "\x00MATH_2\x00" in post.content
        assert stash["\x00MATH_0\x00"] == "$x$"
        assert stash["\x00MATH_1\x00"] == "$$y$$"
        assert stash["\x00MATH_2\x00"] == "$$\nz\n$$"

    def test_shield_raise_error_on_unknown(self, postify):
        post = postify("")
        with pytest.raises(ValueError):
            post, _ = shield_content(post, mode="?")

    def test_unshield_restores_content(self, postify):
        post = postify("Check \x00URL_0\x00.")
        stash = {"\x00URL_0\x00": "https://google.com"}
        unshield(post, stash)

        assert post.content == "Check https://google.com."

    def test_unshield_with_convert_func(self, postify):
        post = postify("Code: \x00CODE_0\x00")
        stash = {"\x00CODE_0\x00": "my_code"}

        def converter(text):
            return text.upper()

        unshield(post, stash, convert_func=converter)

        assert post.content == "Code: MY_CODE"

    def test_liquid_is_shield(self, postify):
        assert shield_liquid("{{ hi }}") == "{% raw %}{{ hi }}{% endraw %}"


class TestFileScanning:
    @pytest.fixture
    def mini_vault(self, tmp_path):
        vault = tmp_path / "Vault"
        vault.mkdir()

        p1 = vault / "post1.md"
        p1.write_text("---\nshare: true\ntitle: Post 1\n---\nContent", encoding="utf-8")

        p2 = vault / "private.md"
        p2.write_text(
            "---\nshare: false\ntitle: Secret\n---\nContent", encoding="utf-8"
        )

        p3 = vault / "bad.md"
        p3.write_text("Just text", encoding="utf-8")

        p4 = vault / "image.png"
        p4.write_text("binary", encoding="utf-8")

        return vault

    def test_get_valid_files_filters_correctly(self, mini_vault, tmp_path):
        post_dir = tmp_path / "output"

        with patch("intaglio.utils._get_dest_fpath", return_value=Path("out/post1.md")):
            results = get_valid_files(mini_vault, post_dir)

        assert "post1" in results
        assert "private" not in results
        assert "bad" not in results
        assert "image" not in results

        assert results["post1"]["source_path"] == mini_vault / "post1.md"

    def test_output_dir_is_not_scanned(self, tmp_path):
        vault = tmp_path / "vault"
        posts = vault / "_posts"
        posts.mkdir(parents=True)
        (vault / "note.md").write_text("---\nshare: true\n---\nx\n")
        (posts / "2026-01-01-note.md").write_text(
            "---\nshare: true\ngenerator: intaglio\n---\nx\n"
        )

        result = get_valid_files(vault, posts)

        assert list(result) == ["note"]


class TestDestPathLogic:
    def test_uses_date_from_frontmatter(self, postify):
        post = postify("cnt", metadata={"date": "2025-05-05"})
        source_path = Path("My Post.md")
        post_dir = Path("out")

        result = _get_dest_fpath(post, source_path, post_dir)

        assert result.name == "2025-05-05-my-post.md"

    def test_falls_back_to_creation_time_if_no_date(self, postify):
        post = postify("cnt")
        source_path = Path("My Post.md")
        post_dir = Path("out")

        with patch("intaglio.utils._get_creation_time", return_value="2020-01-01"):
            result = _get_dest_fpath(post, source_path, post_dir)

        assert result.name == "2020-01-01-my-post.md"

    def test_cleans_existing_date_prefix_from_filename(self, postify):
        post = postify("cnt", metadata={"date": "2025-05-05"})

        source_path = Path("2022-01-01 My Post.md")
        post_dir = Path("out")

        result = _get_dest_fpath(post, source_path, post_dir)

        assert result.name == "2025-05-05-my-post.md"
