# Study Café — Setup Guide

## Requirements

Make sure you have installed:

* Git
* Python 3.10+
* Node.js 18+
* npm
* PostgreSQL 14+

Check the installations:

```bash
git --version
python --version
node --version
npm --version
psql --version
```

## Clone the Repository

```bash
git clone <repository-url>
cd Study-Cafe
```

## Backend Setup

### 1. Create a Virtual Environment

From the project root:

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` (project root) and fill in your values:

```bash
cp .env.example .env
```

Required variables:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=study_cafe
DB_USER=your_database_user
DB_PASSWORD=your_database_password
JWT_SECRET_KEY=change-this-to-a-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
# Work email domains allowed for receptionist accounts.
STAFF_EMAIL_DOMAINS=studycafe.example
# Optional: comma-separated list of allowed frontend origins
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> **Note:** The backend reads `.env` from the project root. Make sure you run the backend from the `backend` directory (see step 6).

### 5. Database Setup

Create the PostgreSQL database and execute the SQL files in the appropriate order:

```bash
# Create the database
createdb study_cafe
# Or from psql: CREATE DATABASE study_cafe;
```

Then run the SQL scripts in order:

```bash
psql -d study_cafe -f database/schema.sql
psql -d study_cafe -f database/functions.sql
psql -d study_cafe -f database/triggers.sql
psql -d study_cafe -f database/procedures.sql
psql -d study_cafe -f database/views.sql
psql -d study_cafe -f database/seed.sql
```

The database uses PostgreSQL features including:
* `TSTZRANGE` and range operators
* GiST indexing and exclusion constraints
* Functions, stored procedures, triggers, and views
* Custom domains and composite types

### 6. Create the First Admin Account (Optional)

If the database has no admin yet, run from the `backend` directory:

```bash
cd backend
python create_admin.py --name "Admin" --email admin@example.com
```

You'll be prompted to enter a password.

### 7. Start the FastAPI Server

From the `backend` directory:

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at:
```
http://127.0.0.1:8000
```

Interactive API documentation (Swagger UI):
```
http://127.0.0.1:8000/docs
```

OpenAPI specification:
```
http://127.0.0.1:8000/openapi.json
```

## Frontend Setup

### 1. Configure Environment Variables (Optional)

The frontend uses Vite. Copy the example environment file:

```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env` if needed:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 2. Install Dependencies

Open another terminal and go to the frontend directory:

```bash
cd frontend
npm install
```

### 3. Start the Development Server

```bash
npm run dev
```

The frontend will run at:
```
http://localhost:5173
```

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Running the Project

The backend and frontend should run in separate terminals.

### Terminal 1 — Backend

```bash
cd Study-Cafe
# Activate virtual environment (see step 2 above)
cd backend
uvicorn main:app --reload
```

### Terminal 2 — Frontend

```bash
cd Study-Cafe/frontend
npm run dev
```

Then open:
```
http://localhost:5173
```

## Project Structure

```
Study-Cafe/
│
├── backend/
│   ├── auth.py           # JWT authentication
│   ├── database.py       # Database connection pool
│   ├── models.py         # Pydantic models
│   ├── schemas.py        # Request/response schemas
│   ├── routes.py         # API routes
│   ├── main.py           # FastAPI app entry point
│   └── create_admin.py   # Admin creation script
│
├── database/
│   ├── schema.sql        # Tables, types, domains
│   ├── functions.sql     # Database functions
│   ├── triggers.sql      # Database triggers
│   ├── procedures.sql    # Stored procedures
│   ├── views.sql         # Database views
│   └── seed.sql          # Initial data
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── dist/             # Production build output
│   ├── src/
│   │   ├── main.jsx      # App entry point
│   │   ├── App.jsx       # Root component
│   │   ├── index.css     # Global styles
│   │   ├── services/
│   │   │   └── api.js    # API client
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── styles/       # Component-specific styles
│   │   └── utils/        # Utility functions
│   │       └── customer.js
│   │
│   └── tests/            # End-to-end test scripts
│       ├── customer-flow.mjs
│       └── staff-flow.mjs
│
├── docs/
│   └── SETUP.md          # This file
│
├── .env.example          # Backend environment template
├── .env                  # Backend environment (gitignored)
├── requirements.txt      # Python dependencies
└── README.md             # Project overview
```

## Troubleshooting

### Database Connection Issues

* Ensure PostgreSQL is running and accessible on the configured host/port
* Verify the database user has permissions to create tables and functions
* Check that `DB_PORT` matches your PostgreSQL installation (default 5432, not 5433)

### CORS Errors

* Add your frontend origin to `CORS_ORIGINS` in `.env`
* Default allowed origin is `http://localhost:5173`

### Port Conflicts

* Backend default: 8000
* Frontend default: 5173
* Change ports in `uvicorn` command or `vite.config.js` if needed

### Virtual Environment Not Activated

* Ensure the virtual environment is activated in each terminal session
* Run `which python` or `where python` to verify the correct interpreter

## Render Deployment

### Quick Deploy (using render.yaml)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New** → **Blueprint**
4. Connect your GitHub repository
5. Render will detect `render.yaml` and create:
   - PostgreSQL database (`study-cafe-db`)
   - Backend web service (`study-cafe-backend`)
   - Frontend web service (`study-cafe-frontend`)
   - Database initialization job (`study-cafe-db-init`)

### Manual Setup

If you prefer manual configuration:

#### 1. Create PostgreSQL Database

1. In Render Dashboard, click **New** → **PostgreSQL**
2. Name: `study-cafe-db`
3. Database: `study_cafe`
4. User: `study_cafe_user`
5. Plan: Free (or paid)
6. Copy the **Internal Database URL** (looks like `postgresql://user:pass@host:port/db`)

#### 2. Deploy Backend

1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Name**: `study-cafe-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend` (if repo root has backend folder)
4. Environment Variables:
   ```
   DATABASE_URL=<paste Internal Database URL from step 1>
   JWT_SECRET_KEY=<generate a long random string>
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=1440
   STAFF_EMAIL_DOMAINS=studycafe.example
   CORS_ORIGINS=https://study-cafe-frontend.onrender.com
   ```

#### 3. Initialize Database Schema

After backend deploys, run the database initialization:

1. In Render Dashboard, go to your backend service
2. Click **Shell** tab
3. Run: `python init_db.py`

Or create a one-off job:
1. **New** → **Job** → **Background Worker**
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `python init_db.py`
4. Add `DATABASE_URL` environment variable (same as backend)

#### 4. Deploy Frontend

1. Click **New** → **Static Site** (or Web Service for SPA)
2. Settings:
   - **Name**: `study-cafe-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist` (for Static Site)
   - **Start Command**: `cd frontend && npm start -- -l $PORT` (for Web Service)
3. Environment Variables:
   ```
   VITE_API_BASE_URL=https://study-cafe-backend.onrender.com
   ```

#### 5. Update CORS

After frontend deploys, update the backend's `CORS_ORIGINS` to include your frontend URL:
```
CORS_ORIGINS=https://study-cafe-frontend.onrender.com
```

Then redeploy the backend.

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (provided by Render) | Yes |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens (generate with `openssl rand -hex 32`) | Yes |
| `JWT_ALGORITHM` | JWT algorithm (default: HS256) | No |
| `JWT_EXPIRE_MINUTES` | Token expiry in minutes (default: 1440) | No |
| `STAFF_EMAIL_DOMAINS` | Allowed domains for receptionist work emails | Yes |
| `CORS_ORIGINS` | Comma-separated frontend origins | No (defaults to localhost) |
| `VITE_API_BASE_URL` | Backend API URL for frontend | Yes |

### Common Render Issues

#### Build Fails
- Check build logs for missing dependencies
- Ensure `requirements.txt` has all packages
- Python version: specify in `runtime.txt` if needed (`python-3.11.0`)

#### Database Connection Failed
- Verify `DATABASE_URL` is set correctly
- Use **Internal Database URL** (not external) for services in same region
- Check database is in **Available** state

#### CORS Errors
- Add frontend URL to backend's `CORS_ORIGINS`
- Redeploy backend after changing CORS

#### Frontend Shows Blank Page
- Ensure `VITE_API_BASE_URL` is set correctly
- Check browser console for API errors
- Verify backend `/docs` endpoint works

#### Database Not Initialized
- Run `python init_db.py` in backend shell or as a job
- Check job logs for SQL errors
- Verify all SQL files exist in `database/` folder