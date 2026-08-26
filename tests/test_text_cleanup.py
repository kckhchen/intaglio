from intaglio.text_cleanup import (
    _ensure_table_spacing,
    _process_frontmatter,
    _process_highlights,
    _strip_comments,
    text_cleanup,
)


class TestProcessFrontmatter:
    def test_h1_preserves_existing_metadata_title(self, postify):
        content = "# H1 Title"
        post = postify(content, metadata={"title": "Original Metadata Title"})
        result = _process_frontmatter(post)
        assert result["title"] == "Original Metadata Title"

    def test_h1_auto_add_titles(self, postify):
        post = postify("# H1 Title")
        assert _process_frontmatter(post)["title"] == "H1 Title"

    def test_auto_add_layout(self, postify):
        post = postify("")
        assert _process_frontmatter(post)["layout"] == "post"

    def test_preserve_post_layout(self, postify):
        post = postify("", metadata={"layout": "article"})
        assert _process_frontmatter(post)["layout"] == "article"

    def test_layout_observe_flag(self, postify):
        post = postify("")
        assert _process_frontmatter(post, layout="article")["layout"] == "article"

    def test_layout_frontmatter_take_precedence(self, postify):
        post = postify("", metadata={"layout": "article"})
        assert _process_frontmatter(post, layout="essay")["layout"] == "article"


class TestTextCleanup:
    def test_strip_comments(self, postify):
        post = postify("%%comment%%")
        assert "comment" not in _strip_comments(post)

    def test_strip_block_comments(self, postify):
        post = postify("%%\nblock comment\n%%")
        assert "block comment" not in _strip_comments(post)

    def test_process_highlights(self, postify):
        post = postify("==highlighted text==")
        assert _process_highlights(post).content == "<mark>highlighted text</mark>"

    def test_process_highlights_spare_setext_headings(self, postify):
        post = postify("Title\n========")
        assert _process_highlights(post).content == post.content

    def test_ensure_table_spacing_fixes_cramped_tables(self, postify):
        bad_markdown = "Preceding text\n| Header | Col |\n|---|---|\n| Val | Val |"
        post = postify(bad_markdown)
        result = _ensure_table_spacing(post)
        assert "Preceding text\n\n| Header |" in result.content


class TestTextCleanupFlow:
    def test_text_cleanup_orchestrator(self, postify):
        raw_text = """# Main Title

%% secret %%
Intro text.
==Important== point.
Table follows:
| A | B |
|---|---|
"""
        post = postify(raw_text)

        result = text_cleanup(post)

        assert result["title"] == "Main Title"
        assert "# Main Title" not in result.content
        assert "%% secret %%" not in result.content
        assert "<mark>Important</mark>" in result.content
        assert "follows:\n\n| A |" in result.content
