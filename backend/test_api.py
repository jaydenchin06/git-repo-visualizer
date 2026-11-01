from fastapi.testclient import TestClient

from backend import main
from backend.github import GitHubError

client = TestClient(main.app)


def test_analyze_pasted_code():
    response = client.post("/api/analyze/code", json={"code": "class A:\r\n    def b(self):\r\n        pass\r\n"})
    data = response.json()

    assert data["status"] == "success"
    assert data["files"] == {"pasted_code.py": "class A:\n    def b(self):\n        pass\n"}
    file_node = data["tree"]["children"][0]
    assert file_node["name"] == "pasted_code.py"
    assert file_node["children"][0]["children"][0]["name"] == "b"


def test_analyze_pasted_code_strips_paths_from_filename():
    response = client.post("/api/analyze/code", json={"code": "x = 1", "filename": "..\\secret/app.py"})
    assert list(response.json()["files"]) == ["app.py"]


def test_analyze_pasted_code_with_syntax_error():
    response = client.post("/api/analyze/code", json={"code": "def oops(:"})
    file_node = response.json()["tree"]["children"][0]
    assert file_node["error"].startswith("Syntax error")


def test_analyze_repo(monkeypatch):
    # Pretend to download a repo so the test doesn't need the internet
    def fake_fetch(url):
        return {"name": "demo", "files": {"app.py": "def main():\n    pass\n"}, "skipped": 2}

    monkeypatch.setattr(main, "fetch_repo_files", fake_fetch)
    data = client.post("/api/analyze/repo", json={"url": "https://github.com/me/demo"}).json()

    assert data["status"] == "success"
    assert data["tree"]["name"] == "demo"
    assert data["skipped"] == 2


def test_analyze_repo_error(monkeypatch):
    def fake_fetch(url):
        raise GitHubError("Repo or branch not found.")

    monkeypatch.setattr(main, "fetch_repo_files", fake_fetch)
    data = client.post("/api/analyze/repo", json={"url": "https://github.com/me/missing"}).json()

    assert data == {"status": "error", "message": "Repo or branch not found."}


def test_explain_returns_placeholder():
    data = client.post("/api/explain", json={"code": "def f(): pass", "name": "f", "type": "function", "language": "python"}).json()

    assert data["status"] == "success"
    assert "def f(): pass" in data["explanation"]
