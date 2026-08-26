import pytest

from intaglio import cli


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


# bare invocation


class _Cfg:
    def __init__(self, vault="/v", jekyll="/j"):
        self.vault_dir = vault
        self.jekyll_dir = jekyll


@pytest.fixture
def bare(monkeypatch):
    """Bare `intaglio` with a stub config, a stub tty, and cmd_run disarmed."""
    state = {"resolves": 0, "ran": None, "tty": True, "answer": "", "cfg": _Cfg()}

    def resolve(args=None, **kwargs):
        state["resolves"] += 1
        return state["cfg"]

    monkeypatch.setattr(cli.Config, "resolve", staticmethod(resolve))
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: state["tty"])
    monkeypatch.setattr("builtins.input", lambda _="": state["answer"])
    monkeypatch.setattr(cli, "cmd_run", lambda args: state.update(ran=args))
    return state


def test_bare_without_config_shows_help(bare, capsys):
    bare["cfg"] = _Cfg(vault=None, jekyll=None)

    assert cli.main([]) == 2

    captured = capsys.readouterr()
    assert "usage: intaglio" in captured.out
    assert "intaglio init" in captured.err
    assert bare["ran"] is None


def test_bare_on_a_tty_asks_before_touching_the_vault(bare, capsys):
    bare["answer"] = "n"

    assert cli.main([]) == 0

    out = capsys.readouterr().out
    assert "/v" in out and "/j" in out
    assert "Aborted." in out
    assert bare["ran"] is None


@pytest.mark.parametrize("answer", ["y", "Y", "yes", " y "])
def test_bare_on_a_tty_runs_when_confirmed(bare, answer):
    bare["answer"] = answer

    assert cli.main([]) == 0
    assert bare["ran"] is not None


@pytest.mark.parametrize("answer", ["", "n", "no", "maybe", "q"])
def test_bare_on_a_tty_defaults_to_no(bare, answer):
    bare["answer"] = answer

    assert cli.main([]) == 0
    assert bare["ran"] is None


@pytest.mark.parametrize("interrupt", [EOFError, KeyboardInterrupt])
def test_bare_treats_ctrl_c_and_ctrl_d_as_no(bare, monkeypatch, capsys, interrupt):
    def raise_it(_=""):
        raise interrupt

    monkeypatch.setattr("builtins.input", raise_it)

    assert cli.main([]) == 0
    assert "Aborted." in capsys.readouterr().out
    assert bare["ran"] is None


def test_bare_without_a_tty_runs_unattended(bare, capsys):
    # cron, CI and the Action: no prompt, same behaviour as before subcommands
    bare["tty"] = False
    bare["answer"] = "n"  # would abort if it were ever asked

    assert cli.main([]) == 0
    assert bare["ran"] is not None
    assert "deprecated" in capsys.readouterr().err


def test_bare_resolves_config_only_once(bare):
    bare["answer"] = "y"
    cli.main([])
    assert bare["resolves"] == 1


def test_bare_hands_the_resolved_config_to_run(bare):
    bare["answer"] = "y"
    cli.main([])
    assert bare["ran"].preresolved_cfg is bare["cfg"]


def test_explicit_run_never_prompts(bare):
    bare["answer"] = "n"  # would abort a bare invocation

    assert cli.main(["run"]) == 0
    assert bare["ran"] is not None


def test_run_accepts_yes_for_backward_compatibility():
    args = cli.setup_parser().parse_args(["run", "--yes"])
    assert args.yes is True
    assert cli.rewrite_legacy(["--yes"]) == ["run", "--yes"]
