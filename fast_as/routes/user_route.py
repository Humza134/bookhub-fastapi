from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import timedelta, datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from models.user_model import User, UserCreate, UserRead, UserLogin, UserReadWithBooksAndReviews
from database.connection import get_session
from services.user_service import UserService
from utils import verify_pswd_hash, create_access_token
from dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from database.redis import add_jti_to_blocklist

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])

@auth_router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Create a new user account
    Args:
        user_data (UserCreate): The data for the new user.
        session (AsyncSession): The database session.
    Returns:
        User: The created user object.
    """
    email = user_data.email
    exist_user = await user_service.user_exists(email, session)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User with this email already exists",
        )

    new_user = await user_service.create_user(user_data, session)
    return new_user
    

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLogin, session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Log in a user
    Args:
        user_data (LoginUser): The data for the user to log in.
        session (AsyncSession): The database session.
    Returns:
        User: The logged-in user object.
    """
    email = user_data.email
    # Check if the user exists
    exist_user = await user_service.user_exists(email, session)
    
    if exist_user is not None:
        # Verify the password
        password_valid = verify_pswd_hash(user_data.password, exist_user.password_hashed)
        if password_valid:
            access_token = create_access_token(
                user_data={"email": exist_user.email, 
                "uid": str(exist_user.uid), "role": exist_user.role},
            )

            refrest_token = create_access_token(
                user_data={"email": exist_user.email, "uid": str(exist_user.uid)},
                refresh=True,
                expiry=timedelta(days=7),
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refrest_token,
                    "user": {"email": exist_user.email, "uid": str(exist_user.uid)},
                }
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )

@auth_router.get("/refresh_token")
async def get_new_access_token(token_detials: Annotated[dict, Depends(RefreshTokenBearer())]):
    """
    Get a new access token using the refresh token
    Args:
        token_detials (dict): The details of the refresh token.
    Returns:
        JSONResponse: The new access token.
    """
    expiry_timestamp = token_detials["exp"]
    print(f"\n\n TOKEN DETAILS:\n\n {token_detials}\n")
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_detials["user"])

        return JSONResponse(
            content={"message": "New access token generated", "access_token": new_access_token}
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired refresh token",
    )

# @auth_router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
# async def get_current_user_details(
#     current_user: Annotated[User, Depends(get_current_user)], _:bool = Depends(role_checker)
# ):
#     """
#     Get the details of the currently logged-in user
#     Args:
#         current_user (User): The current user object.
#     Returns:
#         User: The current user object.
#     """
#     return current_user

@auth_router.get("/me", response_model=UserReadWithBooksAndReviews, status_code=status.HTTP_200_OK)
async def get_current_user_details(
    current_user: Annotated[User, Depends(get_current_user)],
    _: bool = Depends(role_checker),
    session: AsyncSession = Depends(get_session),
):
    """
    Get the details of the currently logged-in user, including their books and reviews.
    """
    result = await session.exec(
        select(User)
        .where(User.uid == current_user.uid)
        .options(
            selectinload(User.books),
            selectinload(User.reviews)
        )
    )
    user = result.first()
    return user

@auth_router.post("/logout")
async def logout_user(token_detials: Annotated[dict, Depends(AccessTokenBearer())]):
    """
    Log out a user
    Args:
        token_detials (dict): The details of the access token.
    Returns:
        JSONResponse: The logout response.
    """

    jti = token_detials["jti"]

    await add_jti_to_blocklist(jti)
    return JSONResponse(content={"message": "Logout successful"}, status_code=status.HTTP_200_OK)

