import argparse
from pathlib import Path

from intaglio.cleanup import remove_stale_files
from intaglio.config import RC_NAME, Config
from intaglio.fs_ops import ensure_css_exists, setup_dir
from intaglio.processor_core import process_posts
from intaglio.utils import get_valid_files

RC_TEMPLATE = """\
# Intaglio configuration file. This defines JEKYLL_DIR
# i.e., Intaglio sends your processed posts here.
# You can left them all commented if you don't want to change any config.

# Absolute path to your Obsidian vault.
# NOTE: This absoluate vault includes your user name,
# either consider exporting VAULT_DIR as environment variable:
#   export VAULT_DIR=~/Obsidian/vault
# or set it up here, but add .intagliorc to your .gitignore
# VAULT_DIR="/path/to/your/vault"

# Everything below has a default value.
# Please leave them commented if you don't wish to change them.
# POST_FOLDER="_posts"
# IMG_FOLDER="assets/images/obsidian"
# INCLUDES_FOLDER="_includes"

# "inject_cdn" injects a MathJax CDN when math is detected to be present
# "metadata" includes "math: true" in the frontmatter if your theme supports math natively.
# MATH_RENDERING_MODE="inject_cdn"

# If your theme or Jekyll 4.x includes site.baseurl,
# set this to "true" to prevent double baseurl like "/blog/blog/..."
# PREVENT_DOUBLE_BASEURL="false"
"""


def run(args):
    if args.init:
        init_intaglio_rc()
        return

    cfg = Config.resolve(args)

    if args.show_config:
        cfg.show()
        return

    cfg.validate()
    valid_files = get_valid_files(cfg.vault_dir, cfg.post_dir)

    if not args.cleanup:
        if args.dry:
            print("------------ DRY RUN MODE -------------")
            print("Operations will be printed but files won't be changed.\n")

        print(f"Start processing posts in Vault [ {cfg.vault_dir} ]...")
        print(f"Destination path: [ {cfg.post_dir} ]\n")

        setup_dir([cfg.post_dir, cfg.img_dir], args.dry)
        ensure_css_exists("obsidian-callouts.html", cfg, args.dry)
        process_posts(valid_files, cfg, args.dry, args.layout, args.force, args.only)

    if args.update or args.cleanup:
        remove_stale_files(valid_files, cfg.post_dir, cfg.img_dir, args.yes)


def init_intaglio_rc():
    target = Path.cwd() / RC_NAME
    if target.exists():
        print(f"{RC_NAME} already exists at {target}")
        return
    target.write_text(RC_TEMPLATE, encoding="utf-8")
    print(f"Created {target}")
    print("Run intaglio from this directory, or any subdirectory.")


def setup_parser():
    parser = argparse.ArgumentParser(description="Convert Obsidian notes to Jekyll")

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "-c", "--cleanup", action="store_true", help="Clean up stale posts and images."
    )
    action_group.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Update posts and clean up stale posts and images.",
    )

    parser.add_argument(
        "--dry", action="store_true", help="Dry run: simulate without changes."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Processes every file regardless of change states.",
    )
    parser.add_argument(
        "--layout",
        type=str,
        default="post",
        help="Jekyll layout to use (default: post).",
    )
    parser.add_argument("--only", default=None, help="Only process the selected post.")
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts (for automation).",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create a commented .intagliorc in the current directory.",
    )

    config_group = parser.add_argument_group(
        "configuration",
        "Overrides .intagliorc and environment variables.",
    )
    config_group.add_argument(
        "--vault", default=None, help="Path to the Obsidian vault."
    )
    config_group.add_argument(
        "--jekyll",
        default=None,
        help="Path to the Jekyll site (defaults to where .intagliorc lives).",
    )
    config_group.add_argument(
        "--post-folder", default=None, help="Jekyll posts folder."
    )
    config_group.add_argument(
        "--img-folder", default=None, help="Where images are copied."
    )
    config_group.add_argument(
        "--includes-folder", default=None, help="Jekyll includes folder."
    )
    config_group.add_argument(
        "--math-mode",
        default=None,
        choices=["inject_cdn", "metadata"],
        help="How math is rendered.",
    )
    config_group.add_argument(
        "--prevent-double-baseurl",
        action="store_const",
        const="true",
        default=None,
        help="Skip site.baseurl if your theme already adds it.",
    )
    config_group.add_argument(
        "--show-config",
        action="store_true",
        help="Print resolved settings with their source, then exit.",
    )

    return parser


def main(argv=None):
    parser = setup_parser()
    args = parser.parse_args(argv)

    if args.dry and (args.cleanup or args.update):
        parser.error("--dry cannot be combined with --cleanup or --update.")

    if args.only and (args.cleanup or args.update):
        parser.error("--only cannot be combined with --cleanup or --update.")

    run(args)


if __name__ == "__main__":
    main()
