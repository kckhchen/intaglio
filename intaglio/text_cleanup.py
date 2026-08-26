import re

from src.patterns import COMMENT_PATTERN, H1_PATTERN, HIGHLIGHT_PATTERN, TABLE_PATTERN


def text_cleanup(post, layout="post"):
    post = _process_frontmatter(post, layout)
    post = _strip_comments(post)
    post = _process_highlights(post)
    post = _ensure_table_spacing(post)

    return post


def _process_frontmatter(post, layout="post"):
    post["layout"] = post.get("layout") or layout
    post["generator"] = "intaglio"
    h1_match = re.search(H1_PATTERN, post.content, flags=re.MULTILINE)
    if h1_match:
        post = _process_h1(post, h1_match)
    return post


def _process_h1(post, match):
    title = match.group("h1").strip()
    post["title"] = post.get("title") or title
    post.content = re.sub(
        H1_PATTERN, "", post.content, count=1, flags=re.MULTILINE
    ).strip()
    return post


def _strip_comments(post):
    post.content = re.sub(COMMENT_PATTERN, "", post.content)
    return post


def _process_highlights(post):
    post.content = re.sub(
        HIGHLIGHT_PATTERN, "<mark>" + r"\g<1>" + "</mark>", post.content
    )
    return post


def _ensure_table_spacing(post):
    post.content = re.sub(TABLE_PATTERN, r"\n\n\1", post.content)
    return post
