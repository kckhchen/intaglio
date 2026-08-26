import pytest

from intaglio.process_math import _fix_math_id, process_math


class TestMathSyntax:
    @pytest.mark.parametrize(
        "input, expected",
        [
            ("Value is $x=2$.", r"Value is \\(x=2\\)."),
            (
                "Text $$E=mc^2$$ Text",
                "\n$$E=mc^2$$\n",
            ),
            ("$$\nE=mc^2\n$$", "$$\nE=mc^2\n$$"),
            (
                "$$ x^2 $$ {: #secid1}",
                "$$ x^2 $$\n{: #secid1}",
            ),
        ],
    )
    def test_math_syntax_transformation(self, input, expected, postify):
        post = postify(input)
        result = process_math(post, "inject_cdn")
        assert expected in result.content


class TestIgnoreInvalidDollars:
    @pytest.mark.parametrize(
        "input", [r"\$50", r"$50", r"$50 and $60", r"$ 50 and$ 60"]
    )
    def test_ignores_invalid_dollars(self, postify, input):
        post = postify(input)
        result = process_math(post, "inject_cdn")

        assert "<script" not in result.content
        assert result.content == input


class TestMathInjection:
    def test_mode_inject_cdn_appends_script(self, postify, monkeypatch):
        post = postify("$1+1$")
        result = process_math(post, "inject_cdn")

        assert '<script id="MathJax-script"' in result.content

    def test_mode_metadata_sets_frontmatter(self, postify, monkeypatch):
        post = postify("$1+1$")
        result = process_math(post, "metadata")
        assert "<script" not in result.content
        assert result["math"] is True

    def test_ignores_posts_without_math(self, postify):
        post = postify("no math")
        result = process_math(post, "inject_cdn")

        assert "<script" not in result.content


class TestMathId:
    def test_math_id_fixed(self, postify):
        inputs = [
            "$$x$$ {: #secid1}",
            "$$x$$  {: #secid1}",
            "$$x$$\n{: #secid1}",
            "$$x$$\n\n{: #secid1}",
        ]
        for input in inputs:
            assert _fix_math_id(postify(input)).content == "$$x$$\n{: #secid1}"
