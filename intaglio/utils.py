import re
from datetime import datetime
from pathlib import Path

import frontmatter
import yaml

from .patterns import (
    BLOCK_MATH_PATTERN,
    CODE_PATTERN,
    INLINE_MATH_PATTERN,
    LIQUID_PATTERN,
    URL_PATTERN,
)

local_tz = datetime.now().astimezone().tzinfo


def _get_creation_time(filepath):
    stat = Path(filepath).stat()
    timestamp = getattr(stat, "st_birthtime", None) or stat.st_mtime
    return datetime.fromtimestamp(timestamp, tz=local_tz).strftime("%Y-%m-%d")


def slugify(name):
    return re.sub(r"[^\w.]+", "-", name).strip("-").lower()


def shield_content(post, mode):
    def _replacer(match):
        text = match.group(0)
        kind = "FENCE" if text[:3] in ("```", "~~~") else mode.upper()
        key = f"\x00{kind}_{len(stash)}\x00"
        stash[key] = text
        return key

    if mode == "code":
        pattern = CODE_PATTERN
    elif mode == "math":
        pattern = f"(?:{BLOCK_MATH_PATTERN}|{INLINE_MATH_PATTERN})"
    elif mode == "url":
        pattern = URL_PATTERN
    else:
        raise ValueError(f"Unknown shield type: {mode}")

    stash = {}
    post.content = re.sub(pattern, _replacer, post.content)
    return post, stash


def unshield(post, stash, convert_func=None):
    for key, original_text in stash.items():
        if convert_func:
            original_text = convert_func(original_text)
        post.content = post.content.replace(key, original_text)
    return post


def shield_liquid(text):
    # wrap raw {{...}} into {% raw %} to prevent Jekyll conversion
    if "{% raw %}" in text or "{% endraw %}" in text:
        print("  |  Warning: block already contains raw tags; left as-is.")
        return text
    pattern = re.compile(LIQUID_PATTERN, re.DOTALL)
    return pattern.sub(lambda m: "{% raw %}" + m.group(0) + "{% endraw %}", text)


def get_valid_files(vault_dir, post_dir):
    MD_SUFFIXES = frozenset({".md", ".markdown"})
    valid_files = {}
    post_dir = post_dir.resolve()

    for path in sorted(vault_dir.rglob("*")):
        if path.suffix.lower() not in MD_SUFFIXES:
            continue

        # skip POST_DIR to allow for same repo sync
        if post_dir in path.resolve().parents:
            continue

        # skip dotfiles
        if any(part.startswith(".") for part in path.relative_to(vault_dir).parts):
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                # skip posts without a frontmatter
                if f.readline().strip() != "---":
                    continue
                f.seek(0)
                post = frontmatter.load(f)
        except UnicodeDecodeError:
            print(f"Warning: Skipping non-UTF-8 file: {path}")
            continue
        except yaml.YAMLError as e:
            print(
                f"Warning: Skipping malformed frontmatter in {path}: {e.__class__.__name__}"
            )
            continue

        if str(post.get("share")).lower() == "true":
            dest_path = _get_dest_fpath(post, path, post_dir)

            if path.stem in valid_files:
                print(
                    f"Warning: Duplicate filename found: '{path.stem}'. {path} will be skipped."
                )
                continue

            valid_files[path.stem] = {
                "source_path": path,
                "dest_path": dest_path,
            }

    return valid_files


def _get_dest_fpath(post, source_fpath, post_dir):
    date_val = post.get("date")
    if date_val:
        date_str = str(date_val)[:10]
    else:
        date_str = _get_creation_time(source_fpath)

    clean_stem = re.sub(r"^\d{4}-\d{2}-\d{2}[-_]?", "", source_fpath.stem)
    new_name = f"{date_str}-{slugify(clean_stem)}{source_fpath.suffix}"

    return post_dir / new_name
