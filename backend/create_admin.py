import argparse
import os
from getpass import getpass
from psycopg.rows import dict_row
from psycopg import connect
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

def get_connection():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL not set')
    return connect(url, connect_timeout=10, options='-c timezone=UTC')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def insert_user(cur, data: UserCreate, role: str):
    cur.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s) RETURNING user_id, name, email, role, created_at",
        (data.name, data.email.lower(), hash_password(data.password), role)
    )
    return cur.fetchone()

def main():
    parser = argparse.ArgumentParser(description="Create a Study Café admin account")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    password = getpass("Password: ")
    if password != getpass("Confirm password: "):
        parser.error("Passwords do not match")
    data = UserCreate(name=args.name, email=args.email, password=password)
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        user = insert_user(cur, data, "admin")
    print(f"Admin account created for {user['email']}")

if __name__ == "__main__":
    main()
