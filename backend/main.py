from fastapi import FastAPI

app = FastAPI(
    title="Study Café API",
    description="Backend API for Study Café Slot Booking & Management System",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Study Café API is running"}