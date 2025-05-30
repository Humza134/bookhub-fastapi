from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from database.db_config import Config
import uuid
import logging

ACCESS_TOKEN_EXPIRY = 3600

#password hashing

pwd_context = CryptContext(schemes=["bcrypt"])

def generate_pswd_hash(password: str) -> str:
    """
    Generate a hashed password.
    Args:
        password (str): The password to hash.
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_pswd_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a hashed password.
    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to verify against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

#jwt token generation and verification

def create_access_token(user_data: dict, expiry: timedelta | None = None, refresh: bool = False) -> str:
    """
    Create a JWT access token.
    Args:
        user_data (dict): The data to encode in the token.
        expiry (timedelta, optional): The expiration time delta. Defaults to None.
    Returns:
        str: The encoded JWT access token.
    """
    payload = {}

    payload["user"] = user_data
    expire_time = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["exp"] = int(expire_time.timestamp())  # <-- FIX: use Unix timestamp
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
        # headers={"alg": Config.JWT_ALGORITHM, "typ": "JWT"},
    )
    return token

#decode jwt token
def decode_token(token: str) -> dict:
    """
    Decode a JWT token.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded payload.
    """
    try:
        token_data = jwt.decode(
            token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(f"Error decoding token: {e}")
        return None
        
    