import io
import zipfile

import pytest

from backend.github import GitHubError, parse_github_url, _read_zip


@pytest.mark.parametrize("url, expected", [
    ("https://github.com/owner/repo", ("owner", "repo", None)),
    ("https://github.com/owner/repo.git", ("owner", "repo", None)),
    ("http://www.github.com/owner/repo/", ("owner", "repo", None)),
    ("github.com/owner/repo/tree/dev", ("owner", "repo", "dev")),
    ("https://github.com/owner/repo/tree/feature/login", ("owner", "repo", "feature/login")),
    ("owner/repo", ("owner", "repo", None)),
])
def test_parse_github_url(url, expected):
    assert parse_github_url(url) == expected


@pytest.mark.parametrize("url", ["", "https://github.com/owner", "owner/re po", "../../etc/passwd/x"])
def test_parse_github_url_rejects_bad_links(url):
    with pytest.raises(GitHubError):
        parse_github_url(url)


def test_read_zip_keeps_text_files_and_skips_the_rest():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("owner-repo-abc123/", "")
        archive.writestr("owner-repo-abc123/main.py", "print('hi')\r\n")
        archive.writestr("owner-repo-abc123/src/app.py", "x = 1\n")
        archive.writestr("owner-repo-abc123/node_modules/lib/index.js", "ignored")
        archive.writestr("owner-repo-abc123/logo.png", b"\x89PNG\r\n\x1a\n\x00\x00")

    result = _read_zip(buffer.getvalue())

    assert result["files"] == {"main.py": "print('hi')\n", "src/app.py": "x = 1\n"}
    assert result["skipped"] == 1  # the png
