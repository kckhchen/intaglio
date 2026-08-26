import re
import shutil

from intaglio.callout_styles import CALLOUT_CSS
from intaglio.patterns import IMG_PATTERN
from intaglio.process_images import image_name


def setup_dir(paths, dry):
    for path in paths:
        if not path.exists():
            print(f"---- Destination folder not found, creating {path} ----")
            if not dry:
                path.mkdir(parents=True, exist_ok=True)


def ensure_css_exists(css_name, cfg, dry):
    includes_dir = cfg.includes_dir
    css_path = includes_dir / css_name
    if not css_path.exists():
        print(f"---- Creating default callout CSS at: {css_path} ----")
        if not dry:
            css_path.parent.mkdir(parents=True, exist_ok=True)
            css_path.write_text(CALLOUT_CSS, encoding="utf-8")


def copy_images(post, img_map, img_dir):
    for match in re.finditer(IMG_PATTERN, post.content):
        name = image_name(match)
        if not name:
            continue
        src = img_map.get(name.lower())
        if src:
            shutil.copy2(src, img_dir / name)
