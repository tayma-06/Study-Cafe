import logging
import os
import psycopg
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth import require_admin
from routes import router
from database import get_connection


# This code sets up a FastAPI application for the Study Café API. 
# It configures CORS middleware to allow requests from specified origins, includes API routes from the `router`, and defines exception handlers for database errors. 
# The root endpoint returns a simple message indicating that the API is running, and the `/test-db` endpoint allows admin users to test the database connection.
app = FastAPI(title='Study Café API', version='1.1.0')
app.add_middleware(CORSMiddleware,
    allow_origins=[s.strip() for s in os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',') if s.strip()],
    allow_credentials=True, allow_methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Authorization', 'Content-Type'])
app.include_router(router)

# Mount the frontend static files
app.mount("/", StaticFiles(directory="backend_static", html=True), name="frontend")

@app.exception_handler(psycopg.Error)
async def database_error(request, exc):
    if isinstance(exc, (psycopg.errors.UniqueViolation, psycopg.errors.ExclusionViolation)):
        return JSONResponse(status_code=409, content={'detail': 'Duplicate record or overlapping booking'})
    if isinstance(exc, (psycopg.errors.CheckViolation, psycopg.errors.ForeignKeyViolation, psycopg.errors.RaiseException)):
        return JSONResponse(status_code=400, content={'detail': 'Invalid data or disallowed operation'})
    logging.getLogger(__name__).error('Database operation failed: %s', type(exc).__name__)
    return JSONResponse(status_code=503, content={'detail': 'Database operation unavailable'})

@app.get('/')
def root():
    return {'message': 'Study Café API is running'}

@app.get('/test-db')
def test_db(current_user: dict = Depends(require_admin)):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT 1')
        cur.fetchone()
    return {'status': 'ok'}
