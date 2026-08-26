# Actions Configuration

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
