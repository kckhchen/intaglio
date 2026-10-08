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

|                    Original Obsidian Article                     |                     Processed Jekyll Site                      |
| :--------------------------------------------------------------: | :------------------------------------------------------------: |
| <img src="./assets/images/obsidian-demo.gif" width="380" alt=""> | <img src="./assets/images/jekyll-demo.gif" width="380" alt=""> |

<p align="center"><a href="https://kckhchen.com/intaglio-demo/my-main-post/"><b>Read the Demo Blog Post</b></a></p>

## Features

- Auto-generates all the essentials for the frontmatter.
- Converts your `h1` header to your post title.
- Copies used images to Jekyll assets folder and updates `![[img]]` links along with alt texts and width settings.
- Converts `[[Wikilinks]]` to standard Markdown links and links posts properly, including URLs and internal links.
- `$Math$` / `Code` / `> [!Callout]` / `[[#^Block Link]]` support, and more.
- Syncs to your vault; removed posts and stale images get removed from your Jekyll site too.
- Your original Obsidian articles remain intact, the way you want them to be.

## Quick Start

### 1. Mark the Posts You Want to Publish

Add `share: true` and `date: YYYY-MM-DD` to your post's frontmatter ([Obsidian Properties](https://help.obsidian.md/properties)):

```markdown
---
share: true
date: 2026-01-01
---

# My Post Title
```

Only posts with `share: true` will be processed. Your `h1` header becomes the post title.

### 2. Try It Locally

You'll need Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/kckhchen/intaglio@v1
```

From the root of your **Jekyll site**, create a config file:

```bash
cd /path/to/jekyll/site
intaglio init
```

This writes a commented `.intagliorc`. The only setting you need to add to the file is the path to your vault:

```bash
VAULT_DIR="/path/to/obsidian/vault"
```

Then, run the conversion:

```bash
intaglio run
```

Spin up your Jekyll server and check the beautifully rendered posts. Like how they look?

### 3. Set Up the Action

Once you like what the tool produces, this is the way to keep it running hassle-free: your publishing workflow becomes as simple as **"write, commit, push"**. You'll need your vault and your Jekyll site in two separate GitHub repositories.

1. [Generate a fine-grained token](https://github.com/settings/personal-access-tokens/new) for your Jekyll site with **Contents: Read and write** and **Pull Requests: Read and write**. Paste it to your repository secrets in your vault repo, naming it `BLOG_PUSH_TOKEN`.
2. Create a `publish.yml` file under `.github/workflows` in your vault repo and paste the following snippet:

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

That's it. On every push, the Action converts the notes and sends a pull request to your Jekyll site with the formatted posts. More options in [action_config.md](./assets/docs/action_config.md).

> [!tip]
> Prefer to keep your vault off GitHub? The tool got ya. Skip step 3 and just run `intaglio run` from your Jekyll directory — nothing in your vault ever leaves your machine.

## Good to Know

- **Deleted posts stay on your site by default** (we don't want to delete anything without your explicit consent). To clean them up, use `intaglio update`, or `args: update --force --yes` in the Action. Only files the tool generated are ever removed.
- **Dead links like `blog/blog/my-post`?** Set `PREVENT_DOUBLE_BASEURL=True` in `.intagliorc`, or `prevent-double-baseurl: true` in the Action.
- **Not supported (yet):** note embeds, PDF embeds, Mermaid graphs, backlinks, bases, canvas, and graph views. If you would like any of these, please open an issue or contact me.

## Learn More

- [User Guide](./assets/docs/GUIDE.md): installation, commands, settings, and how the conversion works
- [Action Configuration](./assets/docs/action_config.md): all the options for the GitHub Action
- [Contributing](./CONTRIBUTING.md): running from source and testing
