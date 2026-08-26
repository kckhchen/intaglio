import re
from pathlib import Path

from src.patterns import IMG_EXT, IMG_PATTERN


def process_embedded_images(post, img_map, destination):
    post.content = re.sub(
        IMG_PATTERN,
        lambda m: _embedded_image_replacer(m, img_map, destination),
        post.content,
    )
    return post


def _split_opt(raw, is_md):
    raw = (raw or "").strip()

    if is_md and "|" in raw:
        alt, _, size = raw.rpartition("|")
    elif raw and raw.replace("x", "", 1).isdigit():
        alt, size = "", raw
    else:
        alt, size = raw, ""

    w, _, h = size.partition("x")
    return alt.strip(), (w if w.isdigit() else ""), (h if h.isdigit() else "")


def _embedded_image_replacer(match, img_map, img_folder):
    is_md = match.group("mdlink") is not None
    alt, width, height = _split_opt(
        match.group("md_opt") if is_md else match.group("wiki_opt"), is_md
    )

    name = image_name(match)
    if not name:
        raw = (match.group("mdlink") if is_md else match.group("wikilink")).strip()
        return f"![{alt}]({raw})"

    if name.lower() not in img_map:
        print(
            f"  |  Warning: Image target not found in Vault: {name}. Link kept as-is."
        )
        return match.group(0)

    posix_path = (img_folder / name).as_posix()
    updated_link = f"![{alt}]({{{{ site.baseurl }}}}{{% link {posix_path} %}})"

    attrs = [f'{k}="{v}"' for k, v in (("width", width), ("height", height)) if v]
    if attrs:
        updated_link += "{: " + " ".join(attrs) + " }"

    return updated_link


def image_name(match):
    is_md = match.group("mdlink") is not None
    name = (match.group("mdlink") if is_md else match.group("wikilink")).strip()
    return name if Path(name).suffix.lower() in IMG_EXT else None
