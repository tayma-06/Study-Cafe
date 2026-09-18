from fastapi import FastAPI
from routes import router
from database import get_connection

app = FastAPI(
    title="Study Café API",
    version="1.0.0"
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