from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/test")
def test():
    return {"testingggggg"}

@app.get("/analyze")
def analyze():
    return {"analyzzingggg"} 
