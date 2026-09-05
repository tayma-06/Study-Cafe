from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="Study Café API",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Study Café API is running"}