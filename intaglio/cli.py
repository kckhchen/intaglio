import argparse
import re
import sys
from pathlib import Path

from intaglio import __version__
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


def cmd_init(args):
    target = Path.cwd() / RC_NAME
    if target.exists():
        print(f"{RC_NAME} already exists at {target}")
        return
    target.write_text(RC_TEMPLATE, encoding="utf-8")
    print(f"Created {target}")
    print("Run intaglio from this directory, or any subdirectory.")


def cmd_config(args):
    Config.resolve(args).show()


def cmd_run(args):
    cfg = _resolved(args)
    _process(cfg, args)


def cmd_update(args):
    cfg = _resolved(args)
    valid_files = _process(cfg, args)
    remove_stale_files(valid_files, cfg.post_dir, cfg.img_dir, args.yes)


def cmd_clean(args):
    cfg = _resolved(args)
    valid_files = get_valid_files(cfg.vault_dir, cfg.post_dir)
    remove_stale_files(valid_files, cfg.post_dir, cfg.img_dir, args.yes)


def _resolved(args):
    # a bare invocation already resolved the config to show it in the prompt;
    # resolving twice would repeat every warning Config.resolve() prints
    cfg = getattr(args, "preresolved_cfg", None) or Config.resolve(args)
    cfg.validate()
    return cfg


def _process(cfg, args):
    valid_files = get_valid_files(cfg.vault_dir, cfg.post_dir)
    dry = getattr(args, "dry", False)

    if dry:
        print("------------ DRY RUN MODE -------------")
        print("Operations will be printed but files won't be changed.\n")

    print(f"Start processing posts in Vault [ {cfg.vault_dir} ]...")
    print(f"Destination path: [ {cfg.post_dir} ]\n")

    setup_dir([cfg.post_dir, cfg.img_dir], dry)
    ensure_css_exists("obsidian-callouts.html", cfg, dry)
    process_posts(
        valid_files, cfg, dry, args.layout, args.force, getattr(args, "only", None)
    )
    return valid_files


# legacy flag shim

_LEGACY_TOKENS = {
    "--init": "init",
    "--show-config": "config",
    "--cleanup": "clean",
    "-c": "clean",
    "--update": "update",
    "-u": "update",
}

_LEGACY_SHORT = {"c": "clean", "u": "update"}

_PASSTHROUGH = {"-h", "--help", "--version"}

_GROUPED_SHORT = re.compile(r"-[A-Za-z]{2,}$")


def rewrite_legacy(argv):
    if not argv or not argv[0].startswith("-") or argv[0] in _PASSTHROUGH:
        return argv

    found = []
    rest = []

    for token in argv:
        if token in _LEGACY_TOKENS:
            found.append(_LEGACY_TOKENS[token])
            continue

        if _GROUPED_SHORT.match(token):
            letters = token[1:]
            verbs = [c for c in letters if c in _LEGACY_SHORT]
            if verbs:
                found.extend(_LEGACY_SHORT[c] for c in verbs)
                leftover = "".join(c for c in letters if c not in _LEGACY_SHORT)
                if leftover:
                    rest.append("-" + leftover)
                continue

        rest.append(token)

    if len(set(found)) > 1:
        print(
            f"intaglio: error: {' and '.join(sorted(set(found)))} "
            "are separate commands and cannot be combined.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    command = found[0] if found else "run"
    if command == "init":
        rest = []

    rewritten = [command, *rest]
    print(
        f"warning: `intaglio {' '.join(argv)}` uses the deprecated flag-only form.\n"
        f"         Use `intaglio {' '.join(rewritten)}` instead. The old form still\n"
        f"         works and will be removed in a future release.",
        file=sys.stderr,
    )
    return rewritten


def _config_options():
    """Shared config overrides, attached to every command that resolves config."""
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_argument_group(
        "configuration",
        "Overrides .intagliorc and environment variables.",
    )
    group.add_argument("--vault", default=None, help="Path to the Obsidian vault.")
    group.add_argument(
        "--jekyll",
        default=None,
        help="Path to the Jekyll site (defaults to where .intagliorc lives).",
    )
    group.add_argument("--post-folder", default=None, help="Jekyll posts folder.")
    group.add_argument("--img-folder", default=None, help="Where images are copied.")
    group.add_argument(
        "--includes-folder", default=None, help="Jekyll includes folder."
    )
    group.add_argument(
        "--math-mode",
        default=None,
        choices=["inject_cdn", "metadata"],
        help="How math is rendered.",
    )
    group.add_argument(
        "--prevent-double-baseurl",
        action="store_const",
        const="true",
        default=None,
        help="Skip site.baseurl if your theme already adds it.",
    )
    return parser


def _add_force(parser):
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Processes every file regardless of change states.",
    )


def _add_layout(parser):
    parser.add_argument(
        "--layout",
        type=str,
        default="post",
        help="Jekyll layout to use (default: post).",
    )


def _add_yes(parser):
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts (for automation).",
    )


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="intaglio", description="Convert Obsidian notes to Jekyll"
    )
    parser.add_argument(
        "--version", action="version", version=f"intaglio {__version__}"
    )

    commands = parser.add_subparsers(dest="command")
    config_options = _config_options()

    run = commands.add_parser(
        "run",
        parents=[config_options],
        help="Process vault posts into the Jekyll site.",
    )
    run.add_argument(
        "--dry", action="store_true", help="Dry run: simulate without changes."
    )
    _add_force(run)
    _add_layout(run)
    run.add_argument("--only", default=None, help="Only process the selected post.")
    # run never prompts, so this is accepted and ignored — as it was before
    # subcommands, when --yes was a top-level flag the default action ignored
    _add_yes(run)
    run.set_defaults(func=cmd_run)

    update = commands.add_parser(
        "update",
        parents=[config_options],
        help="Process posts, then clean up stale posts and images.",
    )
    _add_force(update)
    _add_layout(update)
    _add_yes(update)
    update.set_defaults(func=cmd_update)

    clean = commands.add_parser(
        "clean",
        parents=[config_options],
        help="Clean up stale posts and images.",
    )
    _add_yes(clean)
    clean.set_defaults(func=cmd_clean)

    init = commands.add_parser(
        "init", help=f"Create a commented {RC_NAME} in the current directory."
    )
    init.set_defaults(func=cmd_init)

    config = commands.add_parser(
        "config",
        parents=[config_options],
        help="Print resolved settings with their source, then exit.",
    )
    config.set_defaults(func=cmd_config)

    return parser


BARE_DEPRECATION = "Running intaglio with no command is deprecated; use `intaglio run`."


def _bare_invocation(parser):
    """Decide what a bare `intaglio` does.

    It still means `run`, so cron jobs and the Action keep working. But a
    human at a terminal is usually just poking at the tool to see what it
    is, so ask before touching their vault.

    Returns (argv, exit_code, cfg); argv is None when nothing should run.
    """
    cfg = Config.resolve(None)

    if cfg.vault_dir is None or cfg.jekyll_dir is None:
        parser.print_help()
        sys.stdout.flush()
        print(
            f"\nNo vault configured yet. Run `intaglio init` to create a "
            f"{RC_NAME}, or pass --vault explicitly.",
            file=sys.stderr,
        )
        return None, 2, None

    if not sys.stdin.isatty():
        print(f"warning: {BARE_DEPRECATION}", file=sys.stderr)
        return ["run"], 0, cfg

    print("This will process posts from")
    print(f"  vault:  {cfg.vault_dir}")
    print(f"  site:   {cfg.jekyll_dir}")
    print(f"\n{BARE_DEPRECATION}")

    try:
        answer = input("Continue? [y/N]: ")
    except (EOFError, KeyboardInterrupt):
        answer = ""
        print()

    if answer.strip().lower() not in {"y", "yes"}:
        print("Aborted.")
        return None, 0, None

    return ["run"], 0, cfg


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = setup_parser()

    cfg = None
    if not argv:
        argv, code, cfg = _bare_invocation(parser)
        if argv is None:
            return code

    args = parser.parse_args(rewrite_legacy(argv))

    if not getattr(args, "func", None):
        parser.print_help()
        return 2

    if cfg is not None:
        args.preresolved_cfg = cfg

    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
