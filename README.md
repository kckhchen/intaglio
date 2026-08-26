<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/images/icons/icon-dark.svg">
    <img src="assets/images/icons/icon.svg" width="112" alt="Intaglio">
  </picture>
</p>

<h1 align="center">Intaglio</h1>

<p align="center">
  A theme-agnostic tool that makes your Obsidian articles Jekyll-ready.
</p>

<p align="center">
  <a href="https://github.com/kckhchen/intaglio/actions/workflows/ci.yml"><img src="https://github.com/kckhchen/intaglio/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/kckhchen/intaglio/releases"><img src="https://img.shields.io/github/v/release/kckhchen/intaglio" alt="Release"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
</p>

---

Intaglio scans your Obsidian vault, converts the notes you've marked as shared into Jekyll-compatible posts, and writes them to your site — so your vault stays clean Markdown while Jekyll gets the flavour it expects.

It runs as a GitHub Action that opens a pull request against your site repository on every push, or as a local CLI if you'd rather keep your vault off GitHub.

## Features

- Auto-generates all the essentials for the frontmatter.
- Converts your `h1` header to your post title.
- Copies used images to Jekyll assets folder and updates `![[img]]` links along with alt texts and width settings.
- Converts `[[Wikilinks]]` to standard Markdown links and links posts properly, including URLs and internal links.
- `$Math$` / `Code` / `> [!Callout]` / `[[#^Block Link]]` support, and more.
- Syncs to your vault; removed posts and stale images get removed from your Jekyll site too.
- Your original Obsidian articles remain intact, the way you want them to be.

## Live Demo

|                    Original Obsidian Article                     |                     Processed Jekyll Site                      |
| :--------------------------------------------------------------: | :------------------------------------------------------------: |
| <img src="./assets/images/obsidian-demo.gif" width="380" alt=""> | <img src="./assets/images/jekyll-demo.gif" width="380" alt=""> |

  <div align="center">
    <p><a href="https://kckhchen.com/intaglio-demo/my-main-post/"><b>Read the Demo Blog Post</b></a></p>
  </div>

## Quick Start

### Prerequisites

- **For the GitHub Action:** nothing to install.
- **For the local CLI:** Python 3.10+ and [uv](https://docs.astral.sh/uv/).

### 1. Mark the Posts You Want to Publish

Add `share: true` and `date: YYYY-MM-DD` to your post's frontmatter ([Obsidian Properties](https://help.obsidian.md/properties)). You can use a [checkbox](https://help.obsidian.md/properties#Checkbox) or [plain text](https://help.obsidian.md/properties#Text) for `share`. `date` will be the publish date displayed on your Jekyll site. Anything else you add (`slug`, `permalink`, and so on) is optional and will be left alone.

The tool adds `title`, `layout`, and `math` (based on settings) to the frontmatter for you, so you don't have to configure those unless you want to override them.

```markdown
---
share: true
date: 2026-01-01
---

# My Post Title
```

Only posts with `share: true` will be processed.

> [!important]
> **Set `date` yourself.** The creation date the tool falls back to is not stable and may change on copy, clone, or sync. When it changes, the generated filename changes with it — and so does the post's permalink. The old URL starts returning 404, and every link anyone has already shared to that post breaks. This is also why the GitHub Action refuses to run at all when a shared note has no `date`.

### 2. Try It Locally

Before setting anything up on GitHub, run the conversion on your own machine and have a look at the results:

#### Install

```bash
uv tool install git+https://github.com/kckhchen/intaglio@v1
```

This installs an `intaglio` command onto your PATH in its own isolated environment. If your shell can't find the command afterwards, run `uv tool update-shell` and open a new terminal.

`@v1` follows the latest 1.x release; use a full tag such as `@v1.5.0` to pin an exact version. To upgrade later:

```bash
uv tool upgrade --reinstall intaglio
# or if you prefer pipx:
# pipx install git+https://github.com/kckhchen/intaglio@v1
```

#### Point it at your vault

From the root of your **Jekyll site**, create a config file:

```bash
cd /path/to/jekyll/site
intaglio init
```

This writes a commented `.intagliorc`. The only setting you need is the path to your vault:

```bash
# .intagliorc
VAULT_DIR="/path/to/obsidian/vault"
# or exported as environment variable with
# export VAULT_DIR="/path/to/obsidian/vault"
```

`JEKYLL_DIR` defaults to wherever `.intagliorc` lives, so you don't need to set it. Run `intaglio` from that directory or any subdirectory of it.

> [!note]
> `.intagliorc` contains the absolute path to your vault and exposes your username. Consider adding `.intagliorc` to your `.gitignore`, or, if you wish to carry the config file around, you can export `VAULT_DIR` as environment variable.

> [!important]
> Earlier versions used a `.env` file. It is still read, but is deprecated and will warn on every run. Rename it to `.intagliorc`.

You can override the settings in `.intagliorc` either with environment variables or temporarily with CLI flags. CLI flags takes precedence over everything else. The tool automatically resolves the config. To see which config source is at work for each variable, use the command:

```bash
intaglio config
```

#### Preview, then commit

Start with a dry run. It prints every action it would take without changing a single file:

```bash
intaglio run --dry
```

Looks good? Drop the flag:

```bash
intaglio run
```

> [!note]
> **A Note on Styling**: The first time you run the tool, it will create `_includes/obsidian-callouts.html` in your Jekyll repository. This file handles the icons and colors for your callouts. Feel free to customize it.

> [!important]
> If you set up a baseurl for your Jekyll site and found links dead due to duplicate baseurls e.g. `blog/blog/my-post`, flip `PREVENT_DOUBLE_BASEURL` to `True` in `.intagliorc`. This could happen for Jekyll 4.x or some special themes.

### 3. Set Up the Action (Recommended for Ongoing Use)

Once you like what the tool produces, this is the way to keep it running hassle-free. After setting the things up ,your publishing workflow becomes as simple as **"write, commit, push"**. The Action converts the notes and sends a pull request to your Jekyll site with the formatted posts.

Three things have to be true before you start:

1. **Your vault is a GitHub repository**, and the workflow file lives in it. The Action checks out the calling repository as the vault.
2. **Your Jekyll site is a separate repository.** A single checkout cannot serve as both source and destination.
3. **Every shared note has an explicit `date`.** Modification time refreshes on every push, so the Action cannot fall back to it. A shared note without a `date` fails the run on purpose, rather than silently producing an unstable permalink.

If any of those don't suit you, skip ahead to [running the CLI instead](#4-or-keep-using-the-cli).

#### 1. Generate a Fine-Grained Token

Generate a fine-grained token for your Jekyll site and set repository permissions to **Contents: Read and write** and **Pull Requests: Read and write**. Copy the token and paste it to your repository secrets in your vault repo, naming it `BLOG_PUSH_TOKEN`.

#### 2. Create the Action `.yml`

Create a `publish.yml` file under `.github/workflows` and paste the following snippet:

```yaml
name: Publish
on:
  push:
    branches: [main] # or master based on your repo
  workflow_dispatch: # for manual run

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: kckhchen/intaglio@v1
        with:
          jekyll-repo: username/jekyll-repo # your own repo name
          token: ${{ secrets.BLOG_PUSH_TOKEN }}
```

By default, this publishes new and updated posts only. Posts you delete from your vault will stay on your site (we don't want to delete anything without your explicit consent). To remove stale posts and images and sync your vault status, see the sync example below:

```yaml
name: Publish
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: kckhchen/intaglio@v1
        with:
          jekyll-repo: username/jekyll-repo # your own repo name
          token: ${{ secrets.BLOG_PUSH_TOKEN }}
          args: update --force --yes
```

This will update the posts and remove stale posts and images from your Jekyll site.

> [!important]
> If you set up a baseurl for your Jekyll site and found links dead due to duplicate baseurls e.g. `blog/blog/my-post`, set `prevent-double-baseurl: true` under the `with:` section in your `.yml` file. This could happen for Jekyll 4.x or some special themes. For more information about flags, check out [GUIDE.md](./assets/docs/GUIDE.md).

A few more things worth knowing:

1. Unlike the CLI tool, the Action **does not** implement incremental builds. Incremental builds rely on file modification time, which refreshes on push. In other words, it process every post regardless it's been modified or not, just like the `--force` flag. This would not make any practical difference to your posts though.
2. **Cleanup automatically proceeds.** With no terminal to prompt at, `update` and `clean` need the `--yes` flag or they abort without deleting anything. To keep that safe, you can set a `max-deletions` (default to 10) limit that when reached, the process will send a warning. Regardless, you can always have a look before merging the PR.
3. For full configuration, check out [action_config.md](./assets/docs/action_config.md)

### 4. Or Keep Using the CLI

Prefer to keep your vault off GitHub? The tool got ya. The CLI does the same conversion locally, and nothing in your vault ever leaves your machine. Just `cd` to your Jekyll directory and run any of the commands:

```bash
# Process new posts
intaglio run

# Process posts and clean up posts deleted from the vault
intaglio update

# Process only one post (use only the post name, not the relative path)
intaglio run --only "My Post.md"
```

Check your `_posts` folder. Like how they look? Push it and publish to the world!

### Available Flags

`intaglio --help` lists every command, and `intaglio <command> --help` lists the flags for one. The full list is in [GUIDE.md](./assets/docs/GUIDE.md).

Neither your original Obsidian notes nor hand-authored posts on your Jekyll site are ever touched when you run `intaglio update`: cleanup only removes files carrying the tool's own `generator: intaglio` frontmatter marker.

> [!note]
> Running `intaglio` with no command still means `intaglio run`. At a terminal it first shows which vault and site it is about to touch and asks you to confirm; in a script or CI it just runs.

#### Running from source

Use this if you want to modify the tool or run the test suite:

```bash
git clone https://github.com/kckhchen/intaglio.git
cd intaglio
python3 -m venv .venv
source .venv/bin/activate
# or .venv\Scripts\activate.bat for Windows
pip install -e .
```

## User Guide

You can find the full User Guide and Advanced Settings in [GUIDE.md](./assets/docs/GUIDE.md).

## What This Tool Doesn't Do

This tool converts most Obsidian Markdown syntax elements into Jekyll-compatible liquid tags or html tags, but these feature supports are not included (yet):

1. Note embed (frame for another note inside current note)
2. PDF embed
3. Mermaid graphs
4. Backlinks

If you would like any of these feature supports to be added to the tool, please open an issue or contact me. I will add these features ASAP.

Other things this tool doesn't support are non-note and non-text based elements, such as bases, canvas, and graph views.

## Contributing

This project is actively maintained and frequently updated. If you'd like to contribute, you can submit issues or fork this repository.

## Testing

This project uses `pytest` for testing. The tests are in the `tests` folder. To run the tests locally, follow these steps:

1. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

1. Run the Test Suite
   To run all tests:

```bash
pytest
# or pytest --spec for spec reviews
```

To run a specific test file:

```bash
pytest tests/test_process_images.py
```

## Heads-Up

The test suite covers the conversion pipeline end to end across macOS, Linux and Windows on Python 3.10 and 3.13, and every post on my [personal blog](https://kckhchen.com/blog/) (in Mandarin Chinese) is generated by this tool. That said, Jekyll themes vary widely — if something renders oddly on your site, please open an issue.
