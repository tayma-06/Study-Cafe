from fastapi import APIRouter, HTTPException

from models import get_all_users, get_user_by_id, create_user
from schemas import UserCreate, UserResponse

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def get_users():
    users = get_all_users()

    return [
        {
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "created_at": user[4],
        }
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "role": user[3],
        "created_at": user[4],
    }


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user_route(user: UserCreate):
    try:
        new_user = create_user(
            user.name,
            user.email,
            user.password,
            user.role
        )

    except Exception as e:
        if "users_email_key" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

        raise HTTPException(
            status_code=500,
            detail="Could not create user"
        )

    return {
        "user_id": new_user[0],
        "name": new_user[1],
        "email": new_user[2],
        "role": new_user[3],
        "created_at": new_user[4],
    }