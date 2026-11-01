import io
import os
import re
import zipfile
from typing import Dict, Optional, Tuple
from urllib.parse import quote

import httpx

# Limits so a huge repo can't use up all the memory
MAX_ZIP_BYTES = 50 * 1024 * 1024   # size of the download
MAX_FILE_BYTES = 500 * 1024        # size of any one file we keep
MAX_FILES = 3000                   # number of files we keep

# Folders that are almost never useful to look at
SKIP_FOLDERS = {".git", "node_modules", "__pycache__", "venv", ".venv", "env", "dist", "build", ".next", ".idea", ".vscode"}

# Allowed characters in a GitHub owner or repo name (and it can't be only dots, like "..")
NAME_PATTERN = re.compile(r"^(?!\.+$)[A-Za-z0-9_.-]+$")


class GitHubError(Exception):
    """Raised when a repo can't be downloaded, with a message that's safe to show the user."""


def parse_github_url(url: str) -> Tuple[str, str, Optional[str]]:
    """
    Splits a GitHub link into its owner, repo name and branch.

    Accepts links like:
        https://github.com/owner/repo
        https://github.com/owner/repo.git
        https://github.com/owner/repo/tree/some-branch
        github.com/owner/repo
        owner/repo

    Returns:
        (owner, repo, branch). branch is None when the link doesn't name one,
        which means the repo's default branch is used.

    Raises:
        GitHubError: If the link isn't a GitHub repo link
    """
    cleaned = url.strip()
    cleaned = re.sub(r"^https?://", "", cleaned)
    cleaned = re.sub(r"^(www\.)?github\.com/", "", cleaned)
    parts = [p for p in cleaned.split("/") if p]

    if len(parts) < 2:
        raise GitHubError("That doesn't look like a GitHub repo link. Try https://github.com/owner/repo")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not NAME_PATTERN.match(owner) or not NAME_PATTERN.match(repo):
        raise GitHubError("That doesn't look like a GitHub repo link. Try https://github.com/owner/repo")

    branch = None
    if len(parts) > 3 and parts[2] == "tree":
        branch = "/".join(parts[3:])
    return owner, repo, branch


def fetch_repo_files(url: str) -> Dict:
    """
    Downloads a public GitHub repo and returns its text files.

    Args:
        url: A GitHub repo link (see parse_github_url for the formats accepted)

    Returns:
        A dictionary with:
            - "name": the repo name
            - "files": a dictionary mapping each file path to its contents
            - "skipped": how many files were left out (binary, too large or over the limit)

    Raises:
        GitHubError: If the repo can't be found or downloaded
    """
    owner, repo, branch = parse_github_url(url)

    # GitHub gives us the whole repo as one zip file
    api_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    if branch:
        api_url += "/" + quote(branch, safe="")

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "git-repo-visualizer"}
    # Optional: a token raises GitHub's limit from 60 to 5000 downloads an hour
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    zip_bytes = _download(api_url, headers)
    return {"name": repo, **_read_zip(zip_bytes)}


def _download(api_url: str, headers: Dict[str, str]) -> bytes:
    """Downloads the zip, stopping if it goes over MAX_ZIP_BYTES."""
    try:
        with httpx.stream("GET", api_url, headers=headers, follow_redirects=True, timeout=60) as response:
            if response.status_code == 404:
                raise GitHubError("Repo or branch not found. Private repos aren't supported yet.")
            if response.status_code in (403, 429):
                raise GitHubError("GitHub's download limit was reached. Wait a bit, or set GITHUB_TOKEN in backend/.env")
            if response.status_code != 200:
                raise GitHubError(f"GitHub returned an error ({response.status_code}).")

            data = bytearray()
            for chunk in response.iter_bytes():
                data.extend(chunk)
                if len(data) > MAX_ZIP_BYTES:
                    raise GitHubError("This repo is too big to load (over 50 MB).")
            return bytes(data)
    except httpx.HTTPError as e:
        raise GitHubError(f"Couldn't reach GitHub: {e}")


def _read_zip(zip_bytes: bytes) -> Dict:
    """Pulls the text files out of the downloaded zip."""
    files = {}
    skipped = 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue

            # Every path starts with a folder like "owner-repo-abc123/", so drop it
            path = info.filename.split("/", 1)[-1]
            if not path or any(part in SKIP_FOLDERS for part in path.split("/")[:-1]):
                continue

            if info.file_size > MAX_FILE_BYTES or len(files) >= MAX_FILES:
                skipped += 1
                continue

            raw = archive.read(info)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                skipped += 1  # images, compiled files, etc.
                continue
            if "\x00" in text:
                skipped += 1
                continue

            # Use \n line endings everywhere so line numbers match up
            files[path] = text.replace("\r\n", "\n")

    return {"files": files, "skipped": skipped}
