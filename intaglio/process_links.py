import re
from pathlib import Path

from intaglio.patterns import ANCHOR_PATTERN, LINK_PATTERN, PLACEHOLDER_PATTERN
from intaglio.utils import slugify


def process_wikilinks(post, files, destination, prevent_double_baseurl):
    baseurl = not prevent_double_baseurl
    post.content = re.sub(
        ANCHOR_PATTERN, _anchor_replacer, post.content, flags=re.MULTILINE
    )
    post.content = re.sub(
        LINK_PATTERN,
        lambda m: _link_replacer(m, files, destination, baseurl),
        post.content,
    )
    return post


def _anchor_replacer(match):
    preceding_char = match.group(1)
    anchor = match.group("anchor").strip()
    if preceding_char == " ":
        return f"\n{{: #secid{anchor}}}"
    else:
        return f"{{: #secid{anchor}}}"


def _link_replacer(match, valid_files, post_folder, baseurl):
    target = match.group("wikilink") or match.group("mdlink")
    target = target.strip()
    display = match.group("wiki_display") or match.group("md_display") or target
    display = display.strip("#")

    # skip shielding placeholders
    if re.match(PLACEHOLDER_PATTERN, target) and match.group("mdlink"):
        return f"[{display}]({target})"

    filename = target
    anchor_suffix = ""

    if "#^" in target:
        parts = target.split("#^", 1)
        filename = parts[0]
        anchor_suffix = "#secid" + parts[1].strip()
    elif "#" in target:
        parts = target.split("#", 1)
        filename = parts[0]
        anchor_suffix = "#" + slugify(parts[1])

    filename = filename.strip()

    if not filename:
        return f"[{display}]({anchor_suffix})"

    filename = Path(filename).stem

    if filename not in valid_files:
        print(
            f"  |  Warning: Link target not found: '{filename}'. Converted to plain text."
        )
        return f"{display}"

    dest = valid_files[filename]["dest_path"].name
    posix_path = (post_folder / dest).as_posix()
    if baseurl:
        return f"[{display}]({{{{ site.baseurl }}}}{{% link {posix_path} %}}{anchor_suffix})"
    else:
        return f"[{display}]({{% link {posix_path} %}}{anchor_suffix})"
