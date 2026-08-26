# Changelog

## [1.4.0](https://github.com/kckhchen/intaglio/compare/v1.3.1...v1.4.0) (2026-08-26)


### Features

* add cli.py to separate flag parsing from main ([16117bd](https://github.com/kckhchen/intaglio/commit/16117bdb03028d0acb4ab6d8cd093d690f7a1607))
* add intagliorc init functionality ([c90d328](https://github.com/kckhchen/intaglio/commit/c90d328b21de54487f2f7bd2524b87bae53eb5e0))
* add legacy support for bare commands ([6c6e774](https://github.com/kckhchen/intaglio/commit/6c6e774a921634f775076a6c768127563565a704))
* add missing date warning ([4ba84e1](https://github.com/kckhchen/intaglio/commit/4ba84e1cd5cde6f21adba2cc6c114ad2a7659144))
* change some flags to subpraser with legacy support ([31c65c9](https://github.com/kckhchen/intaglio/commit/31c65c97695791d6b2792674eebcb03c9dfdd484))
* update action.yml to reflect packaging ([0248e70](https://github.com/kckhchen/intaglio/commit/0248e701c9dde0954f2232cc593cd5b5f0ef3a85))
* update config.py to include .intagliorc support ([76b6f12](https://github.com/kckhchen/intaglio/commit/76b6f12a2beef34173c0e5337e051d7dcd33e31c))


### Bug Fixes

* prevent traceback printing when ctrl+c on cleanup confirmation ([bdf4df0](https://github.com/kckhchen/intaglio/commit/bdf4df036aba29879b15044317b47222018ecb80))

## [1.3.1](https://github.com/kckhchen/intaglio/compare/v1.3.0...v1.3.1) (2026-08-23)


### Bug Fixes

* change path to posix before string interpolation ([16599da](https://github.com/kckhchen/intaglio/commit/16599da2462d31562c5e3447082327cd925458c9))

## [1.3.0](https://github.com/kckhchen/intaglio/compare/v1.2.2...v1.3.0) (2026-08-22)


### Features

* add liquid tag shielding ([e9e5098](https://github.com/kckhchen/intaglio/commit/e9e5098c342021db68fc92dd8a5307133d54c858))

## [1.2.2](https://github.com/kckhchen/intaglio/compare/v1.2.1...v1.2.2) (2026-08-22)


### Bug Fixes

* add environment variable support for actions ([fefc1b5](https://github.com/kckhchen/intaglio/commit/fefc1b54e9b298657b077746e9546273f61f8d8b))

## [1.2.1](https://github.com/kckhchen/intaglio/compare/v1.2.0...v1.2.1) (2026-08-21)


### Bug Fixes

* change other reference to old names to intaglio ([963a71a](https://github.com/kckhchen/intaglio/commit/963a71ad70a3a331c449a588014289989edf844f))

## [1.2.0](https://github.com/kckhchen/intaglio/compare/v1.1.1...v1.2.0) (2026-08-21)


### Features

* enhance callout bg and accent colors to render well on both dark and light themes ([84f7858](https://github.com/kckhchen/intaglio/commit/84f78580f232dee1406d391393e9e971d17b9d66))

## [1.1.1](https://github.com/kckhchen/intaglio/compare/v1.1.0...v1.1.1) (2026-08-21)


### Miscellaneous Chores

* release v1.1.1 ([8b5cc49](https://github.com/kckhchen/intaglio/commit/8b5cc495455ade66247c0fc8d33015ebb8bec914))

## [1.1.0](https://github.com/kckhchen/intaglio/compare/v1.0.0...v1.1.0) (2026-08-21)


### Features

* change tool name after rename to intaglio ([ccf844e](https://github.com/kckhchen/intaglio/commit/ccf844e99c78cdd64d641d8bde6e3701917ec747))

## [1.0.0](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.9.1...v1.0.0) (2026-08-21)


### Features

* add action stopper for same repo ([645ccc3](https://github.com/kckhchen/obsidian-2-jekyll/commit/645ccc3edb7030316cf64c0f7130c7957034b4ed))
* enhance md globbing and block post_dir scanning ([b37daa5](https://github.com/kckhchen/obsidian-2-jekyll/commit/b37daa5c38d3da34506b737bbf307b5f7a871e35))


### Documentation

* update README and action_config ([2f50562](https://github.com/kckhchen/obsidian-2-jekyll/commit/2f50562b6cf9d06b664b4901d52b9ac46a0547ec))

## [0.9.1](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.9.0...v0.9.1) (2026-08-21)


### ⚠ BREAKING CHANGES

* release v0.9.1

### Miscellaneous Chores

* release v0.9.1 ([39b5f89](https://github.com/kckhchen/obsidian-2-jekyll/commit/39b5f8942192a6a72a498114c864d8fc70557fae))

## [0.9.0](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.8.2...v0.9.0) (2026-08-21)


### Features

* add --yes flag for automation ([5972ed1](https://github.com/kckhchen/obsidian-2-jekyll/commit/5972ed1a44b2f1e1d3b847d3be2b8e4b33cefb7c))
* add github action bot ([0a31944](https://github.com/kckhchen/obsidian-2-jekyll/commit/0a319441479a153363996e3334eee5ddb32623f7))
* change automation workflow to creating PR instead of pushing directly ([d12cd5b](https://github.com/kckhchen/obsidian-2-jekyll/commit/d12cd5b6e05603b488b0671bf6dc1fc6cba4986d))


### Bug Fixes

* remove pip cache and PR HEAD problem ([5cb12c0](https://github.com/kckhchen/obsidian-2-jekyll/commit/5cb12c04f616b012c08723e3691aa8936933a1b7))


### Documentation

* fix typo and add compatible version in README ([c7ae8e0](https://github.com/kckhchen/obsidian-2-jekyll/commit/c7ae8e018bb2282ecd7648449d86eadbc83de167))

## [0.8.2](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.8.1...v0.8.2) (2026-08-08)


### Bug Fixes

* make _get_post_images scan images from the output end instead of input end ([8bc2f42](https://github.com/kckhchen/obsidian-2-jekyll/commit/8bc2f4295171e29cc66d8eaa573acfd16469d2cc))
* make block math pattern track linebreaks ([28a7590](https://github.com/kckhchen/obsidian-2-jekyll/commit/28a759095f2501ffc098f28435eb913759a86c8a))

## [0.8.1](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.8.0...v0.8.1) (2026-08-07)


### Features

* add environmental variable check in config.py ([608b8ce](https://github.com/kckhchen/obsidian-2-jekyll/commit/608b8ce61a27c28be0d6520d89ac7a95d91e406b))
* update shared folder check in image cleanup process ([a8d00b9](https://github.com/kckhchen/obsidian-2-jekyll/commit/a8d00b9a9ebf8e8bffc9fa86f8c22df2d6dd42bb))

## [0.8.0](https://github.com/kckhchen/obsidian-2-jekyll/compare/v0.7.2...v0.8.0) (2026-08-07)


### ⚠ BREAKING CHANGES

* restructure code so env vars are read from .env via config

### Features

* add generator signature in frontmatter for mark managed files ([30c1812](https://github.com/kckhchen/obsidian-2-jekyll/commit/30c18120f827fdd85670bce95c6478a74bde6acd))
* add Makefile for formatting and testing commands ([ecf9742](https://github.com/kckhchen/obsidian-2-jekyll/commit/ecf97428df7456b55685670cae1fafc9ea9c07d1))


### Bug Fixes

* correct typo in config.py and set override=False for load_env ([13c05a0](https://github.com/kckhchen/obsidian-2-jekyll/commit/13c05a0466c43ce2b9e9f2d70d60e7ff4144372d))
* fix ci.yml to create venv first ([c6115c6](https://github.com/kckhchen/obsidian-2-jekyll/commit/c6115c6834a00c81d2099a16968ff8158ce91736))
* move make_path to fs_ops ([88934df](https://github.com/kckhchen/obsidian-2-jekyll/commit/88934dfd0ef89fce7c8a0cfee916abf97c244ec3))
* remove path making process from main.py ([effbc06](https://github.com/kckhchen/obsidian-2-jekyll/commit/effbc06785c7be586d63710244ef23c6c21cf092))
* remove uv and use pip manager for ci.yml ([c06266c](https://github.com/kckhchen/obsidian-2-jekyll/commit/c06266ca3ba6cbca93a5f047a932b612edea517a))
* **utils:** remove misleading ctime ([e78a67c](https://github.com/kckhchen/obsidian-2-jekyll/commit/e78a67cecc383f556d0a7f77efc031167d484ff3))
* validate config in main to avoid import trap ([a5208a5](https://github.com/kckhchen/obsidian-2-jekyll/commit/a5208a57c960602502e323904278e5befe452305))


### Code Refactoring

* restructure code so env vars are read from .env via config ([dac083d](https://github.com/kckhchen/obsidian-2-jekyll/commit/dac083d8964c301bd584926848344271e2f19364))
