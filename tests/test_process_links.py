from pathlib import Path

import pytest

from intaglio.process_links import process_wikilinks


@pytest.fixture
def valid_files_map():
    return {
        "A Test Post": {
            "source_path": "",
            "dest_path": Path("_posts/a-test-post.md"),
        },
        "Another Post": {
            "source_path": "",
            "dest_path": Path("_posts/another-post.md"),
        },
    }


class TestProcessLinks:
    @pytest.mark.parametrize(
        "input, expected",
        [
            pytest.param(
                "[[A Test Post]]",
                "[A Test Post]({% link _posts/a-test-post.md %})",
                id="standard_wikilinks",
            ),
            pytest.param(
                "[[Fake Post]]", "Fake Post", id="returns_text_with_missing_target"
            ),
            pytest.param(
                "[[A Test Post|display]]",
                "[display]({% link _posts/a-test-post.md %})",
                id="wikilink_with_displayed_texts",
            ),
            pytest.param(
                "[display](A Test Post)",
                "[display]({% link _posts/a-test-post.md %})",
                id="standard_md_links",
            ),
            pytest.param(
                "[display](\x00URL_1\x00)",
                "[display](\x00URL_1\x00)",
                id="ignores_shielded_content",
            ),
            pytest.param(
                "[[#section 1]]", "[section 1](#section-1)", id="section_reference"
            ),
            pytest.param(
                "[[#section-1|Section One]]",
                "[Section One](#section-1)",
                id="section_reference_with_displayed_texts",
            ),
            pytest.param(
                "[[#^abcd|A block link]]",
                "[A block link](#secidabcd)",
                id="block_links",
            ),
            pytest.param(
                "[[Another Post#Section 1|Section one from another post]]",
                "[Section one from another post]({% link _posts/another-post.md %}#section-1)",
                id="section_link_to_another_post",
            ),
            pytest.param(
                "[[Another Post#^abcd|Block from another post]]",
                "[Block from another post]({% link _posts/another-post.md %}#secidabcd)",
                id="block_link_to_another_post",
            ),
            pytest.param("^12345", "{: #secid12345}", id="transforms_anchors"),
            pytest.param(
                "a paragraph ^12345",
                "a paragraph\n{: #secid12345}",
                id="puts_anchor_next_line_if_one_the_same_line",
            ),
            pytest.param(
                "[[A Test Post]] and [[Another Post]]",
                "[A Test Post]({% link _posts/a-test-post.md %}) and [Another Post]({% link _posts/another-post.md %})",
                id="multiple_links_same_line",
            ),
        ],
    )
    def test_process_wikilinks_scenarios(
        self, input, expected, valid_files_map, postify
    ):
        post = postify(input)
        result_post = process_wikilinks(post, valid_files_map, Path("_posts"), "False")
        assert result_post.content == expected
