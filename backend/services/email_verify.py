import random
import logging
from datetime import datetime, timedelta
from database import get_database

logger = logging.getLogger(__name__)

CODE_EXPIRY_MINUTES = 10


def generate_code() -> str:
    return str(random.randint(100000, 999999))


async def create_verification_code(email: str) -> str:
    db = get_database()
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)

    await db.email_verifications.update_one(
        {"email": email.lower()},
        {"$set": {"code": code, "expires_at": expires_at, "verified": False}},
        upsert=True
    )
    return code


async def check_verification_code(email: str, code: str) -> bool:
    db = get_database()
    record = await db.email_verifications.find_one({"email": email.lower()})
    if not record:
        return False
    if record.get("verified"):
        return True
    if datetime.utcnow() > record.get("expires_at", datetime.utcnow()):
        return False
    if record.get("code") != code.strip():
        return False
    await db.email_verifications.update_one(
        {"email": email.lower()},
        {"$set": {"verified": True}}
    )
    return True


async def is_email_verified(email: str) -> bool:
    db = get_database()
    record = await db.email_verifications.find_one({"email": email.lower()})
    if not record:
        return False
    if not record.get("verified"):
        return False
    if datetime.utcnow() > record.get("expires_at", datetime.utcnow()) + timedelta(hours=1):
        return False
    return True
