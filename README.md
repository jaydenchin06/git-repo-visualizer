# Git Repo Visualizer

Paste some code or a GitHub repo link and see it as a tree of **folders → files → classes → functions/methods**. Click anything to view its code, then ask AI to explain it.

## Features

- Load any **public GitHub repo** by link (`https://github.com/owner/repo`, or `.../tree/branch-name` for a branch)
- Or **paste code** directly
- Tree view with search, so you can find a file, class or function by name
- Code view with syntax highlighting and the real line numbers from the file
- "Explain with AI" button for any file, class or function (the AI provider isn't connected yet, see below)
- Python files are parsed into classes, methods and functions (including nested ones). Other files show up in the tree so you can still read them

## Running it

You need **Python 3.10+** and **Node.js 18+**. Run each part in its own terminal.

**1. Backend** (from the repo root):

```bash
python -m venv .venv
.venv\Scripts\activate          # on Mac/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

This starts the API at http://127.0.0.1:8000.

**2. Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173. The frontend sends `/api` requests to the backend for you.

**Tests** (from the repo root):

```bash
python -m pytest backend
```

## How it works

```
backend/
  main.py      FastAPI app and endpoints
  github.py    downloads a public repo as a zip and pulls out the text files
  parser.py    turns code into classes/functions/methods (Python uses the built-in ast module)
  tree.py      combines the files and parsed symbols into one folder tree
  ai.py        builds the "explain this code" request (placeholder for now)
frontend/src/
  App.jsx                   page layout and state
  api.js                    calls to the backend
  components/InputPanel.jsx the repo link / paste code input
  components/TreeView.jsx   the clickable tree
  components/DetailsPanel.jsx  info, code and AI explanation for the selected item
  components/CodeView.jsx   code with syntax highlighting and line numbers
```

| Endpoint | What it does |
| --- | --- |
| `POST /api/analyze/repo` `{ url }` | Downloads a GitHub repo and returns `{ tree, files, skipped }` |
| `POST /api/analyze/code` `{ code, filename }` | Same thing for pasted code |
| `POST /api/explain` `{ code, name, type, language }` | Returns `{ explanation }` |

Each tree node has an `id`, `name`, `type` (`folder`, `file`, `class`, `function` or `method`) and `children`. Classes, functions and methods also have `path`, `line_start` and `line_end`, and the frontend uses those to cut their code out of `files[path]`.

## Adding another language

1. In `backend/parser.py`, write a function that takes the code as a string and returns a list of symbols in the same shape as `parse_python`:
   `{ "name", "type", "line_start", "line_end", "children" }`
2. Add it to `PARSERS`, e.g. `".js": ("javascript", parse_javascript)`

[tree-sitter](https://tree-sitter.github.io/tree-sitter/) is a good option for parsing many languages.

## Connecting an AI provider

All of it happens in `explain_code()` in `backend/ai.py`. Send `build_prompt(...)` to the AI's API and return the text of its reply. Put the API key in `backend/.env` (it's gitignored) and read it with `os.getenv`, never in the code.

## Limits

- Only public repos. Without a token, GitHub allows 60 downloads an hour. Put `GITHUB_TOKEN=...` in `backend/.env` to raise that to 5000.
- Repos over 50 MB, files over 500 KB, binary files and folders like `node_modules` are skipped.
