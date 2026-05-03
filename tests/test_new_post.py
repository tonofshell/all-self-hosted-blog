import sys
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import new_post


class TestSlugify:
    def test_lowercases(self):
        assert new_post.slugify("Hello World") == "hello-world"

    def test_spaces_become_hyphens(self):
        assert new_post.slugify("foo bar baz") == "foo-bar-baz"

    def test_removes_special_chars(self):
        assert new_post.slugify("Hello, World!") == "hello-world"

    def test_collapses_consecutive_hyphens(self):
        assert new_post.slugify("foo -- bar") == "foo-bar"

    def test_strips_leading_trailing_hyphens(self):
        assert new_post.slugify("-hello-") == "hello"

    def test_underscores_become_hyphens(self):
        assert new_post.slugify("foo_bar") == "foo-bar"

    def test_empty_string(self):
        assert new_post.slugify("") == ""

    def test_numbers_preserved(self):
        assert new_post.slugify("IPv6 Setup") == "ipv6-setup"

    def test_apostrophe_removed(self):
        assert new_post.slugify("don't do it") == "dont-do-it"


class TestParseTags:
    def test_single_tag(self):
        assert new_post.parse_tags("docker") == ["docker"]

    def test_multiple_tags(self):
        assert new_post.parse_tags("docker, linux, self-hosting") == [
            "docker",
            "linux",
            "self-hosting",
        ]

    def test_empty_string(self):
        assert new_post.parse_tags("") == []

    def test_strips_whitespace(self):
        assert new_post.parse_tags("  docker , linux ") == ["docker", "linux"]

    def test_ignores_empty_segments(self):
        assert new_post.parse_tags("docker,,linux") == ["docker", "linux"]


class TestBuildFrontMatter:
    def test_required_fields_present(self):
        fm = new_post.build_front_matter("My Post", "", [])
        assert "title: My Post" in fm
        assert f"date: {date.today()}" in fm

    def test_starts_and_ends_with_delimiters(self):
        fm = new_post.build_front_matter("Post", "", [])
        assert fm.startswith("---\n")
        # second delimiter must appear after the first four chars
        assert "---\n" in fm[4:]

    def test_with_description(self):
        fm = new_post.build_front_matter("Post", "A description", [])
        assert "description: A description" in fm

    def test_without_description(self):
        fm = new_post.build_front_matter("Post", "", [])
        assert "description" not in fm

    def test_with_tags(self):
        fm = new_post.build_front_matter("Post", "", ["docker", "linux"])
        assert "tags: [docker, linux]" in fm

    def test_without_tags(self):
        fm = new_post.build_front_matter("Post", "", [])
        assert "tags" not in fm

    def test_always_has_comments_true(self):
        fm = new_post.build_front_matter("Post", "", [])
        assert "comments: true" in fm


class TestOpenInEditor:
    def test_uses_editor_env_var(self, tmp_path):
        test_file = tmp_path / "post.md"
        test_file.write_text("")
        with patch.dict("os.environ", {"EDITOR": "myeditor", "VISUAL": ""}):
            with patch("subprocess.run") as mock_run:
                new_post.open_in_editor(test_file)
        mock_run.assert_called_once_with(["myeditor", str(test_file)])

    def test_falls_back_to_visual_env_var(self, tmp_path):
        test_file = tmp_path / "post.md"
        test_file.write_text("")
        with patch.dict("os.environ", {"EDITOR": "", "VISUAL": "code"}):
            with patch("subprocess.run") as mock_run:
                new_post.open_in_editor(test_file)
        mock_run.assert_called_once_with(["code", str(test_file)])

    def test_falls_back_to_system_candidate(self, tmp_path):
        test_file = tmp_path / "post.md"
        test_file.write_text("")
        which_found = MagicMock(returncode=0)
        editor_launch = MagicMock()
        with patch.dict("os.environ", {"EDITOR": "", "VISUAL": ""}):
            with patch("subprocess.run", side_effect=[which_found, editor_launch]) as mock_run:
                new_post.open_in_editor(test_file)
        # first call is "which nano", second is launching the editor
        assert mock_run.call_count == 2
        assert mock_run.call_args_list[0][0][0] == ["which", "nano"]

    def test_prints_message_when_no_editor_found(self, tmp_path, capsys):
        test_file = tmp_path / "post.md"
        test_file.write_text("")
        which_not_found = MagicMock(returncode=1)
        with patch.dict("os.environ", {"EDITOR": "", "VISUAL": ""}):
            with patch("subprocess.run", return_value=which_not_found):
                new_post.open_in_editor(test_file)
        out = capsys.readouterr().out
        assert "No editor found" in out
        assert str(test_file) in out
