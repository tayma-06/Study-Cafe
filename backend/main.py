from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Study Café API is running"}