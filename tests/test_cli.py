import pytest

from intaglio import cli

# ---------------------------------------------------------------------------
# subcommand routing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "argv, expected",
    [
        (["run"], cli.cmd_run),
        (["update"], cli.cmd_update),
        (["clean"], cli.cmd_clean),
        (["init"], cli.cmd_init),
        (["config"], cli.cmd_config),
    ],
)
def test_subcommand_dispatches_to_its_handler(argv, expected):
    args = cli.setup_parser().parse_args(argv)
    assert args.func is expected


def test_run_accepts_its_own_flags():
    args = cli.setup_parser().parse_args(
        ["run", "--dry", "--force", "--layout", "page", "--only", "A Post.md"]
    )
    assert (args.dry, args.force, args.layout, args.only) == (
        True,
        True,
        "page",
        "A Post.md",
    )


@pytest.mark.parametrize("command", ["run", "update", "clean", "config"])
def test_config_overrides_are_shared_across_commands(command):
    args = cli.setup_parser().parse_args(
        [command, "--vault", "/v", "--jekyll", "/j", "--math-mode", "metadata"]
    )
    assert (args.vault, args.jekyll, args.math_mode) == ("/v", "/j", "metadata")


@pytest.mark.parametrize("command", ["update", "clean"])
def test_dry_is_rejected_where_it_has_no_meaning(command):
    with pytest.raises(SystemExit):
        cli.setup_parser().parse_args([command, "--dry"])


@pytest.mark.parametrize("command", ["update", "clean"])
def test_only_is_rejected_on_update_and_clean(command):
    with pytest.raises(SystemExit):
        cli.setup_parser().parse_args([command, "--only", "A Post.md"])


def test_init_takes_no_config_overrides():
    with pytest.raises(SystemExit):
        cli.setup_parser().parse_args(["init", "--vault", "/v"])


def test_run_and_clean_are_separate_actions():
    parser = cli.setup_parser()
    assert parser.parse_args(["run"]).func is not parser.parse_args(["clean"]).func


# legacy flag shim


@pytest.mark.parametrize(
    "legacy, expected",
    [
        (["--force"], ["run", "--force"]),
        (["-f"], ["run", "-f"]),
        (["--dry"], ["run", "--dry"]),
        (["--only", "A Post.md"], ["run", "--only", "A Post.md"]),
        (["--cleanup"], ["clean"]),
        (["-c"], ["clean"]),
        (["--update"], ["update"]),
        (["-u"], ["update"]),
        (["--init"], ["init"]),
        (["--show-config"], ["config"]),
        (["--update", "--force", "--yes"], ["update", "--force", "--yes"]),
        (["--show-config", "--vault", "/v"], ["config", "--vault", "/v"]),
        (["-cy"], ["clean", "-y"]),
        (["-uf"], ["update", "-f"]),
        (["-fy"], ["run", "-fy"]),
    ],
)
def test_rewrite_legacy(legacy, expected):
    assert cli.rewrite_legacy(list(legacy)) == expected


@pytest.mark.parametrize(
    "argv", [[], ["run", "--force"], ["clean", "--yes"], ["config"]]
)
def test_rewrite_legacy_leaves_subcommands_alone(argv):
    assert cli.rewrite_legacy(list(argv)) == argv


@pytest.mark.parametrize("argv", [["-h"], ["--help"], ["--version"]])
def test_rewrite_legacy_passes_through_help_and_version(argv):
    assert cli.rewrite_legacy(list(argv)) == argv


def test_rewrite_legacy_drops_flags_init_used_to_ignore():
    assert cli.rewrite_legacy(["--init", "--vault", "/v"]) == ["init"]


@pytest.mark.parametrize(
    "argv",
    [
        ["--cleanup", "--update"],
        ["-c", "-u"],
        ["-cu"],
        ["--init", "--show-config"],
    ],
)
def test_rewrite_legacy_rejects_conflicting_verbs(argv, capsys):
    with pytest.raises(SystemExit) as exc:
        cli.rewrite_legacy(list(argv))
    assert exc.value.code == 2
    assert "cannot be combined" in capsys.readouterr().err


def test_rewrite_legacy_allows_a_repeated_verb():
    assert cli.rewrite_legacy(["-c", "--cleanup"]) == ["clean"]


def test_rewrite_legacy_warns_on_stderr(capsys):
    cli.rewrite_legacy(["--update", "--yes"])
    err = capsys.readouterr().err
    assert "deprecated" in err
    assert "intaglio update --yes" in err


def test_rewrite_legacy_is_silent_for_subcommands(capsys):
    cli.rewrite_legacy(["update", "--yes"])
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "legacy, expected_handler",
    [
        (["--update", "--force", "--yes"], "cmd_update"),
        (["--cleanup", "-y"], "cmd_clean"),
        (["--force"], "cmd_run"),
        (["--show-config"], "cmd_config"),
        (["--init"], "cmd_init"),
    ],
)
def test_legacy_argv_still_parses_end_to_end(legacy, expected_handler):
    parser = cli.setup_parser()
    args = parser.parse_args(cli.rewrite_legacy(list(legacy)))
    assert args.func is getattr(cli, expected_handler)


# main()


def test_bare_invocation_prints_help_and_exits_nonzero(capsys):
    code = cli.main([])
    out = capsys.readouterr().out
    assert code == 2
    assert "usage: intaglio" in out
    assert "run" in out


def test_main_returns_zero_on_success(monkeypatch):
    monkeypatch.setattr(cli, "cmd_init", lambda args: None)
    assert cli.main(["init"]) == 0


def test_main_dispatches_legacy_argv(monkeypatch):
    seen = {}
    monkeypatch.setattr(cli, "cmd_clean", lambda args: seen.setdefault("args", args))

    assert cli.main(["--cleanup", "--yes"]) == 0
    assert seen["args"].yes is True


def test_version_flag_reports_a_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.setup_parser().parse_args(["--version"])
    assert exc.value.code == 0
    assert "intaglio" in capsys.readouterr().out
