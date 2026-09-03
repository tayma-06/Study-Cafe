# Study Café — Setup Guide

## Requirements

Make sure you have installed:

* Git
* Python
* Node.js
* npm

Check the installations:

```bash
git --version
python --version
node --version
npm --version
```

## Clone the Repository

```bash
git clone <repository-url>
cd Study-Cafe
```

## Backend Setup

Go to the backend directory:

```bash
cd backend
```

Install the required packages:

```bash
python -m pip install fastapi uvicorn
```

Run the backend:

```bash
python -m uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another terminal and go to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will run at:

```text
http://localhost:5173
```

## Project Structure

```text
Study-Cafe/
├── backend/
│   └── main.py
│
├── database/
│   └── schema.sql
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       │
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── SeatCard.jsx
│       │   └── BookingCard.jsx
│       │
│       └── pages/
│           ├── Login.jsx
│           ├── Home.jsx
│           ├── Booking.jsx
│           ├── MyBookings.jsx
│           └── Admin.jsx
│
└── .gitignore
```

## Running the Project

The backend and frontend should run in separate terminals.

### Terminal 1 — Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```
