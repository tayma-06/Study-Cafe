import argparse
from getpass import getpass
from psycopg.rows import dict_row
from database import get_connection
from schemas import UserCreate
from models import insert_user

# Create the first admin account from the server terminal.
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
