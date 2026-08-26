import re
from pathlib import Path

import frontmatter

from intaglio.patterns import IMG_EXT, IMG_LINK_PATTERN, POST_NAME_PATTERN

SHARED_LOOKING = {"images", "img", "assets", "media", "static", "uploads", "files"}


def remove_stale_files(files, post_dir, img_dir, assume_yes):
    print("\nStarting cleaning up process...")
    print(f"Post folder: [ {post_dir} ]")
    print(f"Image folder: [ {img_dir} ]\n")

    current_posts = {data["dest_path"].name for data in files.values()}

    all_post_images = _get_post_images(post_dir)
    to_be_removed = _list_posts_to_be_removed(
        post_dir, current_posts
    ) + _list_imgs_to_be_removed(img_dir, all_post_images)

    if to_be_removed:
        _remove_files(to_be_removed, assume_yes)
    else:
        print("No stale files found. Nothing will be removed.")


def _is_managed(path):
    try:
        return frontmatter.load(path).get("generator") == "intaglio"
    except Exception:  # noqa: BLE001
        return False


def _get_post_images(post_dir):
    all_images = set()

    for f in Path(post_dir).glob("*.md"):
        content = f.read_text(encoding="utf-8")
        all_images.update(
            Path(m.group("path")).name
            for m in re.finditer(IMG_LINK_PATTERN, content)
            if Path(m.group("path")).suffix.lower() in IMG_EXT
        )

    return all_images


def _list_posts_to_be_removed(post_dir, current_posts):
    return [
        f
        for f in Path(post_dir).iterdir()
        if f.is_file()
        and re.match(POST_NAME_PATTERN, f.name)
        and f.name not in current_posts
        and _is_managed(f)
    ]


def _list_imgs_to_be_removed(img_dir, all_post_images):
    if img_dir.name in SHARED_LOOKING:
        print(
            f"Warning: IMG_FOLDER points at a shared-looking folder ({img_dir}). "
            "Cleanup removes unreferenced images there. Consider a dedicated "
            "subfolder such as assets/images/obsidian."
        )
    return [
        img_dir / img.name
        for img in img_dir.iterdir()
        if img.is_file()
        and img.suffix.lower() in IMG_EXT
        and img.name not in all_post_images
    ]


def _remove_files(file_path_list, assume_yes=False):
    if not file_path_list:
        return

    print("The following files will be removed:\n")
    for p in file_path_list:
        print(f"[{p.parent.name}] {p.name}")

    if assume_yes or input("\nConfirm removal? [y/n]: ").lower() == "y":
        for p in file_path_list:
            try:
                p.unlink()
            except FileNotFoundError:
                print(f"Skipped {p.name} (not found)")
        print("Files removed.")
    else:
        print("Process aborted.")
