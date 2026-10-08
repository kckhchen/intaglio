# Actions Configuration

## Before You Start

Three things have to be true before you start:

1. **Your vault is a GitHub repository**, and the workflow file lives in it. The Action checks out the calling repository as the vault.
2. **Your Jekyll site is a separate repository.** A single checkout cannot serve as both source and destination.
3. **Every shared note has an explicit `date`.** Modification time refreshes on every push, so the Action cannot fall back to it. A shared note without a `date` fails the run on purpose, rather than silently producing an unstable permalink.

If any of those don't suit you, [run the CLI locally instead](../../README.md#3-set-up-the-action).

## Removing Deleted Posts

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

## Good to Know

A few more things worth knowing:

1. Unlike the CLI tool, the Action **does not** implement incremental builds. Incremental builds rely on file modification time, which refreshes on push. In other words, it process every post regardless it's been modified or not, just like the `--force` flag. This would not make any practical difference to your posts though.
2. **Cleanup automatically proceeds.** With no terminal to prompt at, `update` and `clean` need the `--yes` flag or they abort without deleting anything. To keep that safe, you can set a `max-deletions` (default to 10) limit that when reached, the process will send a warning. Regardless, you can always have a look before merging the PR.
3. For full configuration, check out the [tables below](#available-config)

## Available Config

The following are all the available configuration you can use with `with:` when setting up your custom GitHub Actions:

| Name              | Description                                                                                   | Default value                    |
| ----------------- | --------------------------------------------------------------------------------------------- | -------------------------------- |
| `jekyll-repo`     | Jekyll site repo (owner/name). Must differ from your vault repo.                              | `""`                             |
| `jekyll-dir`      | Path to the Jekyll site                                                                       | `site`                           |
| `vault-dir`       | path to the Obsidian vault                                                                    | `vault`                          |
| `token`           | Token with read-and-write permission for content and PR on `jekyll-repo`                      | `""`                             |
| `args`            | Intaglio command and flags, e.g. `run --force` or `update --force --yes`                      | `run --force`                    |
| `mode`            | `pr` opens or updates a pull request, `push` pushes to the default branch, `none` syncs only. | `pr`                             |
| `branch`          | Branch used in `pr` mode. Fixed names so repeated runs don't create new branches.             | `obsidian-sync`                  |
| `commit-message`  | Custom commit message. `{sha}` is replaced with the short SHA                                 | `chore: sync from vault @ {sha}` |
| `max-deletions`   | Warn above this many deletions. Runs won't fail.                                              | `10`                             |
| `require-date`    | Abort process if a shared noted has no explicit date.                                         | `true`                           |
| `optimise-images` | Compress PNG/JPEG before commiting to save storage.                                           | `false`                          |
| `python-version`  | Python version to run this job.                                                               | `3.13`                           |

Every environment variable also has a counterpart here, listed under [Site Layout and Rendering](#site-layout-and-rendering) below.

> [!note]
> `args` takes a command followed by its flags. The pre-1.5 flag-only form (`--update --force --yes`) still works but prints a deprecation warning; see [GUIDE.md](./GUIDE.md#cli-commands) for the command list.

> [!important]
> Because the Action never has a terminal to prompt at, `update` and `clean` need `--yes` or they will abort without deleting anything.

## Site Layout and Rendering

These mirror the environment variables of the same name, and are only needed when your theme differs from the defaults. See [GUIDE.md](./GUIDE.md#environment-variables) for what each one does.

| Name                     | Description                                                                                     | Default value            |
| ------------------------ | ----------------------------------------------------------------------------------------------- | ------------------------ |
| `post-folder`            | Jekyll posts folder, relative to the site root. Some themes use `_articles`.                    | `_posts`                 |
| `img-folder`             | Where images are copied, relative to the site root.                                             | `assets/images/obsidian` |
| `includes-folder`        | Jekyll includes folder, relative to the site root. This is where `obsidian-callouts.html` goes. | `_includes`              |
| `math-rendering-mode`    | `inject_cdn` adds MathJax to posts with math; `metadata` only sets a frontmatter flag.          | `inject_cdn`             |
| `prevent-double-baseurl` | Set to `true` if your theme already prepends `site.baseurl` to links.                           | `false`                  |

## Outputs

| Name               | Description                                |
| ------------------ | ------------------------------------------ |
| `changed`          | `true` when the sync produced a change.    |
| `deletions`        | Number of files the sync would delete.     |
| `posts-written`    | Number of post files after the sync.       |
| `pull-request-url` | URL of the pull request opened or updated. |

```yaml
- uses: kckhchen/intaglio@v1
  id: sync
  with:
    jekyll-repo: username/jekyll-repo
    token: ${{ secrets.BLOG_PUSH_TOKEN }}
    args: update --force --yes

- if: steps.sync.outputs.deletions > 0
  run: echo "::notice::${{ steps.sync.outputs.pull-request-url }} deletes ${{ steps.sync.outputs.deletions }} file(s)"
```
