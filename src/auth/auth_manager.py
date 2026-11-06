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

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from pathlib import Path

from src.database.connection import get_connection, is_postgres

try:
    import psycopg
    INTEGRITY_ERRORS = (sqlite3.IntegrityError, psycopg.IntegrityError)
except ImportError:
    INTEGRITY_ERRORS = (sqlite3.IntegrityError,)

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None


_PASSWORD_HASHER = PasswordHasher()


# ============================================================
# DATABASE CONNECTION
# ============================================================

class _AuthCursor:
    """Translate authentication SQL placeholders for PostgreSQL."""

    def __init__(self, cursor, postgres):
        self._cursor = cursor
        self._postgres = postgres

    def execute(self, sql, parameters=None):
        if self._postgres:
            sql = sql.replace("?", "%s")
        if parameters is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, parameters)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class _AuthConnection:
    """Expose a small compatible connection interface to authentication."""

    def __init__(self, connection, postgres):
        self._connection = connection
        self._postgres = postgres

    def cursor(self):
        return _AuthCursor(self._connection.cursor(), self._postgres)

    def __getattr__(self, name):
        return getattr(self._connection, name)


def get_auth_connection():
    """Connect to Neon PostgreSQL or the local SQLite database."""
    return _AuthConnection(get_connection(), is_postgres())


# ============================================================
# CREATE AUTHENTICATION TABLE
# ============================================================

def create_auth_table():
    """
    Create the user_credentials table if it does not exist.
    """

    # PostgreSQL credentials were created during migration.
    # Never attempt SQLite-specific AUTOINCREMENT DDL against Neon.
    if is_postgres():
        return

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
    Hash a new password with Argon2id.

    The optional salt argument is retained for compatibility with
    existing callers. Argon2 manages its own salt internally.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    encoded_hash = _PASSWORD_HASHER.hash(password)
    return encoded_hash, "argon2id"


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(password, stored_hash, stored_salt):
    """Verify Argon2id hashes and legacy salted SHA-256 hashes."""
    if not isinstance(password, str) or not isinstance(stored_hash, str):
        return False

    if stored_hash.startswith("$argon2"):
        try:
            return _PASSWORD_HASHER.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    # Legacy SHA-256 verification for existing accounts.
    if not isinstance(stored_salt, str) or not stored_salt:
        return False

    legacy_hash = hashlib.sha256(
        (stored_salt + password).encode("utf-8")
    ).hexdigest()

    return secrets.compare_digest(legacy_hash, stored_hash)


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

    except INTEGRITY_ERRORS as error:
        connection.rollback()
        return False, f"Could not create credentials: {error}"

    finally:
        connection.close()


# ============================================================
# SELF-SERVICE PASSWORD CHANGE
# ============================================================

def change_user_password(user_id, current_password, new_password):
    """
    Change the password belonging to the specified authenticated user.

    The current password must be verified before the stored password
    can be replaced. New passwords are stored using Argon2id.
    """
    if not user_id:
        return False, "A valid user account is required."

    if not isinstance(current_password, str) or not current_password:
        return False, "Enter your current password."

    if not isinstance(new_password, str) or len(new_password) < 8:
        return False, "The new password must contain at least 8 characters."

    if len(new_password) > 1024:
        return False, "The new password is too long."

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT credential_id, password_hash, password_salt, is_active
            FROM user_credentials
            WHERE user_id = ?
            """,
            (user_id,),
        )

        credential = cursor.fetchone()

        if credential is None or not credential["is_active"]:
            return False, "Active login credentials were not found."

        if not verify_password(
            current_password,
            credential["password_hash"],
            credential["password_salt"],
        ):
            return False, "The current password is incorrect."

        if verify_password(
            new_password,
            credential["password_hash"],
            credential["password_salt"],
        ):
            return False, "Choose a password different from your current password."

        new_hash, new_salt = hash_password(new_password)

        cursor.execute(
            """
            UPDATE user_credentials
            SET password_hash = ?, password_salt = ?
            WHERE credential_id = ? AND user_id = ?
            """,
            (
                new_hash,
                new_salt,
                credential["credential_id"],
                user_id,
            ),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            return False, "The password could not be updated. Please try again."

        connection.commit()
        return True, "Your password has been changed successfully."

    except Exception:
        connection.rollback()
        return False, "The password could not be changed. Please try again."

    finally:
        connection.close()


# ============================================================
# ============================================================
# ADMINISTRATOR FARMER PASSWORD RESET
# ============================================================

def admin_reset_farmer_password(user_id, new_password):
    """
    Allow administrators to reset an existing farmer's password.
    Uses Argon2id and the configured database connection.
    """

    if st is None or not has_role("ADMIN"):
        return False, "Administrator access is required."

    if not isinstance(new_password, str) or not 8 <= len(new_password) <= 1024:
        return False, "Password must contain between 8 and 1024 characters."

    connection = get_auth_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT c.credential_id
            FROM user_credentials c
            INNER JOIN users u ON u.user_id = c.user_id
            WHERE c.user_id = ?
              AND UPPER(u.user_type) = 'FARMER'
            """,
            (user_id,),
        )

        credential = cursor.fetchone()

        if credential is None:
            return False, "No existing Farmer login credentials were found."

        new_hash, new_salt = hash_password(new_password)

        cursor.execute(
            """
            UPDATE user_credentials
            SET password_hash = ?, password_salt = ?
            WHERE credential_id = ? AND user_id = ?
            """,
            (
                new_hash,
                new_salt,
                credential["credential_id"],
                user_id,
            ),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            return False, "The password could not be updated."

        connection.commit()
        return True, "Farmer password reset successfully."

    except Exception:
        connection.rollback()
        return False, "Password reset failed. Please check the application logs."

    finally:
        connection.close()


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

        # Upgrade legacy SHA-256 hashes after successful authentication.
        # Existing Argon2id hashes are left unchanged.
        stored_hash = user["password_hash"]

        if isinstance(stored_hash, str) and not stored_hash.startswith("$argon2"):
            try:
                upgraded_hash, upgraded_salt = hash_password(password)

                cursor.execute(
                    """
                    UPDATE user_credentials
                    SET password_hash = ?, password_salt = ?
                    WHERE credential_id = ?
                    """,
                    (
                        upgraded_hash,
                        upgraded_salt,
                        user["credential_id"],
                    ),
                )
                connection.commit()

            except Exception:
                # Do not lock out a valid user if hash migration fails.
                # Roll back the failed migration before returning the user.
                try:
                    connection.rollback()
                except Exception:
                    pass

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
