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

It runs as a CLI, or as a GitHub Action that opens a pull request against your site repository on every push.

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

- Python 3.10+

### Run the Tool

#### 1. Clone this repo

```bash
git clone https://github.com/kckhchen/intaglio.git
cd intaglio
```

#### 2. Create a venv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
# or .\venv\Scripts\activate.bat for Windows
pip install -r requirements.txt
```

#### 3. Configure your paths

Create a `.env` in the project root. It is git-ignored, so your personal paths stay out of version control and `git pull` will never conflict.

```bash
cp .env.example .env
```

Then edit `.env` to set up paths to your vault and Jekyll site:

```bash
# .env
VAULT_DIR="/path/to/obsidian/vault"
JEKYLL_DIR="/path/to/jekyll/site"
```

#### 4. Prepare Your Posts

Add `share: true` to your post's frontmatter ([Obsidian Properties](https://help.obsidian.md/properties)). You can use a [checkbox](https://help.obsidian.md/properties#Checkbox) or [plain text](https://help.obsidian.md/properties#Text). You can also add other settings (e.g. `date`, `slug`) to the frontmatter at this stage, although they are not strictly required.

The tool adds `title`, `layout`, and `math` (based on settings) to the frontmatter for you, and grabs the creation date of your post as the `date` if you do not set one, so you don't have to configure these unless you wish to override the settings.

```markdown
---
share: true
---

# My Post Title
```

Only posts with `share: true` will be processed.

> [!tip]
> It is still strongly recommended that you set `date` in the frontmatter manually to prevent unexpected updates, since the creation date of a file can potentially change due to file system operations. Also, manually setting `date` allows you to control the displayed post date on the site.

#### 5. Run the command

```bash
# Process new posts
python3 main.py

# Process posts and clean up deleted posts
python3 main.py --update

# Process only one post (use only the post name, not the relative path)
python3 main.py --only "My Post.md"

# For dry run
python3 main.py --dry
```

Neither your original Obsidian notes nor hand-authored posts on your Jekyll site are ever touched when you run `--update`: cleanup only removes files carrying the tool's own `generator: intaglio` frontmatter marker.

> [!note]
> **A Note on Styling**: The first time you run the tool, it will create `_includes/obsidian-callouts.html` in your Jekyll repository. This file handles the icons and colors for your callouts. Feel free to customize it.

> [!important]
> If you set up a baseurl for your Jekyll site and found links dead due to duplicate baseurls e.g. `blog/blog/my-post`, switch `PREVENT_DOUBLE_BASEURL` to `True` in `.env`. This could happen for Jekyll 4.x or some special themes.

### Actions (Optional)

This tool can be used with GitHub Actions, as long as your vault (or posts) and your Jekyll site are pushed and synced to separate GitHub repos. Once this is setup, your workflow becomes as simple as **"write, commit, push,"** and the Action takes care of the rest and sends a PR to your Jekyll site with all the formatted posts. Follow the steps below:

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

By default, this publishes new and updated posts only. Posts you delete from your vault will stay on your site. To remove those too, see the sync example below:

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
          args: --update --force --yes
```

This will update the posts and remove stale posts and images from your Jekyll site.

> [!important]
> If you set up a baseurl for your Jekyll site and found links dead due to duplicate baseurls e.g. `blog/blog/my-post`, set `prevent-double-baseurl: true` under the `with:` section in your `.yml` file. This could happen for Jekyll 4.x or some special themes. For more information about flags, check out [GUIDE.md](./assets/docs/GUIDE.md).

A few things to note before proceeding with this workflow:

1. The Action **does not** implement incremental builds. Incremental builds rely on file modification time, which refreshes on push. In other words, it effectively uses the `--force` flag every time it runs. It acts exactly the same way as before (nothing affected).
2. **Dates are mandatory**. As modification time becomes unreliable, it enforces explicit dates in the frontmatter. Failure to comply with this will trigger a delivery stopper.
3. **Cleanup automatically proceeds**. Without a CLI to prompt for confirmation, `--cleanup` and `--update` rely on the `--yes` flag to automatically proceed. To address this challenge, you can set a `max-deletions` (default to 10) limit that when reached, the process will send a warning, and you can always have a look before merging the PR.
4. **Your vault and Jekyll site must be separate repositories.** The action checks out both into the runner workspace, and a single checkout cannot serve as both source and destination.
5. For full configuration, check out [action_config.md](./assets/docs/action_config.md)

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
