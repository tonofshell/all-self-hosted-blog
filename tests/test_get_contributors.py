import json
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import get_contributors


def _urlopen_mock(data):
    """Return a MagicMock that behaves as a urlopen context manager returning `data`."""
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.read.return_value = json.dumps(data).encode()
    return mock_resp


def _commit(login):
    return {"author": {"login": login}}


class TestGithubGet:
    def test_returns_parsed_json(self):
        data = [{"sha": "abc", "author": {"login": "alice"}}]
        with patch("urllib.request.urlopen", return_value=_urlopen_mock(data)):
            result = get_contributors.github_get("repos/foo/bar/commits", "token")
        assert result == data

    def test_builds_correct_url(self):
        with patch("urllib.request.urlopen", return_value=_urlopen_mock([])) as mock_open:
            get_contributors.github_get("repos/foo/bar/commits", "token")
        req = mock_open.call_args[0][0]
        assert req.full_url == "https://api.github.com/repos/foo/bar/commits"

    def test_strips_leading_slash_from_path(self):
        with patch("urllib.request.urlopen", return_value=_urlopen_mock([])) as mock_open:
            get_contributors.github_get("/repos/foo/bar", "token")
        req = mock_open.call_args[0][0]
        assert req.full_url == "https://api.github.com/repos/foo/bar"

    def test_passes_token_in_authorization_header(self):
        with patch("urllib.request.urlopen", return_value=_urlopen_mock([])) as mock_open:
            get_contributors.github_get("repos/foo/bar", "mytoken")
        req = mock_open.call_args[0][0]
        # urllib capitalizes header keys
        assert req.get_header("Authorization") == "Bearer mytoken"


class TestGetContributors:
    def test_returns_logins(self):
        commits = [_commit("alice"), _commit("bob")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["alice", "bob"]

    def test_filters_bots(self):
        commits = [_commit("alice"), _commit("github-actions[bot]")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["alice"]

    def test_deduplicates_logins(self):
        commits = [_commit("alice"), _commit("alice"), _commit("bob")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["alice", "bob"]

    def test_preserves_first_occurrence_order(self):
        commits = [_commit("bob"), _commit("alice"), _commit("bob")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["bob", "alice"]

    def test_handles_null_author(self):
        commits = [{"author": None}, _commit("bob")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["bob"]

    def test_handles_missing_login(self):
        commits = [{"author": {}}, _commit("alice")]
        with patch.object(get_contributors, "github_get", return_value=commits):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == ["alice"]

    def test_paginates_when_full_page_returned(self):
        page1 = [_commit(f"user{i}") for i in range(100)]
        page2 = [_commit("extra")]
        with patch.object(get_contributors, "github_get", side_effect=[page1, page2]) as mock_get:
            with patch("time.sleep"):
                result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert len(result) == 101
        assert mock_get.call_count == 2

    def test_stops_pagination_when_page_less_than_100(self):
        page1 = [_commit(f"user{i}") for i in range(50)]
        with patch.object(get_contributors, "github_get", return_value=page1) as mock_get:
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert mock_get.call_count == 1

    def test_stops_pagination_when_empty_page(self):
        with patch.object(get_contributors, "github_get", return_value=[]) as mock_get:
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == []
        assert mock_get.call_count == 1

    def test_handles_http_error(self, capsys):
        with patch.object(
            get_contributors,
            "github_get",
            side_effect=urllib.error.HTTPError("url", 404, "Not Found", {}, None),
        ):
            result = get_contributors.get_contributors("docs/blog/post.md", "token")
        assert result == []
        assert "API error" in capsys.readouterr().err


class TestPatchContributors:
    def test_injects_contributors_line(self, tmp_path):
        post = tmp_path / "post.md"
        post.write_text("---\ntitle: Hello\ndate: 2026-01-01\n---\n\nContent.\n")
        get_contributors.patch_contributors(post, ["alice", "bob"])
        assert "contributors: [alice, bob]" in post.read_text()

    def test_replaces_existing_contributors(self, tmp_path):
        post = tmp_path / "post.md"
        post.write_text("---\ntitle: Hello\ncontributors: [old]\ndate: 2026-01-01\n---\n\nContent.\n")
        get_contributors.patch_contributors(post, ["alice"])
        text = post.read_text()
        assert "contributors: [alice]" in text
        assert "contributors: [old]" not in text

    def test_preserves_body_content(self, tmp_path):
        post = tmp_path / "post.md"
        body = "\n\n# Heading\n\nSome content paragraph.\n"
        post.write_text(f"---\ntitle: Hello\ndate: 2026-01-01\n---\n{body}")
        get_contributors.patch_contributors(post, ["alice"])
        assert body in post.read_text()

    def test_preserves_other_front_matter_fields(self, tmp_path):
        post = tmp_path / "post.md"
        post.write_text("---\ntitle: Hello\ndate: 2026-01-01\ntags: [docker]\n---\n\nBody.\n")
        get_contributors.patch_contributors(post, ["alice"])
        text = post.read_text()
        assert "title: Hello" in text
        assert "date: 2026-01-01" in text
        assert "tags: [docker]" in text

    def test_output_has_valid_front_matter_structure(self, tmp_path):
        post = tmp_path / "post.md"
        post.write_text("---\ntitle: Hello\ndate: 2026-01-01\n---\n\nBody.\n")
        get_contributors.patch_contributors(post, ["alice"])
        text = post.read_text()
        assert text.startswith("---\n")
        assert "---\n" in text[4:]

    def test_skips_file_without_front_matter(self, tmp_path, capsys):
        post = tmp_path / "post.md"
        post.write_text("No front matter here.\n")
        original = post.read_text()
        get_contributors.patch_contributors(post, ["alice"])
        assert post.read_text() == original
        assert "No front matter" in capsys.readouterr().err
