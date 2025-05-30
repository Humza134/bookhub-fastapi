import redis.asyncio as redis
from database.db_config import Config

JTI_EXPIRY = 3600

token_blocklist = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=0,
    decode_responses=True,
)

async def add_jti_to_blocklist(jti: str) -> None:
    """
    Add a JWT ID (jti) to the blocklist in Redis.
    Args:
        jti (str): The JWT ID to add to the blocklist.
    """
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

async def token_in_blocklist(jti: str) -> bool:
    """
    Check if a JWT ID (jti) is in the blocklist in Redis.
    Args:
        jti (str): The JWT ID to check.
    Returns:
        bool: True if the jti is blocked, False otherwise.
    """
    value = await token_blocklist.get(jti)
    return value is not None