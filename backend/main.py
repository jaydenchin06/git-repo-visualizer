import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from backend.ai import explain_code
from backend.github import GitHubError, fetch_repo_files
from backend.parser import read_file, get_detailed_structure
from backend.tree import build_tree

# Load settings like GITHUB_TOKEN from backend/.env (if it exists)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()


class CodeInput(BaseModel):
    code: str


class PastedCodeInput(BaseModel):
    code: str
    filename: str = "pasted_code.py"


class RepoInput(BaseModel):
    url: str


class ExplainInput(BaseModel):
    code: str
    name: str
    type: str
    language: Optional[str] = None


@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/test")
def test():
    return {"testingggggg"}

@app.get("/analyze")
def analyze():
    try:
        # Read the test sample file
        file_content = read_file("backend/test_sample.py")
        
        # Parse the file to extract functions and classes
        parsed_data = get_detailed_structure(file_content)
        
        return {
            "status": "success",
            "file": "test_sample.py",
            "content": file_content,
            "length": len(file_content),
            "parsed": {
                "functions": parsed_data["functions"],
                "classes": parsed_data["classes"],
                "total_functions": len(parsed_data["functions"]),
                "total_classes": len(parsed_data["classes"])
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/parse")
def parse_code(code_input: CodeInput):
    try:
        # Get the code from the request
        code = code_input.code
        
        # Parse the code to extract functions and classes
        parsed_data = get_detailed_structure(code)
        
        return {
            "status": "success",
            "parsed": parsed_data,
            "code_length": len(code)
        }
    except SyntaxError as e:
        return {
            "status": "error",
            "message": f"Invalid Python syntax: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---- Endpoints used by the frontend (the Vite dev server forwards /api here) ----

@app.post("/api/analyze/code")
def analyze_pasted_code(code_input: PastedCodeInput):
    """Builds the tree for a single piece of pasted code."""
    # Only keep the file name, in case someone types a path
    filename = os.path.basename(code_input.filename.replace("\\", "/")) or "pasted_code.py"
    code = code_input.code.replace("\r\n", "\n")
    files = {filename: code}
    return {
        "status": "success",
        "tree": build_tree(files, root_name="Pasted code"),
        "files": files,
        "skipped": 0,
    }


@app.post("/api/analyze/repo")
def analyze_repo(repo_input: RepoInput):
    """Downloads a public GitHub repo and builds its tree."""
    try:
        repo = fetch_repo_files(repo_input.url)
    except GitHubError as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "success",
        "tree": build_tree(repo["files"], root_name=repo["name"]),
        "files": repo["files"],
        "skipped": repo["skipped"],
    }


@app.post("/api/explain")
def explain(explain_input: ExplainInput):
    """Asks the AI to explain a piece of code."""
    try:
        explanation = explain_code(
            explain_input.code, explain_input.name, explain_input.type, explain_input.language
        )
        return {"status": "success", "explanation": explanation}
    except Exception as e:
        return {"status": "error", "message": str(e)}
