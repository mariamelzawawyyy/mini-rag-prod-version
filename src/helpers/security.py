from datetime import UTC, datetime, timedelta
import jwt
from pwdlib import PasswordHash
from .config import get_settings 
 
 
password_hash = PasswordHash.recommended()
# using Argon2 that i used in requirements.txt
 
#hash passowrd that will be stored in the db  
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# verify the password written from the user in login with the stored hashed password 
# in the db 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# create token for the user after logging in , it takes the user id from the db
# and creates a token using it and the secret key and the algorithm   
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt


# this is done in the step of getting the current user if the logged in user
#wants to access any endpoint 
def verify_access_token(token: str) -> str | None:
    # verify the jwt and return the subject (user id) if valid
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")  
