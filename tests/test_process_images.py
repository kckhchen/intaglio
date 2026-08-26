from pathlib import Path

import pytest

from intaglio.process_images import process_embedded_images


@pytest.fixture
def img_map():
    return {
        "image.png": Path("/abs/path/to/vault/assets/image.png"),
        "photo.jpg": Path("/abs/path/to/vault/photos/photo.jpg"),
        "graphic.png": Path("/abs/path/to/graphic.png"),
    }


class TestProcessEmbeddedImages:
    @pytest.mark.parametrize(
        "input_text, expected_output, expected_width_attr",
        [
            (
                "![[image.png]]",
                "![]({{ site.baseurl }}{% link assets/image.png %})",
                None,
            ),
            (
                "![[image.png|300]]",
                '![]({{ site.baseurl }}{% link assets/image.png %}){: width="300" }',
                "300",
            ),
            (
                "![](image.png)",
                "![]({{ site.baseurl }}{% link assets/image.png %})",
                None,
            ),
            (
                "![500](image.png)",
                '![]({{ site.baseurl }}{% link assets/image.png %}){: width="500" }',
                "500",
            ),
            (
                "![[IMAGE.PNG]]",
                "![]({{ site.baseurl }}{% link assets/IMAGE.PNG %})",
                None,
            ),
        ],
    )
    def test_image_replacement_and_copy(
        self,
        input_text,
        expected_output,
        expected_width_attr,
        postify,
        img_map,
    ):
        post = postify(input_text)
        dest_folder = Path("assets")

        result = process_embedded_images(post, img_map, dest_folder)

        assert result.content == expected_output

    def test_keeps_tag_if_image_not_in_map(self, postify, img_map, capsys):
        post = postify("![[missing_file.png]]")
        dest_folder = Path("/out")

        result = process_embedded_images(post, img_map, dest_folder)

        assert result.content.strip() == "![[missing_file.png]]"

        captured = capsys.readouterr()
        assert "Warning: Image target not found" in captured.out
        assert "missing_file.png" in captured.out

    def test_ignores_non_image_extensions(self, postify, img_map):
        input_text = "![[document.pdf]]"
        post = postify(input_text)
        dest_folder = Path("/out")

        result = process_embedded_images(post, img_map, dest_folder)

        assert result.content == "![](document.pdf)"
        assert "{% link" not in result.content

    def test_handles_spaces_in_filenames(self, postify, img_map):
        img_map["my cool image.png"] = Path("/source/my cool image.png")

        post = postify("![[My Cool Image.png]]")
        dest_folder = Path("/out")

        result = process_embedded_images(post, img_map, dest_folder)

        assert "My Cool Image.png" in result.content


class TestProcessAltText:
    @pytest.mark.parametrize(
        "md, expected_alt, expected_attrs",
        [
            ("![[image.png]]", "", ""),
            ("![[image.png|300]]", "", 'width="300"'),
            ("![[image.png|300x200]]", "", 'width="300" height="200"'),
            ("![alt text](image.png)", "alt text", ""),
            ("![alt text|400](image.png)", "alt text", 'width="400"'),
            ("![400](image.png)", "", 'width="400"'),
            ("![](image.png)", "", ""),
        ],
    )
    def test_alt_and_size(
        self,
        md,
        expected_alt,
        expected_attrs,
        postify,
        img_map,
    ):
        out = process_embedded_images(postify(md), img_map, Path("/tmp")).content
        assert out.startswith(f"![{expected_alt}](")
        assert expected_attrs in out
