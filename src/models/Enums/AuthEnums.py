from enum import Enum


class AuthSignal(Enum):
    # register
    REGISTER_SUCCESS = "User registered successfully"
    USERNAME_ALREADY_TAKEN = "Username already taken"

    # known trade-off: reveals that an email is registered (user enumeration).
    # proper fix: always return the same response and notify the owner by email.
    EMAIL_ALREADY_EXISTS = "Email already registered"

    # login
    LOGIN_SUCCESS = "Login successful"
    INVALID_CREDENTIALS = "Invalid email or password"

    # protected endpoints (dependencies.py)
    NOT_AUTHENTICATED = "Not authenticated"
    TOKEN_INVALID_OR_EXPIRED = "Invalid or expired token" 