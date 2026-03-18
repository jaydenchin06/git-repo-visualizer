from fastapi import FastAPI
from parser import read_file

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
        file_content = read_file("test_sample.py")
        return {
            "status": "success",
            "file": "test_sample.py",
            "content": file_content,
            "length": len(file_content)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }