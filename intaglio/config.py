# CLI flags > env vars > .intagliorc > default values

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

RC_NAME = ".intagliorc"
LEGACY_RC_NAME = ".env"

KNOWN = {
    "VAULT_DIR",
    "JEKYLL_DIR",
    "POST_FOLDER",
    "IMG_FOLDER",
    "INCLUDES_FOLDER",
    "MATH_RENDERING_MODE",
    "PREVENT_DOUBLE_BASEURL",
}

VALID_MATH_MODES = {"inject_cdn", "metadata"}

DEFAULTS = {
    "POST_FOLDER": "_posts",
    "IMG_FOLDER": "assets/images/obsidian",
    "INCLUDES_FOLDER": "_includes",
    "MATH_RENDERING_MODE": "inject_cdn",
    "PREVENT_DOUBLE_BASEURL": "false",
}


def find_rc(start=None):
    # locate rc file up until hitting the .git folder
    current = Path(start or Path.cwd()).resolve()

    for directory in (current, *current.parents):
        for name in (RC_NAME, LEGACY_RC_NAME):
            candidate = directory / name
            if candidate.is_file():
                is_legacy = name == LEGACY_RC_NAME
                return candidate, is_legacy
        if (directory / ".git").exists():
            break

    return None, False


def _as_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


@dataclass(frozen=True)
class Config:
    vault_dir: Path | None
    jekyll_dir: Path | None
    post_folder: Path = Path("_posts")
    img_folder: Path = Path("assets/images/obsidian")
    includes_folder: Path = Path("_includes")
    math_rendering_mode: str = "inject_cdn"
    prevent_double_baseurl: bool = False
    sources: dict = field(default_factory=dict, compare=False, repr=False)

    @property
    def _site(self) -> Path:
        if self.jekyll_dir is None:
            raise RuntimeError("JEKYLL_DIR is unset; call validate() first.")
        return self.jekyll_dir

    @property
    def post_dir(self) -> Path:
        return self._site / self.post_folder

    @property
    def img_dir(self):
        return self._site / self.img_folder

    @property
    def includes_dir(self):
        return self._site / self.includes_folder

    @classmethod
    def resolve(cls, args=None, *, cwd=None, env=None):
        env = os.environ if env is None else env
        rc_path, is_legacy = find_rc(cwd)
        rc_values = dotenv_values(rc_path) if rc_path else {}
        rc_source = rc_path.name if rc_path else "rc"

        if is_legacy:
            print(
                f"Warning: {LEGACY_RC_NAME} is deprecated. "
                f"Rename it to {RC_NAME} — support will be removed in a future release."
            )

        for key in rc_values:
            if key not in KNOWN:
                print(f"Warning: Unknown setting in {rc_source}: {key}")

        sources = {}

        def pick(flag_value, key, default=None):
            if flag_value is not None:
                sources[key] = "flag"
                return flag_value
            if env.get(key):
                sources[key] = "env"
                return env[key]
            if rc_values.get(key):
                sources[key] = rc_source
                return rc_values[key]
            sources[key] = "default"
            return default

        def pick_str(flag_value: str | None, key: str, default: str) -> str:
            return pick(flag_value, key, default) or default

        def flag(name):
            return getattr(args, name, None) if args else None

        jekyll_default = str(rc_path.parent) if rc_path else None
        jekyll = pick(flag("jekyll"), "JEKYLL_DIR", jekyll_default)
        if rc_path and sources["JEKYLL_DIR"] == "default":
            sources["JEKYLL_DIR"] = f"{rc_source} location"

        vault = pick(flag("vault"), "VAULT_DIR")

        return cls(
            vault_dir=Path(vault).expanduser() if vault else None,
            jekyll_dir=Path(jekyll).expanduser() if jekyll else None,
            post_folder=Path(
                pick_str(flag("post_folder"), "POST_FOLDER", DEFAULTS["POST_FOLDER"])
            ),
            img_folder=Path(
                pick_str(flag("img_folder"), "IMG_FOLDER", DEFAULTS["IMG_FOLDER"])
            ),
            includes_folder=Path(
                pick_str(
                    flag("includes_folder"),
                    "INCLUDES_FOLDER",
                    DEFAULTS["INCLUDES_FOLDER"],
                )
            ),
            math_rendering_mode=pick_str(
                flag("math_mode"),
                "MATH_RENDERING_MODE",
                DEFAULTS["MATH_RENDERING_MODE"],
            ),
            prevent_double_baseurl=_as_bool(
                pick(
                    flag("prevent_double_baseurl"),
                    "PREVENT_DOUBLE_BASEURL",
                    DEFAULTS["PREVENT_DOUBLE_BASEURL"],
                )
            ),
            sources=sources,
        )

    def validate(self):
        if self.vault_dir is None or not self.vault_dir.exists():
            print(f"STARTUP FAILED: VAULT_DIR doesn't exist: {self.vault_dir}")
            sys.exit(1)

        if self.jekyll_dir is None or not self.jekyll_dir.exists():
            print(f"STARTUP FAILED: JEKYLL_DIR doesn't exist: {self.jekyll_dir}")
            sys.exit(1)

        if self.math_rendering_mode not in VALID_MATH_MODES:
            print(
                f"STARTUP FAILED: MATH_RENDERING_MODE must be one of "
                f"{sorted(VALID_MATH_MODES)}, got: {self.math_rendering_mode}"
            )
            sys.exit(1)

    def show(self):
        rows = [
            ("VAULT_DIR", self.vault_dir),
            ("JEKYLL_DIR", self.jekyll_dir),
            ("POST_FOLDER", self.post_folder),
            ("IMG_FOLDER", self.img_folder),
            ("INCLUDES_FOLDER", self.includes_folder),
            ("MATH_RENDERING_MODE", self.math_rendering_mode),
            ("PREVENT_DOUBLE_BASEURL", self.prevent_double_baseurl),
        ]
        width = max(len(str(v)) for _, v in rows)
        key_width = max(len(k) for k, _ in rows) + 2
        for key, value in rows:
            source = self.sources.get(key, "default")
            print(f"{key:<{key_width}}{value!s:<{width + 2}}({source})")
