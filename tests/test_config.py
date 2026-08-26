import argparse
from pathlib import Path

import pytest

from src.config import Config, find_rc


def args(**kw):
    ns = argparse.Namespace(
        vault=None,
        jekyll=None,
        post_folder=None,
        img_folder=None,
        includes_folder=None,
        math_mode=None,
        prevent_double_baseurl=None,
    )
    for key, value in kw.items():
        setattr(ns, key, value)
    return ns


@pytest.fixture
def rc(tmp_path):
    def _write(content, name=".intagliorc", where=None):
        target = where or tmp_path
        target.mkdir(parents=True, exist_ok=True)
        (target / name).write_text(content, encoding="utf-8")
        return target

    return _write


class TestPrecedence:
    def test_rc_is_used(self, tmp_path, rc):
        rc("POST_FOLDER=_from_rc\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.post_folder == Path("_from_rc")
        assert cfg.sources["POST_FOLDER"] == ".intagliorc"

    def test_env_beats_rc(self, tmp_path, rc):
        rc("POST_FOLDER=_from_rc\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={"POST_FOLDER": "_from_env"})
        assert cfg.post_folder == Path("_from_env")
        assert cfg.sources["POST_FOLDER"] == "env"

    def test_flag_beats_env(self, tmp_path, rc):
        rc("POST_FOLDER=_from_rc\n")
        cfg = Config.resolve(
            args(post_folder="_from_flag"),
            cwd=tmp_path,
            env={"POST_FOLDER": "_from_env"},
        )
        assert cfg.post_folder == Path("_from_flag")
        assert cfg.sources["POST_FOLDER"] == "flag"

    def test_default_when_nothing_set(self, tmp_path):
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.post_folder == Path("_posts")
        assert cfg.sources["POST_FOLDER"] == "default"


class TestDiscovery:
    def test_rc_location_defines_jekyll_dir(self, tmp_path, rc):
        rc("POST_FOLDER=_posts\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.jekyll_dir == tmp_path

    def test_found_from_subdirectory(self, tmp_path, rc):
        rc("POST_FOLDER=_posts\n")
        sub = tmp_path / "_posts" / "nested"
        sub.mkdir(parents=True)
        cfg = Config.resolve(args(), cwd=sub, env={})
        assert cfg.jekyll_dir == tmp_path

    def test_search_stops_at_git_root(self, tmp_path, rc):
        rc("POST_FOLDER=_outer\n", where=tmp_path)
        inner = tmp_path / "inner"
        (inner / ".git").mkdir(parents=True)
        found, _ = find_rc(inner)
        assert found is None

    def test_explicit_jekyll_flag_wins(self, tmp_path, rc):
        rc("POST_FOLDER=_posts\n")
        other = tmp_path / "elsewhere"
        other.mkdir()
        cfg = Config.resolve(args(jekyll=str(other)), cwd=tmp_path, env={})
        assert cfg.jekyll_dir == other


class TestLegacyEnv:
    def test_dotenv_still_works(self, tmp_path, rc, capsys):
        rc("POST_FOLDER=_legacy\n", name=".env")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.post_folder == Path("_legacy")
        assert "deprecated" in capsys.readouterr().out

    def test_intagliorc_wins_when_both_present(self, tmp_path, rc):
        rc("POST_FOLDER=_old\n", name=".env")
        rc("POST_FOLDER=_new\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.post_folder == Path("_new")

    def test_no_warning_for_new_name(self, tmp_path, rc, capsys):
        rc("POST_FOLDER=_posts\n")
        Config.resolve(args(), cwd=tmp_path, env={})
        assert "deprecated" not in capsys.readouterr().out


class TestMisc:
    def test_unknown_key_warns(self, tmp_path, rc, capsys):
        rc("POST_FOLER=_typo\n")
        Config.resolve(args(), cwd=tmp_path, env={})
        assert "Unknown setting" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("no", False),
            ("", False),
        ],
    )
    def test_bool_parsing(self, tmp_path, rc, raw, expected):
        rc(f"PREVENT_DOUBLE_BASEURL={raw}\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.prevent_double_baseurl is expected

    def test_tilde_is_expanded(self, tmp_path, rc):
        rc("POST_FOLDER=_posts\n")
        cfg = Config.resolve(args(vault="~/vault"), cwd=tmp_path, env={})
        assert "~" not in str(cfg.vault_dir)

    def test_derived_paths(self, tmp_path, rc):
        rc("POST_FOLDER=_articles\nIMG_FOLDER=assets/img\n")
        cfg = Config.resolve(args(), cwd=tmp_path, env={})
        assert cfg.post_dir == tmp_path / "_articles"
        assert cfg.img_dir == tmp_path / "assets/img"
        assert cfg.includes_dir == tmp_path / "_includes"
