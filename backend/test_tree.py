from backend.parser import parse_python, parse_code
from backend.tree import build_tree


def test_parse_python_finds_nested_symbols():
    code = '''
class Outer:
    @property
    def size(self):
        return 1

    class Inner:
        async def run(self):
            def helper():
                pass
'''
    symbols = parse_python(code)

    outer = symbols[0]
    assert (outer["name"], outer["type"]) == ("Outer", "class")

    size = outer["children"][0]
    assert (size["name"], size["type"]) == ("size", "method")
    # The decorator line is included
    assert size["line_start"] == 3

    inner = outer["children"][1]
    run = inner["children"][0]
    assert (run["name"], run["type"]) == ("run", "method")
    assert run["children"][0]["name"] == "helper"
    assert run["children"][0]["type"] == "function"


def test_parse_code_handles_unknown_languages_and_errors():
    assert parse_code("let x = 1", "app.js") == {"language": "javascript", "symbols": [], "error": None}
    assert parse_code("hello", "notes") == {"language": None, "symbols": [], "error": None}

    broken = parse_code("def oops(:\n", "broken.py")
    assert broken["symbols"] == []
    assert "line 1" in broken["error"]


def test_build_tree_makes_folders_files_and_symbols():
    files = {
        "src/app.py": "class App:\n    def run(self):\n        pass\n",
        "src/utils/helpers.py": "def add(a, b):\n    return a + b\n",
        "README.md": "# Hi\n",
    }
    root = build_tree(files, root_name="my-repo")

    assert root["name"] == "my-repo"
    # Folders come before files
    assert [c["name"] for c in root["children"]] == ["src", "README.md"]

    src = root["children"][0]
    assert [c["name"] for c in src["children"]] == ["utils", "app.py"]

    app_file = src["children"][1]
    assert app_file["type"] == "file"
    assert app_file["language"] == "python"

    app_class = app_file["children"][0]
    assert app_class["type"] == "class"
    assert app_class["path"] == "src/app.py"
    assert app_class["children"][0]["name"] == "run"
    assert (app_class["line_start"], app_class["line_end"]) == (1, 3)

    helpers = src["children"][0]["children"][0]
    assert helpers["path"] == "src/utils/helpers.py"
    assert helpers["children"][0]["name"] == "add"


def test_build_tree_ids_are_unique():
    files = {"a.py": "def f():\n    pass\n\ndef f():\n    pass\n"}
    root = build_tree(files, root_name="x")

    ids = []

    def collect(node):
        ids.append(node["id"])
        for child in node["children"]:
            collect(child)

    collect(root)
    assert len(ids) == len(set(ids))
