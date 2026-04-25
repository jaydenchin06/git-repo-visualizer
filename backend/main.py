from fastapi import FastAPI
from pydantic import BaseModel
from backend.parser import read_file, get_detailed_structure

app = FastAPI()


class CodeInput(BaseModel):
    code: str


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