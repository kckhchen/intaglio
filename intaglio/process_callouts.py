import re

from src.callout_styles import ICONS
from src.patterns import CALLOUT_PATTERN, FENCE_IN_BODY


def process_callouts(post):
    new_content, count = re.compile(CALLOUT_PATTERN, re.MULTILINE).subn(
        _callout_replacer, post.content
    )

    if count > 0:
        post.content = new_content
        post.content += "\n\n{% include obsidian-callouts.html %}"

    return post


def _callout_replacer(match):
    if re.compile(FENCE_IN_BODY).search(match.group("body")):
        print(
            "  |  Warning: Fenced code block inside a callout is not supported; "
            "callout left as a plain blockquote."
        )
        return match.group(0)

    ctype = match.group("ctype").lower()
    collapse = match.group("collapse")
    title = match.group("title").strip()
    body = re.sub(r"^>\s?", "", match.group("body"), flags=re.MULTILINE)

    body = re.compile(CALLOUT_PATTERN, re.MULTILINE).sub(_callout_replacer, body)

    return _render_callout(ctype, title, body, collapse)


def _render_callout(callout_type, title, body, collapse):
    icon = ICONS.get(callout_type, ICONS["others"])
    title = title or callout_type.capitalize()
    tag_map = {"+": "details open", "-": "details"}
    open_tag = tag_map.get(collapse)
    if open_tag:
        content = f"""<{open_tag} markdown="1">
<summary class="callout-title"><i class="callout-icon" data-lucide="{icon}"></i><span class="callout-title-text">{title}</span></summary>
{body}</details>"""
    else:
        content = f"""<div class="callout-title"><i class="callout-icon" data-lucide="{icon}"></i><span class="callout-title-text">{title}</span></div>
{body}"""

    return f'<div class="callout callout-{callout_type}" markdown="1">{content}\n</div>'
