from fastapi import FastAPI
from backend.parser import read_file, get_top_level_functions, get_top_level_items

app = FastAPI()

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
        parsed_data = get_top_level_items(file_content)
        
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