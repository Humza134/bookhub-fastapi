from fastapi.security import HTTPBearer
from fastapi import Request, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from utils import decode_token
from database.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from database.connection import get_session
from typing import Annotated
from services.user_service import UserService
from models.user_model import User

user_service = UserService()

class TokenBearer(HTTPBearer):
    """
    Custom HTTPBearer class for handling access tokens.
    """
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)
        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid access token",
            )

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This token is invalid or has expired",
            )
        
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or has been revoked",
                    "resolution": "Please get new token"
                }
            )
        
        self.verify_token_data(token_data)
        

        return token_data
    
    def token_valid(self, token: str) -> bool:
        """
        Validate the access token.
        Args:
            token (str): The access token to validate.
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        token_data = decode_token(token)
        return token_data is not None 
    
    def verify_token_data(self, token_data: dict):
        raise NotImplementedError(
            "Please override the verify_token_data method in the subclass"
        )
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an an access token",
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token",
            )
        
async def get_current_user(
    token_details: Annotated[dict, Depends(AccessTokenBearer())],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Dependency to get the current user from the access token.
    Args:
        token_details (dict): The decoded access token details.
    Returns:
        dict: The user details.
    """
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
    
class RoleChecker:
    """
    Dependency to check if the user has the required role.
    Args:
        required_role (str): The required role for the endpoint.
    Returns:
        bool: True if the user has the required role, False otherwise.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return True
    

# from fastapi import Request, Depends, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.exceptions import HTTPException
# from typing import Annotated

# from sqlmodel.ext.asyncio.session import AsyncSession

# from database.connection import get_session
# from database.redis import token_in_blocklist
# from models.user_model import User
# from services.user_service import UserService
# from utils import decode_token

# import logging

# logger = logging.getLogger(__name__)
# user_service = UserService()


# class TokenBearer(HTTPBearer):
#     """
#     Abstract base class for handling Bearer token authentication.
#     Subclasses must implement `verify_token_data()` to validate token type.
#     """
#     def __init__(self, auto_error: bool = True):
#         super().__init__(auto_error=auto_error)

#     async def __call__(self, request: Request) -> dict:
#         credentials: HTTPAuthorizationCredentials = await super().__call__(request)
#         token = credentials.credentials

#         token_data = decode_token(token)
#         if not token_data:
#             logger.warning("Invalid or expired token.")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="This token is invalid or has expired."
#             )

#         if await token_in_blocklist(token_data["jti"]):
#             logger.warning("Revoked token used.")
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail={
#                     "error": "This token has been revoked.",
#                     "resolution": "Please obtain a new token."
#                 }
#             )

#         self.verify_token_data(token_data)
#         return token_data

#     def verify_token_data(self, token_data: dict):
#         """
#         Subclass-specific token type validation.
#         """
#         raise NotImplementedError("Subclasses must implement verify_token_data().")


# class AccessTokenBearer(TokenBearer):
#     """
#     Validates access tokens.
#     """
#     def verify_token_data(self, token_data: dict):
#         if token_data.get("refresh"):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Access token required, not refresh token."
#             )


# class RefreshTokenBearer(TokenBearer):
#     """
#     Validates refresh tokens.
#     """
#     def verify_token_data(self, token_data: dict):
#         if not token_data.get("refresh"):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Refresh token required, not access token."
#             )


# async def get_current_user(
#     token_data: Annotated[dict, Depends(AccessTokenBearer())],
#     session: Annotated[AsyncSession, Depends(get_session)]
# ) -> User:
#     """
#     Dependency to retrieve current authenticated user using access token.

#     Returns:
#         User instance or raises HTTPException.
#     """
#     user_email = token_data.get("user", {}).get("email")
#     if not user_email:
#         raise HTTPException(status_code=400, detail="Email missing from token.")

#     user = await user_service.get_user_by_email(user_email, session)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found."
#         )
#     return user


# class RoleChecker:
#     """
#     Role-based access control dependency.

#     Args:
#         allowed_roles (list[str]): List of roles permitted to access a route.
#     """
#     def __init__(self, allowed_roles: list[str]):
#         self.allowed_roles = allowed_roles

#     def __call__(self, user: Annotated[User, Depends(get_current_user)]) -> bool:
#         if user.role not in self.allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Access denied: insufficient permissions."
#             )
#         return True