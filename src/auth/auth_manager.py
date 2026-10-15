"""
AGRO LIFE-AI
Authentication Manager

Handles:
- User credentials
- Password hashing
- Login verification
- User role retrieval
- Account activation/deactivation
"""

import hashlib
import secrets
import os
import sqlite3
from pathlib import Path

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None


# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = Path(os.environ.get("AGRO_LIFE_AI_DB_PATH", str(PROJECT_ROOT / "database" / "agro_life_ai.db")))


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_auth_connection():
    """
    Create a database connection for authentication operations.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# CREATE AUTHENTICATION TABLE
# ============================================================

def create_auth_table():
    """
    Create the user_credentials table if it does not exist.
    """

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_credentials (
                credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password, salt=None):
    """
    Hash a password using SHA-256 with a random salt.

    Returns:
        tuple: (password_hash, salt)
    """

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.sha256(
        (salt + password).encode("utf-8")
    ).hexdigest()

    return password_hash, salt


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(password, stored_hash, stored_salt):
    """
    Verify a password against its stored hash and salt.
    """

    password_hash, _ = hash_password(
        password,
        stored_salt
    )

    return secrets.compare_digest(
        password_hash,
        stored_hash
    )


# ============================================================
# CREATE USER CREDENTIALS
# ============================================================

def create_user_credentials(
    user_id,
    username,
    password
):
    """
    Create login credentials for an existing user.
    """

    create_auth_table()

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        username = username.strip().lower()

        # Check whether credentials already exist
        cursor.execute(
            """
            SELECT credential_id
            FROM user_credentials
            WHERE user_id = ?
               OR username = ?
            """,
            (user_id, username)
        )

        existing = cursor.fetchone()

        if existing:
            return False, "Credentials already exist."

        password_hash, password_salt = hash_password(password)

        cursor.execute(
            """
            INSERT INTO user_credentials (
                user_id,
                username,
                password_hash,
                password_salt,
                is_active
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                user_id,
                username,
                password_hash,
                password_salt
            )
        )

        connection.commit()

        return True, "Credentials created successfully."

    except sqlite3.IntegrityError as error:
        connection.rollback()
        return False, f"Could not create credentials: {error}"

    finally:
        connection.close()


# ============================================================
# LOGIN VERIFICATION
# ============================================================

def authenticate_user(username, password):
    """
    Authenticate a user using username and password.

    Returns:
        dictionary containing user information
        or None when authentication fails.
    """

    create_auth_table()

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        username = username.strip().lower()

        cursor.execute(
            """
            SELECT
                c.credential_id,
                c.user_id,
                c.username,
                c.password_hash,
                c.password_salt,
                c.is_active,

                u.full_name,
                u.user_type,
                u.phone,
                u.email

            FROM user_credentials c

            INNER JOIN users u
                ON c.user_id = u.user_id

            WHERE c.username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        if not user["is_active"]:
            return None

        if not verify_password(
            password,
            user["password_hash"],
            user["password_salt"]
        ):
            return None

        return {
            "credential_id": user["credential_id"],
            "user_id": user["user_id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "user_type": user["user_type"],
            "phone": user["phone"],
            "email": user["email"],
        }

    finally:
        connection.close()


# ============================================================
# GET USER ROLE
# ============================================================

def get_user_role(user_id):
    """
    Get the role of a user.
    """

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_type
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        return user["user_type"]

    finally:
        connection.close()


# ============================================================
# GET USER BY USERNAME
# ============================================================

def get_user_by_username(username):
    """
    Retrieve authenticated user information by username.
    """

    create_auth_table()

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        username = username.strip().lower()

        cursor.execute(
            """
            SELECT
                c.credential_id,
                c.user_id,
                c.username,
                c.is_active,
                u.full_name,
                u.user_type,
                u.phone,
                u.email

            FROM user_credentials c

            INNER JOIN users u
                ON c.user_id = u.user_id

            WHERE c.username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        return dict(user)

    finally:
        connection.close()


# ============================================================
# ACTIVATE ACCOUNT
# ============================================================

def activate_user(user_id):
    """
    Activate a user's login account.
    """

    create_auth_table()

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE user_credentials
            SET is_active = 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ============================================================
# DEACTIVATE ACCOUNT
# ============================================================

def deactivate_user(user_id):
    """
    Deactivate a user's login account.
    """

    create_auth_table()

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE user_credentials
            SET is_active = 0
            WHERE user_id = ?
            """,
            (user_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ============================================================
# INITIALIZE AUTHENTICATION SYSTEM
# ============================================================

def initialize_authentication():
    """
    Initialize authentication database structures.
    """

    create_auth_table()

    # ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def is_authenticated():
    """
    Check whether a user is currently authenticated.
    """
    return (
        "authenticated" in st.session_state
        and st.session_state.authenticated is True
        and st.session_state.get("user") is not None
    )


def has_role(required_role):
    """
    Check whether the logged-in user has the required role.
    """

    if not is_authenticated():
        return False

    user = st.session_state.get("user")

    if not user:
        return False

    return user.get("user_type", "").upper() == required_role.upper()


def logout_user():
    """
    Clear the current user's authentication session.
    """

    st.session_state.authenticated = False
    st.session_state.user = None
    # ============================================================
# CREATE FARMER LOGIN
# ============================================================

def create_farmer_login(user_id, username, password):
    """
    Create login credentials for an existing farmer user.
    """

    # Make sure authentication table exists
    create_auth_table()

    # Check that the user exists and is actually a farmer
    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id, full_name, user_type
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:
            return False, "User does not exist."

        if user["user_type"].upper() != "FARMER":
            return False, "This user is not registered as a farmer."

    finally:
        connection.close()

    # Create credentials using the existing function
    return create_user_credentials(
        user_id,
        username,
        password
    )
