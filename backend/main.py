from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from database import get_connection

app = FastAPI(
    title="Study Café API",
    version="1.0.0"
)

# Allow CORS for the frontend application running on http://localhost:5173
# http://localhost:5173 is Vite's default dev server port
# CORS: Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Study Café API is running"}


@app.get("/test-db")
def test_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()

    return {
        "database": result[0],
        "user": result[1]
    }